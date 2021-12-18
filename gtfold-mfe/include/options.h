#ifndef _OPTIONS_H_
#define _OPTIONS_H_

#include <stdlib.h>
#include <stdio.h>
#ifdef __cplusplus
     #include <string>
     #include <cstring>
     using namespace std;
#else
     #include <stdbool.h>
#endif

//extern bool ILSA;
//extern bool NOISOLATE;
//extern bool USERDATA;
//extern bool PARAMS;

extern int LIMIT_DISTANCE;
extern int BPP_ENABLED;
extern int SUBOPT_ENABLED;
extern int CONS_ENABLED;
extern int VERBOSE;
extern int SILENT;
extern int  SHAPE_ENABLED;
extern int PARAM_DIR;
extern int T_MISMATCH;
extern int UNAMODE;
extern int RNAMODE;
extern int DEBUG;

extern int PF_COUNT_MODE;
extern float suboptDelta;
extern int b_prefilter;
extern int prefilter1;
extern int prefilter2;
extern int dangles;
extern int LIMIT_DISTANCE;
extern int contactDistance;

/*
extern bool CALC_PART_FUNC;
extern bool RND_SAMPLE;
extern bool NO_DANGLE_MODE;
extern string seqfile;
extern string constraintsFile;
extern string shapeFile;
extern string outputDir;
extern string outputFile;
extern string bppOutFile;
extern string suboptFile;
extern string paramDir;
extern int nThreads;
extern int num_rnd;
*/

#endif
