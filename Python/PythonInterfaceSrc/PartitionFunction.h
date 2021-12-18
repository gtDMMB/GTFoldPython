/* PartitionFunction.h : Partition function related functionality from GTFold;
 * Author: Maxie D. Schmidt (maxieds@gmail.com)
 * Created: 2020.02.03
 */

#ifndef __PARTITION_FUNCTION_H__
#define __PARTITION_FUNCTION_H__

#ifdef __cplusplus
extern "C" {
#endif

#include "PythonConfig.h"
#include "MFEStruct.h"

char * ComputeDsPartitionFunction(MFEStructRuntimeArgs_t *rtArgs);
char * ComputeD2PartitionFunction(int advDblSpec, MFEStructRuntimeArgs_t *rtArgs);

#ifdef __cplusplus
}
#endif

#endif
