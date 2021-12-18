/* Utils.h : Utility functions (and static inline definitions);
 * Author: Maxie D. Schmidt (maxieds@gmail.com)
 * Created: 2020.01.22
 */

#ifndef __GTFOLD_PYTHON_UTILS_H__
#define __GTFOLD_PYTHON_UTILS_H__

#include "PythonConfig.h"

#ifdef __cplusplus
extern "C" {
#endif

#define GetArrayLength(arr)          (arr != NULL ? sizeof(arr) / sizeof(arr[0]) : 0)
#define GetArrayLengthByNonNULL(arr, arrCountPtr)            \
	do {                                                 \
		int acount = 0;                              \
		int arrLengthUpper = GetArrayLength(arr);    \
		for(int ai = 0; ai < arrLengthUpper; ai++) { \
			if(arr[ai] == NULL) break;           \
			acount++;                            \
		}                                            \
		*arrCountPtr = acount;                       \
	} while(0)

void Free(void *memPtr);
char * CopyString(const char *origStr, int *chCount);

bool IsDirectory(const char *dirPath);
bool IsRegularFile(const char *filePath);
bool FileExists(const char *filePath, const char *baseSearchDir);
bool IsSymbolicLink(const char *linkPath);
bool IsCharacterDevice(const char *devPath);
bool IsFIFOPipe(const char *devPath);

bool FileHasExtension(const char *filePath);
bool SetFileOutPath(char *pathVar, const char *pfxDir, const char *namePfx, 
		    const char *defaultName, const char *defaultExt);

PyObject * ReturnPythonNone(void);
PyObject * ReturnPythonInt(int ival);
void PrintPyObjectDebugging(PyObject *pyObj);

#ifdef __cplusplus
}
#endif

#endif
