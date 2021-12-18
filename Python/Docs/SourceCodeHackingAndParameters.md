# Key constants, externed variables, and other constructions in the GTFold source code

## From ``commented_constants.txt``:

```cpp
typedef struct{
	int poppen[5];/*asymmetric internal loops
		From miscloop.dat file:
		the f(m) array (see Ninio for details)*/
	int maxpen; /* From miscloop.dat file:
		asymmetric internal loops: the ninio equation
		the maximum correction*/
	int eparam[11]; /* Amrita: I am not sure of what does this array contain at different values.*/
			/*They seem to be local values used in assignments
			Perhaps they should simply be local variables -Anderson*/
	int mult_const[3];/*Multiloop constants
		mult_const[0] = a, the penalty for starting a multiloop
		mult_const[1] = c, the free base penalty for a multiloop
		mult_const[2] = b, the helix penalty for a multiloop*/
	int dangle[4][4][4][2]; /* Dangling energies */
	int inter[31]; /* Size penalty for internal loops */
	int bulge[31]; /* Size penalty for bulges*/
	int hairpin[31]; /* Size penalty for hairpin loops */
	int stack[256]; /* Stacking energy for stack loops */
	int tstkh[256]; /* Terminal stacking energy for hairpin loops */
	int tstki[256]; /* Terminal stacking energy for internal loops */
	int tloop[MAX_T_LOOP + 1][2]; /*MAX_T_LOOP is a constants, should
	be the number of Tetraloops we have data for*/
	int num_of_t_loops; /*Should also be a local variable, used as a counter*/
	int iloop22[5][5][5][5][5][5][5][5]; /* 2*1 internal loops*/
	int iloop21[5][5][5][5][5][5][5]; /* 2*1 internal loops */
	int iloop11[5][5][5][5][5][5]; /*1*1 internal loops */
	int coax[6][6][6][6];/*Assumed to be coaxial stacking constants*/
	int tstackcoax[6][6][6][6];/*They are unused by gtfold as of Jan 27 2011*/
	int coax_stack[6][6][6][6];/*Unless functionality is added they should
				 probably be REMOVED*/
	int tstack[6][6][6][6];/*Unused in loader should probably be REMOVED*/
	int tstkm[6][6][6][6];/*Same as above*/

	int auend; /* For AU penalty */
	int gubonus; /*GGG hairpin bonus*/
	int cint; /* cint, cslope, c3 are used for poly C hairpin loops */
	int cslope;/*c hairpin slope*/
	int c3;/*CCC hairpin*/
	int efn2a; /*Obsoleted constants should be REMOVED*/
	int efn2b;
	int efn2c;
	int triloop[MAX_T_LOOP + 1][2];/*Unused in loader should be REMOVED*/
	int num_of_triloops; /*Unused in loader should be REMOVED*/
	int init;/*Intermolecular initiation free energy*/
	bool gail;/*Grossly Asymmetric Interior Loop Rule*/
	float prelog; /* Used for loops having size > 30 */
}thermo_struct;
```

## From ``global.h``:

```cpp
extern unsigned char *RNA;
extern int *structure;
extern int* constraints;

extern int g_nthreads;
extern int g_unamode;
extern int g_dangles;
extern int g_mismatch;
extern int g_verbose;
extern int g_prefilter_mode;
extern int g_prefilter1;
extern int g_prefilter2;
extern unsigned int chPairKey;

extern int SHAPE_ENABLED;//0 means false and 1 means true
extern int g_LIMIT_DISTANCE;
extern int g_contactDistance;
extern int g_bignumprecision;
```

## From ``energy.h``:

```cpp
extern int *V;
extern int *W;
extern int *VBI;
extern int *VM;
extern int **WM;
extern int **WMPrime;
extern int *indx;
extern int **PP;
```

## From ``options.h``

```cpp
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
```

## From ``shapereader.h``:

```cpp
extern double* SHAPEarray;
extern int* SHAPEenergies;
```

## From ``subopt_main.h``:

```cpp
extern char suboptFile[256];
extern int is_check_for_duplicates_enabled;
extern int UNIQUE_MULTILOOP_DECOMPOSITION;
extern int max_structure_count;
```

## From ``constraints.h``

```cpp
extern int* BP;
extern int** PBP;
extern int** FBP;
extern int* ind;

extern int nPBP;
extern int nFBP;
```

## From ``boltzmann_main.h``:

```cpp
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
```

