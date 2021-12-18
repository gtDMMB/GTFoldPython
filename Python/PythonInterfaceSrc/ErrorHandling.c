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

char ErrorCodeErrnoMsg[STR_BUFFER_SIZE] = { '\0' };
ErrorCode_t ErrorCodeErrno = { GTFPYTHON_ERRNO_OK, "No error (init value)" };
char __SignalNameBuffer[STR_BUFFER_SIZE] = { '\0' };

const ErrorCode_t GetErrorCode(int ecode) {
     if(ecode < 0 || ecode >= GetArrayLength(GTFPYTHON_ERROR_CODES)) {
          return (ErrorCode_t) { -1, "Invalid error code" };
     }
     return GTFPYTHON_ERROR_CODES[ecode];
}

int SetLastErrorCodeLocal(int ecode, const char *customErrorMsg) {
     if(ecode < 0 || ecode >= GetArrayLength(GTFPYTHON_ERROR_CODES)) {
          ErrorCodeErrno.errorCode = -1;
          strncpy(&ErrorCodeErrno.errorMsg[0], "Invalid error code", STR_BUFFER_SIZE);
          ErrorCodeErrno.errorMsg[STR_BUFFER_SIZE - 1] = '\0';
     }
     else {
          ErrorCodeErrno.errorCode = ecode;
          strncpy(&ErrorCodeErrno.errorMsg[0], GTFPYTHON_ERROR_CODES[ecode].errorMsg, STR_BUFFER_SIZE);
          ErrorCodeErrno.errorMsg[STR_BUFFER_SIZE - 1] = '\0';
     }
     PyGILState_STATE pgState = PyGILState_Ensure();
     PyErr_Clear();
     if(customErrorMsg != NULL) {
          strncpy(&ErrorCodeErrno.errorMsg[0], customErrorMsg, STR_BUFFER_SIZE);
          ErrorCodeErrno.errorMsg[STR_BUFFER_SIZE - 1] = '\0';
     }
     if(ErrorCodeErrno.errorCode != GTFPYTHON_ERRNO_OK && !PyErr_Occurred()) {
          PyErr_SetString(PyExc_RuntimeError, (const char *) &ErrorCodeErrno.errorMsg[0]);
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
     ErrorCodeErrno.errorMsg[STR_BUFFER_SIZE - 1] = '\0';
     fprintf(stderr, "%s\n", ErrorCodeErrno.errorMsg);
}

void * RaiseErrorException(void) {
     ErrorCodeErrno.errorMsg[STR_BUFFER_SIZE - 1] = '\0';
     fprintf(stderr, "GTFoldPython::RuntimeException: %s\n", ErrorCodeErrno.errorMsg);
     return NULL;
}

void keyboard_interrupt_handler(int signum, siginfo_t *siginfo, void *ctx) {
     char interruptDescMsg[MAX_BUFFER_SIZE];
     snprintf(&interruptDescMsg, MAX_BUFFER_SIZE, "User generated keyboard interrupt (%s)", 
              GetSignalNameString(signum));
     fprintf(stderr, "GTFoldPython::RuntimeException: %s\n", interruptDescMsg);
     if(signum == SIGINT) {
          exit(GTFPYTHON_ERRNO_KBDINTERRUPT);
     }
}

void keyboard_interrupt_register(void) {
     struct sigaction sa;
     memset(&sa, 0x00, sizeof(sa));
     sa.sa_sigaction = &keyboard_interrupt_handler;
     sa.sa_flags = SA_SIGINFO;
     sigaction(SIGINT, &sa, NULL);
}

void segfault_interrupt_handler(int signum, siginfo_t *siginfo, void *ctx) {
     char interruptDescMsg[MAX_BUFFER_SIZE];
     snprintf(&interruptDescMsg, MAX_BUFFER_SIZE, "Unexpected memory access error (%s) -- %s",
              GetSignalNameString(signum), ErrorCodeErrno.errorMsg);
     fprintf(stderr, "GTFoldPython::RuntimeException: %s\n", interruptDescMsg);
     if(signum == SIGSEGV) {
          exit(GTFPYTHON_ERRNO_MEMORY_SIGSEGV);
     }
}

void segfault_interrupt_register(void) {
     struct sigaction sa;
     memset(&sa, 0x00, sizeof(sa));
     sa.sa_sigaction = &segfault_interrupt_handler;
     sa.sa_flags = SA_SIGINFO;
     sigaction(SIGSEGV, &sa, NULL);
}

void all_interrupt_register(void) {
     keyboard_interrupt_register();
     segfault_interrupt_register();
}
