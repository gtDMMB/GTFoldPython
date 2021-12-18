/* StructureTypes.h : CTypes for handling structures and returning lists of them back to 
 *                    Python from the results of calling GTFold;
 * Author: Maxie D. Schmidt (maxieds@gmail.com)
 * Created: 2020.02.03
 */

#ifndef __STRUCTURE_TYPES_H__
#define __STRUCTURE_TYPES_H__

#include "PythonConfig.h"

typedef struct {
     char *dotStruct;
     int  energy;
} StructData_t;

StructData_t StructureFromComponents(char *ds, int e);
PyObject * StructureToPythonTuple(StructData_t sd);
PyObject * StructureListToPythonTupleList(StructData_t *sdList, int sdLength);

#endif
