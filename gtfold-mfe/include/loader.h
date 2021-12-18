/*
 GTfold: compute minimum free energy of RNA secondary structure
 Copyright (C) 2008  David A. Bader
 http://www.cc.gatech.edu/~bader

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#ifndef _LOADER_H
#define _LOADER_H

#include "constants.h"
#include "data.h"

#ifdef __cplusplus
     #include <string>
     extern "C" {

     void readThermodynamicParameters(const char *userdatadir, bool userdatalogic, 
		                      int unamode, int rnamode, int t_mismatch);
     
     int initStackValues(const char *fileName, const char *dirPath);
     int initMiscloopValues(const char *fileName, const char *dirPath);
     int initDangleValues(const char *fileName, const char *dirPath);
     int initLoopValues(const char *fileName, const char *dirPath);
     int initTstkhValues(const char *fileName, const char *dirPath);
     int initTstkiValues(const char *fileName, const char *dirPath);
     int initTloopValues(const char *fileName, const char *dirPath);
     int initInt21Values(const char *fileName, const char *dirPath);
     int initInt22Values(const char *fileName, const char *dirPath);
     int initInt11Values(const char *fileName, const char *dirPath);
     int	initTstkmValues(const char *fileName, const char *dirPath);
     int	initTstkeValues(const char *fileName, const char *dirPath);
     int	initTstk23Values(const char *fileName, const char *dirPath);

     extern char EN_DATADIR[256];
}
#else 
     void readThermodynamicParameters(const char *userdatadir,bool userdatalogic, 
		                      int unamode, int rnamode, int t_mismatch);
     extern char EN_DATADIR[256];
#endif

#endif
