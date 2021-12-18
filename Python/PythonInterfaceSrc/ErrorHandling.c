/* ErrorHandling.c : Implementation of the header-defined interface;
 * Author: Maxie D. Schmidt (maxieds@gmail.com)
 * Created: 2020.01.22
 */

#include "ErrorHandling.h"
#include "Utils.h"
#include "PythonConfig.h"

const ErrorCode_t GTFPYTHON_ERROR_CODES[] = {
     { GTFPYTHON_ERRNO_OK,                   "No error" },
     { GTFPYTHON_ERRNO_INVALID_CARGS,        "Invalid arguments specified (to C source function)" },
     { GTFPYTHON_ERRNO_INVALID_PYARGS,       "Invalid arguments passed (to Python source function)" },
     { GTFPYTHON_ERRNO_INVALID_CONSTRAINT,   "Invalid constraint (F/P; i, j, k) specified" },
     { GTFPYTHON_ERRNO_NOMEM,                "No memory available" },
     { GTFPYTHON_ERRNO_INVITER,              "Invalid C-Python iterator type" },
     { GTFPYTHON_ERRNO_OTHER,                "Other (C source) error occurred" },
     { GTFPYTHON_ERRNO_BASESEQ,              "Invalid base sequence" },
     { GTFPYTHON_ERRNO_STRLEN,               "String exceeds the buffer size." },
     { GTFPYTHON_ERRNO_DANGLE,               "Invalid DANGLE parameter." },
     { GTFPYTHON_ERRNO_INVDIST,              "Invalid distance specified." },
     { GTFPYTHON_ERRNO_INVSHAPE,             "Invalid shape constraint." },
     { GTFPYTHON_ERRNO_INVPARAM,             "Invalid parameter." },
     { GTFPYTHON_ERRNO_RUNCFG,               "Mis-set run configuration parameter." },
     { GTFPYTHON_ERRNO_OUTFILESCFG,          "Invalid config of the aux output files." }, 
     { GTFPYTHON_ERRNO_MKDIR,                "Error running mkdir(2)." },
     { GTFPYTHON_ERRNO_SUBOPT,               "Error generating subopt structures." },
     { GTFPYTHON_ERRNO_INVBOLTZPARAMS,       "Error setting gtboltzmann parameters." }, 
     { GTFPYTHON_ERRNO_PFUNC,                "Error in the partition func parameters." },
     { GTFPYTHON_ERRNO_BSAMP,                "Boltzmann sampling error." },
     { GTFPYTHON_ERRNO_FNOEXIST,             "File path does not exist." }, 
     { GTFPYTHON_ERRNO_INVTHERMOPARAMS,      "Invalid thermodynamic parameters set." }, 
     { GTFPYTHON_ERRNO_NAMENOTFOUND,         "Requested name key not found. " }, 
};

char ErrorCodeErrnoMsg[6 * STR_BUFFER_SIZE] = { '\0' };
ErrorCode_t ErrorCodeErrno = { GTFPYTHON_ERRNO_OK, "No error (init value)" };

const ErrorCode_t GetErrorCode(int ecode) {
     if(ecode < 0 || ecode >= GetArrayLength(GTFPYTHON_ERROR_CODES)) {
          return (ErrorCode_t) { -1, "Invalid error code" };
     }
     return GTFPYTHON_ERROR_CODES[ecode];
}

int SetLastErrorCodeLocal(int ecode, const char *customErrorMsg) {
     PyGILState_STATE pgState = PyGILState_Ensure();
     PyErr_Clear();
     ErrorCodeErrno = GetErrorCode(ecode);
     if(customErrorMsg != NULL) {
          strncpy(ErrorCodeErrnoMsg, customErrorMsg, STR_BUFFER_SIZE);
          ErrorCodeErrnoMsg[STR_BUFFER_SIZE - 1] = '\0';
          ErrorCodeErrno.errorMsg = ErrorCodeErrnoMsg;
     }
     if(ecode != GTFPYTHON_ERRNO_OK) {
          PyErr_SetString(PyExc_RuntimeError, ErrorCodeErrno.errorMsg); 
     }
     PyGILState_Release(pgState);
     return ErrorCodeErrno.errorCode;
}

int GetLastErrorCode(void) {
     return ErrorCodeErrno.errorCode;
}

const char * ErrorCodeStrerror(int ecode) {
     return GetErrorCode(ecode).errorMsg;
}

void ErrorCodePerror(const char *errorMsgPrefix) {
     if(errorMsgPrefix != NULL) {
          fprintf(stderr, "%s: ", errorMsgPrefix);
     }
     fprintf(stderr, "%s\n", ErrorCodeErrno.errorMsg);
}
