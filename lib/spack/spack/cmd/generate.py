import os
import sys
import subprocess
import spack
import spack.paths

def generate(parser, args):
    """
       Use CMake to generate WIX installer in newly created build directory 
    """
    if(sys.platform == 'win32'):
        cwd = os.getcwd()
        os.system('cd %SPACK_ROOT%')
        subprocess.call('cmake -B %USERPROFILE%/Documents/build -DSPACK_VERSION='+spack.spack_version,shell=True)
        subprocess.call('cpack --config %USERPROFILE%/Documents/build/CPackConfig.cmake -B %USERPROFILE%/Documents/build',shell=True)
        os.system('cd '+cwd)
    else:
        print('The generate command is currently only supported on Windows.')