/* PythonConfig.h : Local module Python configuration and C includes;
 * Author: Maxie D. Schmidt (maxieds@gmail.com)
 * Created: 2020.01.22
 */

#ifndef __LOCAL_PYTHON_CONFIG_H__
#define __LOCAL_PYTHON_CONFIG_H__

#include <stddef.h>

#undef __BEGIN_DECLS
#undef __END_DECLS
#ifdef __cplusplus
     #define __BEGIN_DECLS extern "C" {
     #define __END_DECLS }
#else
     #define __BEGIN_DECLS
     #define __END_DECLS
#endif

/* Make "s#" use Py_ssize_t rather than int in PyArg_ParseTuple: */
#define PY_SSIZE_T_CLEAN

#define _USE_MATH_DEFINES
#include <math.h>

#ifdef PYTHON2
     #include <python2.7/Python.h>
     #define PY2K
#else
     #include <Python.h>
     #define PY3K
#endif

#ifndef _GNU_SOURCE
     #define _GNU_SOURCE
     #define GNU_SOURCE
     #define __USE_GNU
     #define _POSIX_C_SOURCE 200809L
     #define _XOPEN_SOURCE   700
     #define _DEFAULT_SOURCE
     #define _BSD_SOURCE
#endif

#define __STDC_LIMIT_MACROS
#define __STDC_CONSTANT_MACROS
#include <inttypes.h>

#ifndef O_PATH
     #define O_PATH		010000000
#endif

#undef NULL
#if defined(__cplusplus)
     #define NULL 0
#else
     #define NULL ((void *)0)
#endif

#include <stdbool.h>
#ifndef true
     #define true 1
     #define false (!true)
#endif

#define MAX_BUFFER_SIZE                    (4096)
#define STR_BUFFER_SIZE                    (1024)

#define IFACELIB_MINOR_VERSION             (0)
#define IFACELIB_MAJOR_VERSION             (1)

#include <stdio.h>

#define __HIDDEN__                         __attribute__((visibility ("hidden")))
#define __EXPORT__                         __attribute__((visibility ("default")))

extern int  *CONFIG_QUIET;
extern int  *CONFIG_VERBOSE;
extern int  *CONFIG_DEBUGGING;
extern FILE *CONFIG_STDMSGOUT;
extern int  *CONFIG_CONS_ENABLED;

extern int      *DANGLE;
extern int      *TMISMATCH;
extern int      *LIMITCDIST;
extern int      *PREFILTER;
extern int      WRITEAUXFILES;
extern int      EXACTINTLOOP;
extern char     outputDir_cstr[STR_BUFFER_SIZE];

#define SetLastErrorCode(ecode, emsg)                                                              \
	do {                                                                                          \
		snprintf(&ErrorCodeErrnoMsg[0], STR_BUFFER_SIZE, "On line %d of C-source %s in %s: %s",  \
			 __LINE__, __FILE__, __func__,                                                      \
			 emsg == NULL ? "Error occurred." : emsg);                                          \
		SetLastErrorCodeLocal(ecode, ErrorCodeErrnoMsg);                                         \
	} while(0)

#define SetCSourceNotImplementedError(msg)                                                         \
	do {                                                                                          \
		snprintf(&ErrorCodeErrnoMsg[0], STR_BUFFER_SIZE, "On line %d of C-source %s in %s: %s",  \
			 __LINE__, __FILE__, __func__, msg != NULL ? msg : "Not implemented!");             \
		PyGILState_STATE pgState = PyGILState_Ensure();                                          \
		PyErr_SetString(PyExc_NotImplementedError, ErrorCodeErrnoMsg);                           \
		PyGILState_Release(pgState);                                                             \
	} while(0)

#endif
