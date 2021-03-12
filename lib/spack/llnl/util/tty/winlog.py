from __future__ import unicode_literals

import atexit
import errno
import multiprocessing
import io
import os
import re
import select
import sys
import ctypes
import traceback
import signal
import tempfile
import subprocess
import threading
import queue
from threading import Thread
from contextlib import contextmanager

from typing import Optional  # novm
from types import ModuleType  # novm

class logwin32_output:
    def __init__(self, file_like=None, echo=False, debug=0, buffer=False, env=None):
        print("I AM IN INIT")
        self.file_like = file_like
        self.echo = echo
        self.debug = debug
        self.buffer = buffer
        self.env = env 
        self._active = False  # used to prevent re-entry
        # this part needed for libc.fflush and that is needed to capture libc output
        if sys.version_info < (3, 5):
            self.libc = ctypes.CDLL(ctypes.util.find_library('c'))
        else:
            if hasattr(sys, 'gettotalrefcount'): # debug build
                self.libc = ctypes.CDLL('ucrtbased')
            else:
                self.libc = ctypes.CDLL('api-ms-win-crt-stdio-l1-1-0')

    def __enter__(self):
        print("I AM IN ENTER")
        if self._active:
            raise RuntimeError("Can't re-enter the same log_output!")
        if self.file_like is None:
            raise RuntimeError(
                "file argument must be set by either __init__ or __call__")
        self.saved_stdout = sys.stdout.fileno()
        self.saved_stderr = sys.stderr.fileno()

        # Save a copy of the original stdout fd in saved_stdout_fd
        self.new_stdout = os.dup(sys.stdout.fileno())
        self.new_stderr = os.dup(sys.stderr.fileno())
        # Create a temporary file and redirect stdout to it
        self.tfile = tempfile.TemporaryFile(mode='w+b')
        self.tfile2 = tempfile.TemporaryFile(mode='w+b')
        self._redirect_stdout(self.tfile.fileno())
        self._redirect_stderr(self.tfile2.fileno())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("I AM IN EXIT")
        self._redirect_stdout(self.saved_stdout)
        self._redirect_stderr(self.saved_stderr)
        # Copy contents of temporary file to the given stream
        self.log_file = open(self.file_like,"wb+")
        self.tfile.flush()
        self.tfile.seek(0, io.SEEK_SET)
        self.log_file.write(self.tfile.read())
        self.tfile2.flush()
        self.tfile2.seek(0, io.SEEK_SET)
        self.log_file.write(self.tfile2.read())
        self.log_file.close()
        self.tfile.close()
        os.close(self.saved_stderr)
        # track whether we're currently inside this log_output
        self._active = True

        # return this log_output object so that the user can do things
        # like temporarily echo some ouptut.
        self._active = False  # safe to enter again
        return self

    def _redirect_stdout(self, to_fd):
        self.libc.fflush(None) 
        sys.stdout.close()
        os.dup2(to_fd, self.saved_stdout)
        sys.stdout = io.TextIOWrapper(os.fdopen(self.saved_stdout, 'wb'))

    def _redirect_stderr(self, to_fd):
        self.libc.fflush(None) 
        sys.stderr.close()
        os.dup2(to_fd, self.saved_stdout)
        sys.stderr = io.TextIOWrapper(os.fdopen(self.saved_stderr, 'wb'))


class winlog:
    def __init__(self, filen, echo=True, debug=0):
        print("I AM IN INIT")
        self.filen=filen
        self.echo = echo
        self.debug=debug
        self._active = False  # used to prevent re-entry

    def __enter__(self):
        print("I AM IN ENTER\n")
        if self._active:
            raise RuntimeError("Can't re-enter the same log_output!")
        if self.filen is None:
            raise RuntimeError(
                "file argument must be set by either __init__ or __call__")
        self.saved_stdout = sys.stdout.fileno()
        self.new_stdout = os.dup(self.saved_stdout)
        self.saved_stderr = sys.stderr.fileno()
        self.new_stderr = os.dup(self.saved_stderr)

        self._kill = threading.Event()
        print('I AM HERE')
        _thread = Thread(target=self.tee_output, args=(self.new_stdout, self.new_stderr))
        _thread.daemon = True
        _thread.start()
        print('NOW HERE')
        self.active = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("I AM EXITING")
        self._kill.set()
        self.active = False

    def _textio_iterlines(self, stream):
        line = stream.readline()
        while line != '':
            yield line
            line = stream.readline()

    def tee_output(self, stdout_fd, stderr_fd):
        #ignore stderr until we figure out how to read a line
        print('I AM IN TEE_OUTPUT')
       
        with open(stdout_fd, 'w+') as stream_out:
            while True:
                print('before readline')
                line = stream_out.readline()
                if self.echo:
                    stream_out.write(line)
                with open(self.filen,"w") as log_file:
                    log_file.write(line)
                is_killed = self._kill.wait(.1)
                if is_killed:
                    break
        
        
f = "build-out.txt"

with winlog(f, True) as logger:
    print("INSIDE LOGGER")
    p = subprocess.run("c:/Program Files/CMake/bin/cmake --version")