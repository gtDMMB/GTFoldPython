#!/bin/bash

#### InstallSetupBash.sh : Configure the local user's bash init scripts;
#### Author: Maxie D. Schmidt (maxieds@gmail.com)
#### Created: 2020.01.27

SED=$(which sed)
READLINK=$(which readlink)
BASHRC=

PLATFORM=$(uname -s)
if [[ "$PLATFORM" == "Darwin" ]]; then
	SED=$(which gsed)
	READLINK=$(which greadlink)
	BASHRC=$($READLINK -f ~/.bash_profile)
else
	BASHRC=$($READLINK -f ~/.bashrc)
fi

BASHCONFIG_INSTALLED_LOCKFILE="./LocalBashConfigInstalled.lock"

BASHRC_LINES="#### Configure library GTFoldPython:\n"
BASHRC_LINES+="export GTFOLDDATADIR=\"$($READLINK -f "./Testing/ExtraGTFoldThermoData/DefaultGTFold")\"\n"
BASHRC_LINES+="export READLINK=$READLINK\n"
BASHRC_LINES+="if [[ \"\$LD_LIBRARY_PATH\" == \"\" ]]; then\n"
BASHRC_LINES+="     export LD_LIBRARY_PATH=\$($READLINK -f $($READLINK -f ./Lib))\n"
BASHRC_LINES+="else\n"
BASHRC_LINES+="     export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:\$($READLINK -f ./Lib)\n"
BASHRC_LINES+="fi\n"
BASHRC_LINES+="if [[ \"\$DYLD_LIBRARY_PATH\" == \"\" ]]; then\n"
BASHRC_LINES+="     export DYLD_LIBRARY_PATH=\$($READLINK -f $($READLINK -f ./Lib))\n"
BASHRC_LINES+="else\n"
BASHRC_LINES+="     export DYLD_LIBRARY_PATH=\$DYLD_LIBRARY_PATH:\$($READLINK -f ./Lib)\n"
BASHRC_LINES+="fi\n"
BASHRC_LINES+="if [[ \"\$PYTHONPATH\" == \"\" ]]; then\n"
BASHRC_LINES+="     export PYTHONPATH=\$($READLINK -f $($READLINK -f ./PythonLibrarySrc))\n"
BASHRC_LINES+="else\n"
BASHRC_LINES+="     export PYTHONPATH=\$PYTHONPATH:\$($READLINK -f $($READLINK -f ./PythonLibrarySrc))\n"
BASHRC_LINES+="fi\n"
if [[ "$PLATFORM" == "Darwin" ]]; then
	BASHRC_LINES+="export MACOSX_DEPLOYMENT_TARGET=10.14\n"
	#BASHRC_LINES+="export DYLD_PRINT_LIBRARIES=1 && DYLD_PRINT_LIBRARIES_POST_LAUNCH=1 && \
	#		export DYLD_PRINT_APIS=1 && export DYLD_PRINT_STATISTICS=1 && export DYLD_PRINT_INITIALIZERS=1 && \
	#		DYLD_PRINT_SEGMENTS=1 && DYLD_PRINT_BINDINGS=1\n"
	BASHRC_LINES+="alias python3dbg='/usr/local/Cellar/python-dbg\@3.7/3.7.6_13/bin/python3'\n"
	BASHRC_LINES+="alias python3-config='/usr/local/Cellar/python-dbg\@3.7/3.7.6_13/bin/python3-config'\n"
	BASHRC_LINES+="export PYTHONAPPSDIR=/usr/local/Cellar/python-dbg\@3.7/3.7.6_13\n"
fi
#BASHRC_LINES+="export PYTHONFAULTHANDLER='' && PYTHONMALLOC=debug && PYTHONDEVMODE=debug\n"
#BASHRC_LINES+="export PYTHONINSPECT='' && PYTHONVERBOSE=1 && export PYTHONDONTWRITEBYTECODE=1\n"
#BASHRC_LINES+="export PYTHONWARNINGS=always && export PYTHONMALLOCSTATS='' && export PYTHONUTF8=1\n"
#BASHRC_LINES+="export PYTHONTHREADDEBUG=1 && PYTHONDUMPREFS=1 && PYTHONUNBUFFERED=''\n"
#BASHRC_LINES+="export MALLOC_CHECK_=3 && export LD_BIND_NOW=1 && export LD_DEBUG=1\n"
#BASHRC_LINES+="export LD_VERBOSE=1 && export LD_WARN=1\n"
BASHRC_LINES+="\n"

if [[ -f $BASHCONFIG_INSTALLED_LOCKFILE ]]; then
	echo -e "Already appended lines to \"$BASHRC\" (NOT SPAMMING THIS FILE AGAIN!) ... \n\n"
	echo -e $BASHRC_LINES
else
	echo -e "Appending lines to \"$BASHRC\" ... \n\n"
	echo -e $BASHRC_LINES
	echo -e $BASHRC_LINES >> $BASHRC
fi
touch $BASHCONFIG_INSTALLED_LOCKFILE

exit 0
