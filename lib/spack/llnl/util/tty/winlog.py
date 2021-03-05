""" Tested on Windows 10, 64 bit, Python 3.6

Sources: 
https://eli.thegreenplace.net/2015/redirecting-all-kinds-of-stdout-in-python/
https://stackoverflow.com/questions/17942874/stdout-redirection-with-ctypes
""" 
from contextlib import contextmanager
import ctypes
import io
import os
import re
import sys
import tempfile
import subprocess
import llnl.util.tty as tty
from llnl.util.tty.log import FileWrapper

# this part is needed for libc.fflush and that is needed to caputre libc output
# maynot need that for spack, but I don't think it will hurt
# will want to move this into the constructor of the class
if sys.version_info < (3, 5):
    libc = ctypes.CDLL(ctypes.util.find_library('c'))
else:
    if hasattr(sys, 'gettotalrefcount'): # debug build
        libc = ctypes.CDLL('ucrtbased')
    else:
        libc = ctypes.CDLL('api-ms-win-crt-stdio-l1-1-0')

class logwin32_output(object):
    def __init__(self, file=None, echo=False, debug=0, buffer=False, env=None):
        self.file = file
        self.echo = echo
        self.debug = debug
        self.buffer = buffer
        self.env = env 
        self._active = False  # used to prevent re-entry

    def __call__(self, file=None, echo=None, debug=None, buffer=None):
        if file_like is not None:
            self.file = file
        if echo is not None:
            self.echo = echo
        if debug is not None:
            self.debug = debug
        if buffer is not None:
            self.buffer = buffer
        return self
    def __enter__(self):
        if self._active:
            raise RuntimeError("Can't re-enter the same log_output!")

        if self.file is None:
            raise RuntimeError(
                "file argument must be set by either __init__ or __call__")
    def __exit__(self, exc_type, exc_val, exc_tb):
        tty.color._force_color = self._saved_color
        tty._debug = self._saved_debug

        self._active = False  # safe to enter again
    @contextmanager
    def force_echo(self):
        pass

@contextmanager
def stdout_redirector(stream):
    # The original fd stdout points to. Usually 1 on POSIX systems.
    original_stdout_fd = sys.stdout.fileno()
    original_stderr_fd = sys.stderr.fileno()

    def _redirect_stdout(to_fd):
        """Redirect stdout to the given file descriptor."""
        # Flush the C-level buffer stdout
        libc.fflush(None)   #### CHANGED THIS ARG TO NONE #############
        # Flush and close sys.stdout - also closes the file descriptor (fd)
        sys.stdout.close()
        # Make original_stdout_fd point to the same file as to_fd
        os.dup2(to_fd, original_stdout_fd)
        # Create a new sys.stdout that points to the redirected fd
        sys.stdout = io.TextIOWrapper(os.fdopen(original_stdout_fd, 'wb'))

    def _redirect_stderr(to_fd):
        """Redirect stdout to the given file descriptor."""
        # Flush the C-level buffer stdout
        libc.fflush(None)   #### CHANGED THIS ARG TO NONE #############
        # Flush and close sys.stdout - also closes the file descriptor (fd)
        sys.stderr.close()
        # Make original_stdout_fd point to the same file as to_fd
        os.dup2(to_fd, original_stderr_fd)
        # Create a new sys.stdout that points to the redirected fd
        sys.stderr = io.TextIOWrapper(os.fdopen(original_stderr_fd, 'wb'))

    # Save a copy of the original stdout fd in saved_stdout_fd
    saved_stdout_fd = os.dup(original_stdout_fd)
    saved_stderr_fd = os.dup(original_stderr_fd)
    try:
        # Create a temporary file and redirect stdout to it
        tfile = tempfile.TemporaryFile(mode='w+b')
        tfile2 = tempfile.TemporaryFile(mode='w+b')
        _redirect_stdout(tfile.fileno())
        _redirect_stderr(tfile2.fileno())
        # Yield to caller, then redirect stdout back to the saved fd
        yield
        _redirect_stdout(saved_stdout_fd)
        _redirect_stderr(saved_stderr_fd)
        # Copy contents of temporary file to the given stream
        tfile.flush()
        tfile.seek(0, io.SEEK_SET)
        stream.write(tfile.read())
        tfile2.flush()
        tfile2.seek(0, io.SEEK_SET)
        stream.write(tfile2.read())
    finally:
        tfile.close()
        os.close(saved_stdout_fd)


#### Test it
f = io.BytesIO()

with stdout_redirector(f):
    print('foobar')
    print(12)
    p = subprocess.Popen("c:/Program Files/CMake/bin/cmake --version")
    p.communicate()
    libc.puts(b'this comes from C')
    sys.stderr.write("spam\n")
    os.system('echo and this is from echo')

print('Got stdout: "{0}"'.format(f.getvalue().decode('utf-8')))



