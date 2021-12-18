/* ErrorHandling.h : Error codes and handling routines for the Python interface;
 * Author: Maxie D. Schmidt (maxieds@gmail.com)
 * Created: 2020.01.22
 */

#ifndef __ERROR_HANDLING_H__
#define __ERROR_HANDLING_H__

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <signal.h>

#ifdef __cplusplus
extern "C" {
#endif

#include "PythonConfig.h"
#include "Utils.h"

typedef struct {
     int errorCode;
     char errorMsg[STR_BUFFER_SIZE];
} ErrorCode_t;

#define GTFPYTHON_ERRNO_OK                     (0)
#define GTFPYTHON_ERRNO_INVALID_CARGS          (1)
#define GTFPYTHON_ERRNO_INVALID_PYARGS         (2)
#define GTFPYTHON_ERRNO_INVALID_CONSTRAINT     (3)
#define GTFPYTHON_ERRNO_NOMEM                  (4)
#define GTFPYTHON_ERRNO_INVITER                (5)
#define GTFPYTHON_ERRNO_OTHER                  (6)
#define GTFPYTHON_ERRNO_BASESEQ                (7)
#define GTFPYTHON_ERRNO_STRLEN                 (8)
#define GTFPYTHON_ERRNO_DANGLE                 (9)
#define GTFPYTHON_ERRNO_INVDIST                (10)
#define GTFPYTHON_ERRNO_INVSHAPE               (11)
#define GTFPYTHON_ERRNO_INVPARAM               (12)
#define GTFPYTHON_ERRNO_RUNCFG                 (13)
#define GTFPYTHON_ERRNO_OUTFILESCFG            (14)
#define GTFPYTHON_ERRNO_MKDIR                  (15)
#define GTFPYTHON_ERRNO_SUBOPT                 (16)
#define GTFPYTHON_ERRNO_INVBOLTZPARAMS         (17)
#define GTFPYTHON_ERRNO_PFUNC                  (18)
#define GTFPYTHON_ERRNO_BSAMP                  (19)
#define GTFPYTHON_ERRNO_FNOEXIST               (20)
#define GTFPYTHON_ERRNO_INVTHERMOPARAMS        (21)
#define GTFPYTHON_ERRNO_NAMENOTFOUND           (22)
#define GTFPYTHON_ERRNO_KBDINTERRUPT           (23)
#define GTFPYTHON_ERRNO_MEMORY_SIGSEGV         (24)

extern const ErrorCode_t GTFPYTHON_ERROR_CODES[]; 
extern char ErrorCodeErrnoMsg[STR_BUFFER_SIZE];
extern ErrorCode_t ErrorCodeErrno;

const ErrorCode_t GetErrorCode(int ecode);
int SetLastErrorCodeLocal(int ecode, const char *customErrorMsg);
int GetLastErrorCode(void);
const char * ErrorCodeStrerror(int ecode);
void ErrorCodePerror(const char *errorMsgPrefix);
void * RaiseErrorException(void);

static inline const char * GetPlatformSignalNameString(int signum) {
     #if defined(__APPLE__) || defined(__APPLE_CC__) || defined(__OSX__)
          return sys_signame[signum];
     #else
	  return strsignal(signum);
     #endif
}

/* Handle <CTRL+C> keypresses (SIGINT signals) gracefully -- even while 
 * running computationally intensive code snippets between the Python 
 * bindings glue:
 */
extern char __SignalNameBuffer[STR_BUFFER_SIZE];
#define GetSignalNameString(signum)            ({                                           \
     char *localSigTypeStr = NULL;                                                          \
     __SignalNameBuffer[0] = '\0';                                                          \
     do {                                                                                   \
          localSigTypeStr = strdup(GetPlatformSignalNameString(signum));                    \
          if(localSigTypeStr) {                                                             \
               StringToUpper(localSigTypeStr);                                              \
               snprintf(&__SignalNameBuffer[0], STR_BUFFER_SIZE, "SIG%s", localSigTypeStr); \
               __SignalNameBuffer[STR_BUFFER_SIZE - 1] = '\0';                              \
               free(localSigTypeStr);                                                       \
          }                                                                                 \
     } while(0);                                                                            \
     __SignalNameBuffer;                                                                    \
     })

void keyboard_interrupt_handler(int signum, siginfo_t *siginfo, void *ctx);
void keyboard_interrupt_register(void);
void segfault_interrupt_handler(int signum, siginfo_t *siginfo, void *ctx);
void segfault_interrupt_register(void);
void all_interrupt_register(void);

#ifdef __cplusplus
}
#endif

#endif
