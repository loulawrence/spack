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

        os.system('pushd %SPACK_ROOT%')
        subprocess.call('cmake -B %USERPROFILE%/Documents/spack_build/ -DSPACK_VERSION='+spack.spack_version,shell=True)
        subprocess.call('cpack --config %USERPROFILE%/Documents/spack_build/CPackConfig.cmake -B %USERPROFILE%/Documents/spack_build/',shell=True)
        os.system('popd')
        # TODO: optional clean generation
        # os.system('move /y "%USERPROFILE%/Documents/_build_temp/Spack-'+spack.spack_version+'.msi" "%USERPROFILE%/Documents/spack_build/"')
        # os.system('rmdir /s /q %USERPROFILE%/Documents/_build_temp/')
    else:
        print('The generate command is currently only supported on Windows.')