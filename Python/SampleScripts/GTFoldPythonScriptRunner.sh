#!/bin/bash

PYTHON3=`which python3`
READLINK=`which readlink`
if [[ "`uname -s`" == "Darwin" ]]; then
     READLINK=`which greadlink`
fi

source ~/.bash_profile || source ~/.bashrc

GTFPYTHON_INSTALL_PATH="$GTDMMB_HOME/GTFoldPython/Python/PythonLibrarySrc"
GTFPYTHON_INSTALL_LIBS_PATH="$GTDMMB_HOME/GTFoldPython/Python/Lib"

GTFP_SCRIPT_CWD=`pwd`
GTFP_SCRIPT_PATH=`$READLINK -f $GTFP_SCRIPT_CWD/$1`

export PYTHONPATH="$GTFPYTHON_INSTALL_PATH:$GTFP_SCRIPT_PATH"
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$GTFPYTHON_INSTALL_PATH"
export DYLD_LIBRARY_PATH="$DYLD_LIBRARY_PATH:$GTFPYTHON_INSTALL_LIBS_PATH"
export DYLD_FALLBACK_LIBRARY_PATH="/usr/lib:/usr/local/lib:$DYLD_FALLBACK_LIBRARY_PATH"

$PYTHON3 $GTFP_SCRIPT_PATH

exit 0
