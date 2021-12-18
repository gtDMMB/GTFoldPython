#!/bin/bash

PYTHON3=python3
READLINK=readlink

PLATFORM_VERSION=$(uname -s)
if [[ "$PLATFORM_VERSION" == "Darwin" ]]; then
	READLINK=greadlink
fi

PARAMS_LIST_DIR=$($READLINK -f ../Testing/ExtraGTFoldThermoData/BuildingCustomDataSets)
TSTACKI_FILE="$PARAMS_LIST_DIR/turner-tstacki-rna.DAT"
PARAM_FILES=(\
	"CG_best_parameters_ISMB2007.txt" \
	"CG_parameters_v1.1.txt" \
	"parameters_CC06.txt" \ 
	"parameters_CC09.txt" \
	"parameters_DP03.txt" \
	"parameters_DP09.txt" \
	"parameters_MT09.txt" \
	"parameters_MT99.txt" \
	"turner_parameters_fm363_constrdangles.txt" \
	"turner_parameters_fm363_dangles0.txt" \
)

PARAM_DEST_BASEDIR=$($READLINK -f ../Testing/ExtraGTFoldThermoData)
PARAM_DEST_DATASET_DIRS=(\
	"CGBestISMB2007" \
	"CGV11" \
	"CC06" \
	"CC09" \
	"DP03" \
	"DP09" \
	"MT09" \
	"MT99" \
	"TurnerFM363ConstrDangles" \
	"TurnerFM363Dangles0" \
)

NUM_DATASETS=${#PARAM_FILES[@]}
for dsIdx in $(seq 0 $NUM_DATASETS); do
	echo "  >> Creating data set ${PARAM_DEST_DATASET_DIRS[$dsIdx]} ... "
	mkdir -p $dataSetDestDir
	dataSetDestDir=$PARAM_DEST_BASEDIR/${PARAM_DEST_DATASET_DIRS[$dsIdx]}
	cp $TSTACKI_FILE $dataSetDestDir
	$PYTHON3 $PARAMS_LIST_DIR/${PARAM_FILES[$dsIdx]} $dataSetDestDir
done

exit 0
