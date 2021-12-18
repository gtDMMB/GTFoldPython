/* BoltzmannSampling.h : Wrapper around the GTFold functionality to sample structures and 
 *                       their corresponding energies from the Boltzmann distribution;
 * Author: Maxie D. Schmidt (maxieds@gmail.com)
 * Created: 2020.02.03
 */

#ifndef __BOLTZMANN_SAMPLING_H__
#define __BOLTZMANN_SAMPLING_H__

#include "PythonConfig.h"

#ifdef __cplusplus
extern "C" {
#endif

#include "MFEStruct.h"
#include "GTFoldDataDir.c"

#define mpf_set_default_prec    __gmpf_set_default_prec

extern int OUTPUT_FILES_CONFIG;

void ConfigureOutputFileSettings(void);
void ValidateOptions(void);

void * ConfigureBoltzmannMainRuntimeParameters(MFEStructRuntimeArgs_t *rtArgs);
PyObject * HandleBPP(MFEStructRuntimeArgs_t *rtArgs);

PyObject * HandleD2Sample(int advDblSpec, int N, MFEStructRuntimeArgs_t *rtArgs);
PyObject * HandleDsSample(int N, MFEStructRuntimeArgs_t *rtArgs);

#ifdef __cplusplus
}
#endif

#endif
