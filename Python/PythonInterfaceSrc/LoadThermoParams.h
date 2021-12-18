/* LoadThermoParams.h : Static definitions and helper functions for loading thermodynamic parameters;
 * Author: Maxie D. Schmidt (maxieds@gmail.com) 
 * Created: 2020.02.21
 */

#ifndef __LOAD_THERMO_PARAMS_H__
#define __LOAD_THERMO_PARAMS_H__ 

#include "PythonConfig.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
     const char *configName;
     int  *configSettingParam;
     char miscLoop[48];
     char dangleValues[48];
     char stackValues[48];
     char loopValues[48];
     char tloopValues[48];
     char tstackhValues[48];
     char tstackiValues[48];
     char tstackmValues[48];
     char tstackeValues[48];
     char tstack23Values[48];
     char int21Values[48];
     char int22Values[48];
     char int11Values[48];
} ThermoParams_t;

extern const ThermoParams_t STATIC_THERMO_PARAMS_CONFIG[];
extern const ThermoParams_t *ACTIVE_THERMO_PARAMS;

int CheckThermodynamicConfig(const ThermoParams_t *tparams, const char *baseSearchDir);
int LoadThermodynamicParameters(const ThermoParams_t *tparams, const char *baseSearchDir);
int SetThermodynamicMode(const char *presetConfigName);

#ifdef __cplusplus
}
#endif

#endif
