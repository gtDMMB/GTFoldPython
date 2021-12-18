#ifndef _BPP_MAIN_H_
#define _BPP_MAIN_H_

extern int CALC_PART_FUNC;
extern int RND_SAMPLE;
extern int DUMP_CT_FILE;
extern int CALC_PF_DO;
extern int CALC_PF_DS;
extern int CALC_PF_D2;
extern int PF_D2_UP_APPROX_ENABLED;
extern int PF_PRINT_ARRAYS_ENABLED;
extern int ST_D2_ENABLE_COUNTS_PARALLELIZATION;
extern int ST_D2_ENABLE_ONE_SAMPLE_PARALLELIZATION;
extern int ST_D2_ENABLE_SCATTER_PLOT;
extern int ST_D2_ENABLE_UNIFORM_SAMPLE;
extern double ST_D2_UNIFORM_SAMPLE_ENERGY;
extern int PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER;
extern int ST_D2_ENABLE_CHECK_FRACTION;
extern int ST_D2_ENABLE_BPP_PROBABILITY;

extern char seqfile[256];
extern char outputPrefix[256];
extern char outputDir[256];
extern char outputFile[256];
extern char paramDir[256]; 
extern char bppOutFile[256];
extern char sampleOutFile[256];
extern char energyDecomposeOutFile[256];
extern char estimateBppOutputFile[256];
extern char scatterPlotOutputFile[256];
extern char pfArraysOutFile[256];
extern char ctFileDumpDir[256];
extern char stochastic_summery_file_name[256];
extern char shapeFile[256];

extern int num_rnd;
extern int print_energy_decompose;
extern double scaleFactor;

extern double t1;

#ifdef __cplusplus
extern "C" {
     void boltzmann_printRunConfiguration(const char *seq);
     void decideAutomaticallyForAdvancedDoubleSpecifier();
}
#else 
     void boltzmann_printRunConfiguration(const char *seq);
     void decideAutomaticallyForAdvancedDoubleSpecifier();
#endif

int boltzmann_main(int argc, char** argv);

#endif
