/* PartitionFunction.cpp : Call the (templated, hence C++ sourced) GTFold partition function routines;
 * Author: Maxie D. Schmidt (maxieds@gmail.com)
 * Created: 2020.02.08
 */

#include <string.h>
#include <limits.h>

#include "include/options.h"
#include "include/boltzmann_main.h"
#include "include/partition-func.h"
#include "include/partition-func-d2.h"
#include "include/partition-dangle.h"
#include "include/algorithms-partition.h"
#include "include/AdvancedDouble.h"

#include "PartitionFunction.h"
#include "ErrorHandling.h"

#define DERROR_VALUE                        ("NaN")

char * ComputeDsPartitionFunction(MFEStructRuntimeArgs_t *rtArgs) {
     if(rtArgs == NULL) {
          SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CARGS, NULL);
          return strdup(DERROR_VALUE);
     }
     int pf_count_mode = 0;
     if(PF_COUNT_MODE) pf_count_mode=1;
     int no_dangle_mode = 0;
     if(CALC_PF_DO) no_dangle_mode=1;
     if(!SILENT) {
          fprintf(stderr, "\nComputing partition function in -dS mode ..., "
			  "pf_count_mode=%d, no_dangle_mode=%d\n", pf_count_mode, no_dangle_mode);
          fprintf(stderr, "\nComputing partition function...\n");
     }
     t1 = get_seconds();
     double pfuncValueDbl = calculate_partition(rtArgs->numBases, pf_count_mode, no_dangle_mode);
     t1 = get_seconds() - t1;
     if(!SILENT) {
          fprintf(stderr, "\npartition function computation running time: %9.6f seconds\n", t1);
	  if(WRITEAUXFILES || PF_PRINT_ARRAYS_ENABLED) {}
          if(DEBUG) printAllMatrixes();
     }
     free_partition();
     char pfuncValue[STR_BUFFER_SIZE];
     snprintf(pfuncValue, STR_BUFFER_SIZE, "%g", pfuncValueDbl);
     pfuncValue[STR_BUFFER_SIZE - 1] = '\0';
     return strdup(pfuncValue);
}

template<typename T>
char * _ComputeD2PartitionFunction(PartitionFunctionD2<T> pfunc, MFEStructRuntimeArgs_t *rtArgs) {
      int pf_count_mode = 0;
      if(PF_COUNT_MODE) pf_count_mode=1;
      int no_dangle_mode = 0;
      if(CALC_PF_DO) no_dangle_mode=1;
      if(!SILENT) {
           fprintf(stderr, "\nComputing partition function in -d2 mode ..., \n"
			   "pf_count_mode=%d, no_dangle_mode=%d, PF_D2_UP_APPROX_ENABLED=%d\n", 
			   pf_count_mode, no_dangle_mode,PF_D2_UP_APPROX_ENABLED);
           fprintf(stderr, "\nComputing partition function...\n");
      }
      t1 = get_seconds();
      char * pfuncValue = pfunc.calculate_partition(rtArgs->numBases, pf_count_mode, no_dangle_mode, 
		                                    PF_D2_UP_APPROX_ENABLED, scaleFactor).getDoubleValue();
      t1 = get_seconds() - t1;
      if(!SILENT) {
           fprintf(stderr, "partition function computation running time: %f seconds\n\n", t1);
           if(WRITEAUXFILES || PF_PRINT_ARRAYS_ENABLED) 
	        pfunc.printAllMatrixesToFile(pfArraysOutFile);
           if(DEBUG) pfunc.printAllMatrixes();
      }
      pfunc.free_partition();
      return pfuncValue;
}

char * ComputeD2PartitionFunction(int advDblSpec, MFEStructRuntimeArgs_t *rtArgs) {
     if(rtArgs == NULL) {
          SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CARGS, NULL);
	  return strdup(DERROR_VALUE);
     }
     switch(advDblSpec) {
	  case 1: {
               PartitionFunctionD2<AdvancedDouble_Native> d2pfunc;
               return _ComputeD2PartitionFunction<AdvancedDouble_Native>(d2pfunc, rtArgs);
	  }
	  case 2: {
               PartitionFunctionD2<AdvancedDouble_BigNum> d2pfunc;
               return _ComputeD2PartitionFunction<AdvancedDouble_BigNum>(d2pfunc, rtArgs);
	  }
	  case 3: {
               PartitionFunctionD2<AdvancedDouble_Hybrid> d2pfunc;
               return _ComputeD2PartitionFunction<AdvancedDouble_Hybrid>(d2pfunc, rtArgs);
	  }
	  case 4: {
	       PartitionFunctionD2<AdvancedDouble_BigNumOptimized> d2pfunc;
               return _ComputeD2PartitionFunction<AdvancedDouble_BigNumOptimized>(d2pfunc, rtArgs);
	  }
	  default:
               break;
     }
     SetLastErrorCode(GTFPYTHON_ERRNO_PFUNC, NULL);
     return strdup(DERROR_VALUE);
}

