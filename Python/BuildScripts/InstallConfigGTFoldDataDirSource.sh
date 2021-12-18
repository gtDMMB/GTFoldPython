#!/bin/bash 

#### InstallConfigGTFoldDataDirSource.sh : Configure the local user's bash init scripts;
#### Author: Maxie D. Schmidt (maxieds@gmail.com)
#### Created: 2020.01.27

SED=$(which sed)
READLINK=$(which readlink)

PLATFORM=$(uname -s)
if [[ "$PLATFORM" == "Darwin" ]]; then
        SED=$(which gsed)
        READLINK=$(which greadlink)
fi

GTFOLD_DATADIR_PATH=$(env | grep GTFOLDDATADIR | $SED -e 's/GTFOLDDATADIR=//g')
if [[ "$GTFOLD_DATADIR_PATH" == "" ]]; then
	GTFOLD_DATADIR_PATH="./Testing/ExtraGTFoldThermoData/DefaultGTFold";
fi
GTFOLD_DATADIR_PATH=$($READLINK -f $GTFOLD_DATADIR_PATH)

CSOURCE_FILE="$($READLINK -f ./PythonInterfaceSrc)/GTFoldDataDir.c"
cp $CSOURCE_FILE.in $CSOURCE_FILE
$SED -i "s|##__GTFOLD_DATADIR__##|$GTFOLD_DATADIR_PATH|g" $CSOURCE_FILE

PYSOURCE_FILE="$($READLINK -f ./PythonLibrarySrc)/GTFoldPythonConfig.py"
GTFOLD_DATADIR_PATH=$($READLINK -f $GTFOLD_DATADIR_PATH/..)
$SED -i "s|##--__GTFOLD_DATADIR_PATH__--##|$GTFOLD_DATADIR_PATH\/|g" $PYSOURCE_FILE

exit 0
