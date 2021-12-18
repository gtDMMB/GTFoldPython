/* StructureTypes.c : Implementation of the header interface;
 * Author: Maxie D. Schmidt (maxieds@gmail.com)
 * Created: 2020.02.03
 */

#include "StructureTypes.h"
#include "ErrorHandling.h"
#include "Utils.h"

StructData_t StructureFromComponents(char *ds, int e) {
     StructData_t sdata;
     sdata.dotStruct = ds;
     sdata.energy = e;
     return sdata;
}

PyObject * StructureToPythonTuple(StructData_t sd) {
     PyGILState_STATE pgState = PyGILState_Ensure();
     PyObject *tupleRef = PyTuple_New(2);
     PyGILState_Release(pgState);
     if(tupleRef == NULL) {
          SetLastErrorCode(GTFPYTHON_ERRNO_NOMEM, NULL);
	  return ReturnPythonNone();
     }
     pgState = PyGILState_Ensure();
     PyTuple_SetItem(tupleRef, 0, PyUnicode_FromString(sd.dotStruct));
     PyTuple_SetItem(tupleRef, 1, PyLong_FromLong(sd.energy));
     Py_INCREF(tupleRef);
     PyGILState_Release(pgState);
     return tupleRef;
}

PyObject * StructureListToPythonTupleList(StructData_t *sdList, int sdLength) {
     if(sdList == NULL || sdLength < 0) {
          SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CARGS, NULL);
          return ReturnPythonNone();
     }
     PyGILState_STATE pgState = PyGILState_Ensure();
     PyObject *structTupleList = PyList_New(sdLength);
     PyGILState_Release(pgState);
     if(structTupleList == NULL) {
          SetLastErrorCode(GTFPYTHON_ERRNO_NOMEM, NULL);
	  return ReturnPythonNone();
     }
     pgState = PyGILState_Ensure();
     for(int sdi = 0; sdi < sdLength; sdi++) {
          PyList_SetItem(structTupleList, sdi, StructureToPythonTuple(sdList[sdi]));
     }
     Py_INCREF(structTupleList);
     PyGILState_Release(pgState);
     return structTupleList;
}
