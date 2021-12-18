/* Utils.c : Implementation of utility functions;
 * Author: Maxie D. Schmidt (maxieds@gmail.com)
 * Created: 2020.01.22
 */

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <limits.h>

#include "Utils.h"
#include "ErrorHandling.h"

void Free(void *memPtr) {
     if(memPtr != NULL) {
          free(memPtr);
     }
}

char * CopyString(const char *origStr, int *chCount) {
     if(origStr == NULL) {
          if(chCount != NULL) {
	       *chCount = 0;
	  }
	  return NULL;
     }
     if(chCount != NULL) {
          *chCount = strlen(origStr);
     }
     return strdup(origStr);
}

bool IsDirectory(const char *dirPath) {
     struct stat st;
     if(lstat(dirPath, &st)) { // error getting the file info struct:
          return false;
     }
     return (st.st_mode & S_IFMT) == S_IFDIR;
}

bool IsRegularFile(const char *filePath) {
     struct stat st;
     if(lstat(filePath, &st)) { // error getting the file info struct:
          return false;
     }
     return (st.st_mode & S_IFMT) == S_IFREG;
}

bool FileExists(const char *filePath, const char *baseDir) {
     if(filePath == NULL || strlen(filePath) == 0) {
          return false;
     }
     else if(baseDir == NULL || strlen(baseDir) == 0) {
	  return IsRegularFile(filePath);
     }
     char fullFilePathBuf[STR_BUFFER_SIZE], absFullFilePathBuf[STR_BUFFER_SIZE];
     int filePathLen = strlen(filePath), baseDirLen = strlen(baseDir);
     bool needSlashChar = (filePath[0] != '/' && baseDir[baseDirLen - 1] != '/');
     snprintf(fullFilePathBuf, STR_BUFFER_SIZE, "%s%s%s", baseDir, needSlashChar ? "/" : "", filePath);
     fullFilePathBuf[STR_BUFFER_SIZE - 1] = '\0';
     //if(realpath(fullFilePathBuf, absFullFilePathBuf)) {
     //     return IsRegularFile(absFullFilePathBuf);
     //}
     //fprintf(stderr, "FILE PATH: %s\n", fullFilePathBuf);
     return IsRegularFile(fullFilePathBuf);
}

bool IsSymbolicLink(const char *linkPath) {
     struct stat st;
     if(lstat(linkPath, &st)) {
          return false;
     }
     return (st.st_mode & S_IFMT) == S_IFLNK;
}

bool IsCharacterDevice(const char *devPath) {
     struct stat st;
     if(lstat(devPath, &st)) {
          return false;
     }
     return (st.st_mode & S_IFMT) == S_IFCHR;
}

bool IsFIFOPipe(const char *filePath) {
     struct stat st;
     if(lstat(filePath, &st)) {
          return false;
     }
     else if((st.st_mode & S_IFMT) != S_IFIFO) {
	  return false;
     }
     int fpFD = open(filePath, O_RDONLY | O_PATH);
     if(fpFD == -1) {
	  return false;
     }
     int attyStatus = isatty(fpFD);
     close(fpFD);
     return attyStatus;
}

bool FileHasExtension(const char *filePath) {
     if(filePath == NULL) {
          return false;
     }
     const char *extPos = strrchr(filePath, '.');
     return extPos != NULL;
}

bool SetFileOutPath(char *pathVar, const char *pfxDir, const char *namePfx, 
		    const char *defaultName, const char *defaultExt) {
     if(pathVar == NULL || pfxDir == NULL || namePfx == NULL || 
        defaultName == NULL || defaultExt == NULL) {
	  return false;
     }
     char tempBuf[STR_BUFFER_SIZE] = { '\0' };
     bool pfxDirHasSlash = strlen(pfxDir) == 0 || pfxDir[strlen(pfxDir) - 1] == '/';
     strcat(tempBuf, pfxDir);
     if(!pfxDirHasSlash) {
          strcat(tempBuf, "/");
     }
     bool namePfxNeedsSep = namePfx[strlen(namePfx) - 1] == '_' && 
	                    namePfx[strlen(namePfx) - 1] == '-';
     strcat(tempBuf, namePfx);
     if(namePfxNeedsSep) {
          strcat(tempBuf, "-");
     }
     if(strlen(pathVar) == 0) {
          strcat(tempBuf, defaultName);
     }
     else {
	  strcat(tempBuf, pathVar);
     }
     if(!FileHasExtension(tempBuf)) {
          strcat(tempBuf, defaultExt);
     }
     strcpy(pathVar, tempBuf);
     return true;
}

PyObject * ReturnPythonNone(void) {
     PyGILState_STATE pgState = PyGILState_Ensure();
     Py_INCREF(Py_None);
     PyGILState_Release(pgState);
     return Py_None;
}

PyObject * ReturnPythonInt(int ival) {
     PyGILState_STATE pgState = PyGILState_Ensure();
     PyObject *pyInt = PyLong_FromLong(ival);
     PyGILState_Release(pgState);
     if(pyInt == NULL) {
          SetLastErrorCode(GTFPYTHON_ERRNO_NOMEM, NULL);
	  return ReturnPythonNone();
     }
     pgState = PyGILState_Ensure();
     Py_INCREF(pyInt);
     PyGILState_Release(pgState);
     return pyInt;
}

void PrintPyObjectDebugging(PyObject *pyObj) {
     if(pyObj == NULL) {
          return;
     }
     fprintf(CONFIG_STDMSGOUT, "\n");
     PyGILState_STATE pgState = PyGILState_Ensure();
     PyObject_Print(pyObj, CONFIG_STDMSGOUT, 0);
     PyGILState_Release(pgState);
     fprintf(CONFIG_STDMSGOUT, "\n");
}


