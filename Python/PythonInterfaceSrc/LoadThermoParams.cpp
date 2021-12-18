/* LoadThermoParams.cpp : Implementation of the header interface;
 * Author: Maxie D. Schmidt (maxieds@gmail.com)
 * Created: 2020.02.21
 */

#include <sys/types.h>
#include <sys/stat.h>

#include "include/loader.h"
#include "include/options.h"

#include "LoadThermoParams.h"
#include "ErrorHandling.h"
#include "Utils.h"

const ThermoParams_t STATIC_THERMO_PARAMS_CONFIG[] = {
	{
	     "default",
	     NULL, 
	     "miscloop.DAT", 
	     "dangle.DAT",
	     "stack.DAT", 
	     "loop.DAT", 
	     "tloop.DAT", 
	     "tstackh.DAT",
	     "tstacki.DAT", 
             "tstackm.DAT", 
	     "tstacke.DAT",
	     "", 
	     "int21.DAT", 
	     "int22.DAT", 
             "int11.DAT"
	},
	{
	     "GTFold", 
	     NULL,
	     "miscloop.DAT", 
	     "dangle.DAT",
	     "stack.DAT", 
	     "loop.DAT", 
	     "tloop.DAT", 
	     "tstackh.DAT",
	     "tstacki.DAT", 
             "tstackm.DAT", 
	     "tstacke.DAT",
	     "", 
	     "int21.DAT", 
	     "int22.DAT", 
             "int11.DAT"
     },
     {
	     "RNAStructure", 
	     NULL,
             "miscloop.DAT", 
	     "dangle.DAT",
	     "stack.DAT", 
	     "loop.DAT", 
	     "tloop.DAT", 
	     "tstackh.DAT",
	     "tstacki.DAT", 
             "tstackm.DAT", 
	     "tstacke.DAT",
	     "tstacki23.DAT", 
	     "int21.DAT", 
	     "int22.DAT", 
             "int11.DAT"
     },
     {
	     "RNAFold", 
	     &RNAMODE, 
             "miscloop.DAT", 
	     "dangle.DAT",
	     "stack.DAT", 
	     "loop.DAT", 
	     "tloop.DAT", 
	     "tstackh.DAT",
	     "tstacki.DAT", 
             "tstackm.DAT", 
	     "tstacke.DAT",
	     "", 
	     "int21.DAT", 
	     "int22.DAT", 
             "int11.DAT"
     },
     {
	     "UNAFold",
	     &UNAMODE,
             "miscloop.DAT", 
	     "dangle.DAT",
	     "stack.DAT", 
	     "loop.DAT", 
	     "tloop.DAT", 
	     "tstackh.DAT",
	     "tstacki.DAT", 
             "tstackm.DAT", 
	     "tstacke.DAT",
	     "tstacki23.DAT", 
	     "asint1x2.DAT", 
	     "sint4.DAT", 
             "sint2.DAT"
     },
     {
	     "Turner04",
	     &RNAMODE, 
	     "miscloop.DAT", 
	     "dangle.DAT", 
	     "stack.DAT",
	     "loop.DAT", 
	     "tloop.DAT", 
	     "tstackh.DAT",
	     "tstacki.DAT", 
             "tstackm.DAT", 
	     "tstacke.DAT",
	     "", 
	     "int21.DAT", 
	     "int22.DAT", 
             "int11.DAT"
     },
};

const ThermoParams_t *ACTIVE_THERMO_PARAMS = &(STATIC_THERMO_PARAMS_CONFIG[0]);

int CheckThermodynamicConfig(const ThermoParams_t *tparams, const char *baseSearchDir) {
     if(tparams == NULL || baseSearchDir == NULL) {
          SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CARGS, NULL);
	  return GetLastErrorCode();
     }
     if(!IsDirectory(baseSearchDir) || 
	!FileExists(tparams->miscLoop, baseSearchDir) || 
	!FileExists(tparams->dangleValues, baseSearchDir) || 
	!FileExists(tparams->stackValues, baseSearchDir) || 
	!FileExists(tparams->loopValues, baseSearchDir) || 
	!FileExists(tparams->tloopValues, baseSearchDir) || 
	!FileExists(tparams->tstackhValues, baseSearchDir) || 
	!FileExists(tparams->tstackiValues, baseSearchDir) || 
	!FileExists(tparams->int21Values, baseSearchDir) || 
	!FileExists(tparams->int22Values, baseSearchDir) || 
	!FileExists(tparams->int11Values, baseSearchDir)) {
          SetLastErrorCode(GTFPYTHON_ERRNO_FNOEXIST, "Loading thermo parameters");
	  return GTFPYTHON_ERRNO_FNOEXIST;
     }
     else if(UNAMODE && !FileExists(tparams->tstack23Values, baseSearchDir)) {
	  SetLastErrorCode(GTFPYTHON_ERRNO_FNOEXIST, "Loading thermo parameters");
	  return GTFPYTHON_ERRNO_FNOEXIST;
     }
     else if(!UNAMODE && !(*TMISMATCH)) {
	  return GTFPYTHON_ERRNO_OK;
     }
     else if(!FileExists(tparams->tstackmValues, baseSearchDir) || 
             !FileExists(tparams->tstackeValues, baseSearchDir)) {
	  SetLastErrorCode(GTFPYTHON_ERRNO_FNOEXIST, "Loading thermo parameters");
	  return GTFPYTHON_ERRNO_FNOEXIST;
     }
     return GTFPYTHON_ERRNO_OK;
}

