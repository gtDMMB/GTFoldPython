#!/bin/bash

#### InstallSetupBash.sh : Configure the local user's bash init scripts;
#### Author: Maxie D. Schmidt (maxieds@gmail.com)
#### Created: 2020.01.27

SED=$(which sed)
READLINK=$(which readlink)
BASHRC_CFGFILE=
HOME_PROFILE_PREFIX=

PLATFORM=$(uname -s)
if [[ "$PLATFORM" == "Darwin" ]]; then
	SED=$(which gsed)
	READLINK=$(which greadlink)
	BASHRC_CFGFILE=.bash_profile
else
	BASHRC_CFGFILE=.bashrc
fi

# Fixes the error ssh'ing into some SOM systems where the 
# user does not have a working home directory on the system: 
# -- if $HOME directory does not exist, then we set the bash configuration 
#    settings invoked by this script to get written out to the CWD one directory 
#    above where thee GTFoldPython repository was cloned ...
if [[ -d "$HOME" ]]; then
     HOME_PROFILE_PREFIX=$HOME
else
     HOME_PROFILE_PREFIX=$(READLINK ../..)
fi

BASHRC="$HOME_PROFILE_PREFIX/$BASHRC_CFGFILE"


# One directory higher, outside of GTFoldPython/Python where `make bash-configure` gets run
LOCAL_GTDMMB_HOME=$($READLINK -f ../..)

BASHCONFIG_INSTALLED_LOCKFILE="./LocalBashConfigInstalled.lock"
if [[ -z $NOCLOBBER_BASHRC_SETTINGS ]]; then
     export NOCLOBBER_BASHRC_SETTINGS=0
     NOCLOBBER_BASHRC_SETTINGS=0
fi

DATESTAMP=$(date +"%Y-%m-%d @@ %H:%M:%S")

BASHRC_LINES=
BASHRC_LINES+="\n\n#### -- START OF GTDMMB GTFOLDPYTHON CONFIG OPTIONS [ADDED += $DATESTAMP]\n\n"
BASHRC_LINES+="## Setup the working GTDMMB software directory reference:\n"
BASHRC_LINES+="export GTDMMB_HOME=\"$LOCAL_GTDMMB_HOME\""
BASHRC_LINES+="\n\n## Configure library GTFoldPython:\n"
BASHRC_LINES+="export GTFOLDDATADIR=\"$($READLINK -f "./Testing/ExtraGTFoldThermoData/GTFoldTurner99")\"\n"
BASHRC_LINES+="export READLINK=$READLINK\n"
BASHRC_LINES+="if [[ \"\$LD_LIBRARY_PATH\" == \"\" ]]; then\n"
BASHRC_LINES+="\texport LD_LIBRARY_PATH=\$($READLINK -f $($READLINK -f ./Lib))\n"
BASHRC_LINES+="else\n"
BASHRC_LINES+="\texport LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:\$($READLINK -f ./Lib)\n"
BASHRC_LINES+="fi\n"
BASHRC_LINES+="if [[ \"\$DYLD_LIBRARY_PATH\" == \"\" ]]; then\n"
BASHRC_LINES+="\texport DYLD_LIBRARY_PATH=\$($READLINK -f $($READLINK -f ./Lib))\n"
BASHRC_LINES+="else\n"
BASHRC_LINES+="\texport DYLD_LIBRARY_PATH=\$DYLD_LIBRARY_PATH:\$($READLINK -f ./Lib)\n"
BASHRC_LINES+="fi\n"
BASHRC_LINES+="if [[ \"\$PYTHONPATH\" == \"\" ]]; then\n"
BASHRC_LINES+="\texport PYTHONPATH=\$($READLINK -f $($READLINK -f ./PythonLibrarySrc))\n"
BASHRC_LINES+="else\n"
BASHRC_LINES+="\texport PYTHONPATH=\$PYTHONPATH:\$($READLINK -f $($READLINK -f ./PythonLibrarySrc))\n"
BASHRC_LINES+="fi\n"
# Extra (optional) configuration settings -- NOTE: Uncommenting these lines leads to VERBOSE terminal output!
#BASHRC_LINES+="export PYTHONFAULTHANDLER='' && PYTHONMALLOC=debug && PYTHONDEVMODE=debug\n"
#BASHRC_LINES+="export PYTHONINSPECT='' && PYTHONVERBOSE=1 && export PYTHONDONTWRITEBYTECODE=1\n"
#BASHRC_LINES+="export PYTHONWARNINGS=always && export PYTHONMALLOCSTATS='' && export PYTHONUTF8=1\n"
#BASHRC_LINES+="export PYTHONTHREADDEBUG=1 && PYTHONDUMPREFS=1 && PYTHONUNBUFFERED=''\n"
#BASHRC_LINES+="export MALLOC_CHECK_=3 && export LD_BIND_NOW=1 && export LD_DEBUG=1\n"
#BASHRC_LINES+="export LD_VERBOSE=1 && export LD_WARN=1\n"
if [[ "$PLATFORM" == "Darwin" ]]; then
	BASHRC_LINES+="export MACOSX_DEPLOYMENT_TARGET=10.14\n"
     # Extra (optional) configuration settings -- NOTE: Uncommenting these lines leads to VERBOSE terminal output!
     #BASHRC_LINES+="export DYLD_PRINT_LIBRARIES=1 && DYLD_PRINT_LIBRARIES_POST_LAUNCH=1 && \
	#		export DYLD_PRINT_APIS=1 && export DYLD_PRINT_STATISTICS=1 && export DYLD_PRINT_INITIALIZERS=1 && \
	#		DYLD_PRINT_SEGMENTS=1 && DYLD_PRINT_BINDINGS=1\n"
fi
BASHRC_LINES+="\n#### -- END OF GTDMMB GTFOLDPYTHON SPECIFIC CONFIG SETTINGS --\n\n"


if [[ -f $BASHCONFIG_INSTALLED_LOCKFILE && "$NOCLOBBER_BASHRC_SETTINGS" == "1" ]]; then
	echo -e "Already appended lines to \"$BASHRC\" (NOT SPAMMING THIS FILE AGAIN!) ... \n\n"
	echo -e $BASHRC_LINES
else
     if [[ -f $BASHCONFIG_INSTALLED_LOCKFILE ]]; then
          echo "   APPENDING new config lines to the user's bashrc config file ..."
          echo "   [PREVIOUS settings will be overridden -- consider editing file \"$BASHRC\" for clarity]\n"
     fi
	echo -e "Appending lines to \"$BASHRC\" ... \n\n"
	echo -e $BASHRC_LINES
	echo -e $BASHRC_LINES >> $BASHRC
     echo -e "REMEMBER TO RUN THE FOLLOWING COMMAND AFTER THIS: $ source $BASHRC\n"
fi
touch $BASHCONFIG_INSTALLED_LOCKFILE

exit 0
