#!/bin/bash

PLATFORM=$(uname -s)
if [[ "$PLATFORM" != "Darwin" ]]; then
	exit 0
fi

OBJCOPY=/usr/local/opt/binutils/bin/objcopy
archiveFile=$(greadlink -f $1)

echo "OBJCOPY: Translated symbols in generated libgomp.a archive on Mac ... "
$OBJCOPY --redefine-sym ___emutls_v.gomp_tls_data=gomp_tls_data $archiveFile
$OBJCOPY --redefine-sym ___builtin_acc_on_device=__builtin_acc_on_device $archiveFile

exit 0

