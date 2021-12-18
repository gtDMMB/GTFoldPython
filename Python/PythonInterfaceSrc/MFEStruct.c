/* MFEStruct.c : Implementations of the header interface;
 * Author: Maxie D. Schmidt (maxieds@gmail.com)
 * Created: 2020.01.22
 */

#include <assert.h>

#include "include/mfe_main.h"
#include "include/global.h"
#include "include/traceback.h"
#include "include/options.h"
#include "include/loader.h"

#include "MFEStruct.h"
#include "ErrorHandling.h"
#include "Utils.h"
#include "LoadThermoParams.h"
#include "GTFoldDataDir.c"

void InitMFEStructRuntimeArgs(MFEStructRuntimeArgs_t *rtArgs) {
     if(rtArgs == NULL) {
          return;
     }
     rtArgs->baseSeq = NULL;
     rtArgs->numBases = rtArgs->numConstraints = 0;
     rtArgs->mfeConstraints = rtArgs->mfeSHAPEConstraints = NULL;
}

void FreeMFEStructRuntimeArgs(MFEStructRuntimeArgs_t *rtArgs) {
     if(rtArgs == NULL) {
          return;
     }
     Free(rtArgs->mfeConstraints);
     Free(rtArgs->mfeSHAPEConstraints);
}

int InitGTFoldMFEStructureData(MFEStructRuntimeArgs_t *rtArgs) {
     if(rtArgs == NULL) {
          SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CARGS, NULL);
	  return ErrorCodeErrno.errorCode;
     }
     // wrapper around global.cc::init_fold(char * seq):
     init_global_params(rtArgs->numBases);
     if(!encodeSequence(rtArgs->baseSeq)) {
          SetLastErrorCode(GTFPYTHON_ERRNO_BASESEQ, NULL);
	  return ErrorCodeErrno.errorCode;
     }
     create_tables(rtArgs->numBases);
     //readThermodynamicParameters(GTFOLD_DATADIR, 1, UNAMODE, RNAMODE, T_MISMATCH);
     if(LoadThermodynamicParameters(ACTIVE_THERMO_PARAMS, GTFOLD_DATADIR) != GTFPYTHON_ERRNO_OK) {
          return GetLastErrorCode();
     }
     int initStatus = InitGTFoldConstraints(rtArgs);
     if(initStatus != GTFPYTHON_ERRNO_OK) {
          free_global_params(rtArgs->numBases);
	  return initStatus;
     }
     g_nthreads = nThreads;
     g_unamode  = UNAMODE;
     g_mismatch = T_MISMATCH;
     g_verbose  = VERBOSE;
     g_prefilter_mode  = b_prefilter;
     g_prefilter1  = prefilter1;
     g_prefilter2  = prefilter2;
     g_dangles = dangles;
     return initStatus;
}

int FreeGTFoldMFEStructureData(int baseSeqLength) {
     free_fold(baseSeqLength);
     SetLastErrorCode(GTFPYTHON_ERRNO_OK, NULL);
     return ErrorCodeErrno.errorCode;
}

int ParseGetMFEStructureArgs(ConsListCType_t consList, int consLength, MFEStructRuntimeArgs_t *rtArgs) {
     if(consList == NULL || consLength < 0 || rtArgs == NULL) {
          SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CARGS, NULL);
	  return ErrorCodeErrno.errorCode;
     }
     int baseCount = rtArgs->numBases;
     rtArgs->mfeConstraints = ParseConstraintsList(consList, consLength);
     rtArgs->numConstraints = consLength;
     if(rtArgs->mfeConstraints == NULL && rtArgs->numConstraints > 0) {
          return GetLastErrorCode();
     }
     SetLastErrorCode(GTFPYTHON_ERRNO_OK, NULL);
     return ErrorCodeErrno.errorCode;
}

int ParseGetMFEStructureSHAPEArgs(SHAPEConstraint_t *scList, int consLength, 
		                  MFEStructRuntimeArgs_t *rtArgs) {
     if(scList == NULL || consLength < 0 || rtArgs == NULL) {
          SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CARGS, NULL);
	  return ErrorCodeErrno.errorCode;
     }
     int baseCount = rtArgs->numBases;
     rtArgs->mfeSHAPEConstraints = scList;
     rtArgs->numSHAPEConstraints = consLength;
     SetLastErrorCode(GTFPYTHON_ERRNO_OK, NULL);
     return ErrorCodeErrno.errorCode;
}

PyObject * PrepareMFETupleResult(double mfe, const char *dotBrackMFEStruct) {
     if(dotBrackMFEStruct == NULL) {
          return NULL;
     }
     PyGILState_STATE pgState = PyGILState_Ensure();
     PyObject *tupleRes = PyTuple_New(2);
     PyTuple_SetItem(tupleRes, 0, PyFloat_FromDouble(mfe));
     PyTuple_SetItem(tupleRes, 1, PyUnicode_FromString(dotBrackMFEStruct));
     Py_INCREF(tupleRes);
     PyGILState_Release(pgState);
     return tupleRes;
}

double ComputeMFEStructure(MFEStructRuntimeArgs_t *rtArgs) {
     if(rtArgs == NULL) {
          SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CARGS, NULL);
	  return 0.0;
     }
     double mfe = calculate_mfe(rtArgs->numBases);
     trace(rtArgs->numBases, 0, NULL);
     return mfe;
}

char * ComputeDOTStructureResult(int baseSeqLength) {
     char * dbStructStr = (char *) malloc((baseSeqLength + 1) * sizeof(char));
     if(dbStructStr == NULL) {
          SetLastErrorCode(GTFPYTHON_ERRNO_NOMEM, NULL);
	  return "";
     }
     for(int si = 1; si <= baseSeqLength; si++) {
          if(structure[si] > 0 && structure[si] > si) {
	       dbStructStr[si - 1] = '(';
	  }
	  else if(structure[si] > 0 && structure[si] < si) {
	       dbStructStr[si - 1] = ')';
	  }
	  else {
	       dbStructStr[si - 1] = '.';
	  }
     }
     dbStructStr[baseSeqLength] = '\0';
     return dbStructStr;
}

int VerifyGTFoldMFEStructure(void) {
     // the code to do this while the internal GTFold structures have not been freed after 
     // computing the MFE data is found in src/constraints.cc:355
     fprintf(CONFIG_STDMSGOUT, "ERROR: This function is not implemented!\n");
     assert(0);
}