int LoadThermodynamicParameters(const ThermoParams_t *tparams, const char *baseSearchDir) {
     if(tparams == NULL || baseSearchDir == NULL) {
          SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CARGS, NULL);
	  return GetLastErrorCode();
     }
     else if(CheckThermodynamicConfig(tparams, baseSearchDir)) {
	  SetLastErrorCode(GTFPYTHON_ERRNO_FNOEXIST, NULL);
	  return GetLastErrorCode();
     }
     char thermoDataDir[STR_BUFFER_SIZE];
     strcpy(thermoDataDir, baseSearchDir);
     if(thermoDataDir[strlen(baseSearchDir) - 1] != '/') {
          strcat(thermoDataDir, "/");
     }
     strcpy(EN_DATADIR, thermoDataDir);
     struct stat statBuf;
     if(stat(EN_DATADIR, &statBuf) == -1){
          fprintf(stderr, "Checking for parameter files in dir '%s', not found.\n", EN_DATADIR);
          fprintf(stderr, "Error: %s\n\n", strerror(errno));
          errno = EINVAL;
          exit(-1);
     }
     initMiscloopValues(tparams->miscLoop,   thermoDataDir);
     initDangleValues(tparams->dangleValues, thermoDataDir);
     initStackValues(tparams->stackValues,   thermoDataDir);
     initLoopValues(tparams->loopValues,     thermoDataDir);
     initTstkhValues(tparams->tstackhValues, thermoDataDir);
     initTstkiValues(tparams->tstackiValues, thermoDataDir);
     initTloopValues(tparams->tloopValues,   thermoDataDir);
     if(UNAMODE) {
          initInt21Values(tparams->int21Values,     thermoDataDir);
          initInt22Values(tparams->int22Values,     thermoDataDir);
          initInt11Values(tparams->int11Values,     thermoDataDir);
          initTstkmValues(tparams->tstackmValues,   thermoDataDir);
          initTstkeValues(tparams->tstackeValues,   thermoDataDir);
          initTstk23Values(tparams->tstack23Values, thermoDataDir);
     }
     else if(*TMISMATCH) {
          initTstkmValues(tparams->tstackmValues, thermoDataDir);
          initTstkeValues(tparams->tstackeValues, thermoDataDir);
          initInt21Values(tparams->int21Values,   thermoDataDir);
          initInt22Values(tparams->int22Values,   thermoDataDir);
          initInt11Values(tparams->int11Values,   thermoDataDir);
     }
     else {
	  initInt21Values(tparams->int21Values, thermoDataDir);
          initInt22Values(tparams->int22Values, thermoDataDir);
          initInt11Values(tparams->int11Values, thermoDataDir);
	  if(FileExists(tparams->tstackmValues, thermoDataDir)) {
	       initTstkmValues(tparams->tstackmValues, thermoDataDir);
	  }
	  if(FileExists(tparams->tstackeValues, thermoDataDir)) {
	       initTstkeValues(tparams->tstackeValues, thermoDataDir);
	  }
     }
     return GTFPYTHON_ERRNO_OK;
}

int SetThermodynamicMode(const char *presetConfigName) {
     if(presetConfigName == NULL) {
          SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CARGS, NULL);
	  return GetLastErrorCode();
     }
     else if(!strncasecmp("default", presetConfigName, 7)) {
          ACTIVE_THERMO_PARAMS = &(STATIC_THERMO_PARAMS_CONFIG[0]);
	  return GTFPYTHON_ERRNO_OK;
     }
     for(int tpIdx = 0; tpIdx < GetArrayLength(STATIC_THERMO_PARAMS_CONFIG); tpIdx++) {
          if(!strcasecmp(STATIC_THERMO_PARAMS_CONFIG[tpIdx].configName, presetConfigName)) {
               if(ACTIVE_THERMO_PARAMS->configSettingParam != NULL) {
	            *(ACTIVE_THERMO_PARAMS->configSettingParam) = 0;
	       }
	       ACTIVE_THERMO_PARAMS = &(STATIC_THERMO_PARAMS_CONFIG[tpIdx]);
               if(ACTIVE_THERMO_PARAMS->configSettingParam != NULL) {
                    *(ACTIVE_THERMO_PARAMS->configSettingParam) = 1;
	       }
	       return GTFPYTHON_ERRNO_OK;
	  }
     }
     SetLastErrorCode(GTFPYTHON_ERRNO_NAMENOTFOUND, NULL);
     return GetLastErrorCode();
}

