#!/bin/bash

SED=sed
READLINK=readlink

PLATFORM_DESC_FULL=$(uname -a)
PLATFORM_NAME=$(uname -s)
if [[ "$PLATFORM_NAME" == "Darwin" ]]; then 
	SED=gsed
	READLINK=greadlink
fi

CONFIG_HEADER_LOCATION=$($READLINK -f PythonLibrarySrc/GTFoldPythonConfig.py)
cp $CONFIG_HEADER_LOCATION.in $CONFIG_HEADER_LOCATION

THERMO_PARAMS_BASEDIR=$($READLINK -f Testing/ExtraGTFoldThermoData)
$SED -i "s|##__THERMO_PARAMS_EXTRA_DATA_BASEDIR__##|$THERMO_PARAMS_BASEDIR|g" $CONFIG_HEADER_LOCATION

if [[ "$PLATFORM_NAME" == "Darwin" ]]; then 
	$SED -i 's/##__PLATFORM_APPLE_MACOSX__##/True/g' $CONFIG_HEADER_LOCATION
elif [[ "$PLATFORM_NAME" == "Linux" ]]; then 
	$SED -i 's/##__PLATFORM_LINUX__##/True/g' $CONFIG_HEADER_LOCATION
else
	$SED -i 's/##__PLATFORM_OTHER__##/True/g' $CONFIG_HEADER_LOCATION
fi

$SED -i "s|##__PLATFORM_VERSION_STRING__##|$PLATFORM_NAME|g" $CONFIG_HEADER_LOCATION
$SED -i "s|##__PLATFORM_VERSION_FULL_DETAILS_STRING__##|$PLATFORM_DESC_FULL|g" $CONFIG_HEADER_LOCATION
$SED -i 's/##__[A-Z][_A-Z]*__##/False/g' $CONFIG_HEADER_LOCATION

exit 0

