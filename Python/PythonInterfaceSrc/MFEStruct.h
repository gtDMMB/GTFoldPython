/* MFEStruct.h : Helper functions for calling GTFold and calculating the MFE and 
 *               MFE structure;
 * Author: Maxie D. Schmidt (maxieds@gmail.com)
 * Created: 2019.01.09
 */

#ifndef __MFESTRUCT_H__
#define __MFESTRUCT_H__

#include "PythonConfig.h"
#include "Constraints.h"

struct _MFEStructRuntimeArgs_t {
     const char *baseSeq;
     int numBases;
     int numConstraints;
     Constraint_t *mfeConstraints;
     int numSHAPEConstraints;
     SHAPEConstraint_t *mfeSHAPEConstraints;
};

typedef struct _MFEStructRuntimeArgs_t MFEStructRuntimeArgs_t;

void InitMFEStructRuntimeArgs(MFEStructRuntimeArgs_t *rtArgs);
void FreeMFEStructRuntimeArgs(MFEStructRuntimeArgs_t *rtArgs);
int InitGTFoldMFEStructureData(MFEStructRuntimeArgs_t *rtArgs);
int FreeGTFoldMFEStructureData(int baseSeqLength);
int ParseGetMFEStructureArgs(ConsListCType_t consList, int consLength, MFEStructRuntimeArgs_t *rtArgs);
int ParseGetMFEStructureSHAPEArgs(SHAPEConstraint_t *scList, int consLength, MFEStructRuntimeArgs_t *rtArgs);
PyObject * PrepareMFETupleResult(double mfe, const char *dotBrackMFEStruct);
double ComputeMFEStructure(MFEStructRuntimeArgs_t *rtArgs);
char * ComputeDOTStructureResult(int baseSeqLength);
int VerifyGTFoldMFEStructure(void);

#endif
