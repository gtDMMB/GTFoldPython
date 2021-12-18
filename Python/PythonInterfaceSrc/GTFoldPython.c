/* GTFoldPython.c : Main interface for the GTFold Python bindings;
 * Author: Maxie D. Schmidt (maxieds@gmail.com)
 * Created: 2019.12.09
 */

#include <assert.h>
#include <string.h>

#include "include/options.h"
#include "include/boltzmann_main.h"
#include "include/mfe_main.h"
#include "include/subopt_main.h"
#include "include/subopt_traceback_cinclude.h"
#include "include/global.h"
#include "include/utils.h"
#include "include/algorithms.h"
#include "include/loader.h"

#include "GTFoldPython.h"
#include "ErrorHandling.h"
#include "MFEStruct.h"
#include "Utils.h"
#include "StructureTypes.h"
#include "BoltzmannSampling.h"
#include "PartitionFunction.h"
#include "LoadThermoParams.h"
#include "GTFoldDataDir.c"

int  *CONFIG_QUIET = &SILENT;
int  *CONFIG_VERBOSE = &VERBOSE;
int  *CONFIG_DEBUGGING = &DEBUG;
FILE *CONFIG_STDMSGOUT = NULL;
int  *CONFIG_CONS_ENABLED = &CONS_ENABLED;
char GTFOLD_DATADIR[STR_BUFFER_SIZE] = { '\0' };
int  *DANGLE = &dangles;
int  *TMISMATCH = &T_MISMATCH;
int  *LIMITCDIST = &contactDistance;
int  *PREFILTER = &prefilter1;
int  WRITEAUXFILES = 0;
int  EXACTINTLOOP = 0;
char outputDir_cstr[STR_BUFFER_SIZE] = { '\0' };

PyObject * GTFoldPythonInit(void) {
     PyGILState_STATE pgState = PyGILState_Ensure();
     //if(!PyEval_Initialized()) {
     //	  Py_Initialize();
     //}
     if (!PyEval_ThreadsInitialized()) {
          PyEval_InitThreads(); 
     }
     PyGILState_Release(pgState);
     strcpy(GTFOLD_DATADIR, DEFAULT_GTFOLD_DATADIR);
     *CONFIG_QUIET = SILENT = 1;
     *CONFIG_VERBOSE = VERBOSE = 0;
     *CONFIG_DEBUGGING = DEBUG = 0;
     return ReturnPythonNone();
}

PyObject * GTFoldPythonConfig(int quietSpec, int verboseSpec, int debugSpec, const char *stdmsgoutSpec) {
     *CONFIG_QUIET = quietSpec;
     *CONFIG_VERBOSE = verboseSpec;
     *CONFIG_DEBUGGING = debugSpec;
     if(stdmsgoutSpec != NULL && !strcasecmp(stdmsgoutSpec, "stderr")) {
          CONFIG_STDMSGOUT = stderr;
     }
     else if(stdmsgoutSpec != NULL && !strcasecmp(stdmsgoutSpec, "stdout")) {
	  CONFIG_STDMSGOUT = stdout;
     }
     else if(stdmsgoutSpec != NULL) {
	  SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_PYARGS, "Invalid stderr|stdout specified");
     }
     if(*CONFIG_DEBUGGING) {
          fprintf(CONFIG_STDMSGOUT, "  >> CONFIG_QUIET = %d\n",     *CONFIG_QUIET);
	  fprintf(CONFIG_STDMSGOUT, "  >> CONFIG_VERBOSE = %d\n",   *CONFIG_VERBOSE);
	  fprintf(CONFIG_STDMSGOUT, "  >> CONFIG_DEBUGGING = %d\n", *CONFIG_DEBUGGING);
	  fprintf(CONFIG_STDMSGOUT, "  >> CONFIG_STDMSGOUT = %s\n", 
		  CONFIG_STDMSGOUT == stderr ? "stderr" : "stdout");
     }
     return ReturnPythonNone();
}

static GTFoldKeywordSpec_t GTFoldPythonConfigSettings_kwlist[] = {
     { 
	     "verbose", 
	     BOOL, 
	     "-v|--verbose",           
	     "     Run in verbose mode. (Includes confirmation of constraints satisfied.)",
	     &g_verbose, 
	     { &VERBOSE, NULL, NULL, NULL }, 
     }, 
     { 
	     "quiet",          
	     BOOL, 
	     "NONE", 
	     "     Run in quiet mode, printing nothing as status messages",
	     NULL, 
	     { &SILENT, NULL, NULL, NULL },  
     }, 
     { 
	     "debugging",      
	     BOOL, 
	     "NONE",                   
	     "     Run in debugging mode, printing extra verbose debugging messages", 
	     NULL, 
	     { &DEBUG, NULL, NULL, NULL },   
     }, 
     { 
	     "dangle",         
	     INT,  
	     "-d|--dangle INT",        
	     "     Restricts treatment of dangling energies, see below for details:\n" 
	     "       INT=0       Ignores dangling energies (mostly for debugging).\n"
             "       INT=1       Unpaired nucleotides adjacent to a branch in a multi-loop or external loop\n"
             "                   are allowed to dangle on at most one branch in that loop.\n"
	     "                   This is the default setting for gtmfe.\n"
             "       INT=2       Dangling energies are added for nucleotides on either side of each branch \n"
	     "                   in multi-loops and external loops.\n"
             "                   This is the default setting for gtboltzmann and gtsubopt.\n"
             "                   (This is the same as the -d2 setting in the RNAfold from the \n"
	     "                   Vienna RNA Package.)\n"
             "       other       INT is ignored and the default setting is used.",
	     NULL,
	     { &dangles, &g_dangles, NULL, NULL }, 
     },
     { 
	     "tmismatch",       
	     BOOL, 
	     "-m|--mismatch",         
	     "     Enable terminal mismatch calculations.",
	     NULL, 
	     { &T_MISMATCH, NULL, NULL, NULL },      
     }, 
     { 
	     "limitcdist",      
	     INT, 
	     "-l|--limitcd INT",      
	     "     Set a maximum base pair contact distance to INT. If no limit is given, \n"
	     "     base pairs can be over any distance.",
	     &LIMIT_DISTANCE, 
	     { &contactDistance, NULL, NULL, NULL }, 
     }, 
     { 
	     "prefilter",       
	     INT, 
	     "--prefilter INT",       
	     "     Prohibits any basepair which does not have appropriate neighboring nucleotides \n"
	     "     such that it could be part of a helix of length INT.", 
	     &b_prefilter, 
	     { &prefilter1, &prefilter2, NULL, NULL }, 
     }, 
     { 
	     "energydetail", 
	     BOOL, 
	     "-e|--energydetail", 
	     "     Write loop-by-loop energy decomposition of structures to output-prefix.energy. \n"
	     "     When using this function in combination with --sample, number of threads must be \n"
	     "     limited to one (-t 1).", 
	     NULL, 
	     { &print_energy_decompose, NULL, NULL, NULL }, 
     }, 
     { 
	     "estimatebpp", 
	     BOOL, 
	     "--estimatebpp",         
	     "     Write a CSV file containing, for each sampled base pair, that base pair and its \n"
	     "     frequency to output-prefix.sbpp.\n"
             "     (Only valid in combination with --sample.)", 
	     &ST_D2_ENABLE_SCATTER_PLOT,
	     { &ST_D2_ENABLE_BPP_PROBABILITY, NULL, NULL, NULL }, 
     }, 
     { 
	     "groupbyfreq", 
             BOOL, 
             "--groupbyfreq",         
	     "     Write a CSV file (output-prefix.frequency) containing, for each sampled structure, \n"
	     "     a line with the structure's probability under the Boltzmann Distribution followed by \n"
             "     the normalized frequency of that structure, where (normalized frequency) = \n"
             "     (structure frequency)/(number of structures sampled).\n"
             "     (Only valid in combination with --sample.)",
             NULL, 
	     { &ST_D2_ENABLE_SCATTER_PLOT, NULL, NULL, NULL }, 
     }, 
     { 
	     "outputprefix",       
	     STRING, 
	     "-o|--output NAME",      
	     "     Write output files with prefix given in NAME.", 
	     NULL, 
	     { outputPrefix, NULL, NULL, NULL }, 
     }, 
     { 
	     "writeauxfiles",    
	     BOOL, 
	     "NONE",                  
	     "     Whether to write the extra output CT and other aux files as GTFold does, \n"
             "     or just return them as Python objects?",
	     NULL, 
	     { &WRITEAUXFILES, NULL, NULL, NULL }, 
     }, 
     { 
	     "numthreads",      
	     INT, 
	     "-t|--threads INT",      
	     "     Limit number of threads used to INT. (Default is max threads available.)",
	     NULL, 
	     { &g_nthreads, &nThreads, NULL, NULL, NULL }, 
     }, 
     { 
	     "workdir",         
	     STRING, 
	     "-w|--workdir DIR",  
	     "     Path of directory where output files are to be written.",
	     NULL, 
	     { outputDir_cstr, NULL, NULL, NULL }, 
     }, 
     { 
	     "rnafold",         
	     BOOL, 
	     "--rnafold",             
	     "     Run as RNAfold default mode (Vienna RNA Package version 1.8.5).\n"
             "     (In this mode calls to -d, -p, -m and --prefilter will be ignored.)",
	     NULL, 
	     { &RNAMODE, NULL, NULL, NULL }, 
     }, 
     { 
	     "unafold", 
	     BOOL, 
	     "--unafold", 
	     "     Run as UNAfold default mode (version 3.8), subject to traceback implementation.\n"
             "     (In this mode calls to -d, -p, -m and --prefilter will be ignored.)",
	     NULL, 
	     { &UNAMODE, NULL, NULL, NULL },  
     }, 
     { 
	     "calcpartition",       
	     BOOL, 
	     "--partition", 
	     "     [DEVELOPER OPTION] Calculate the partition function (default is using d2 dangling mode).",
	     NULL, 
	     { &CALC_PART_FUNC, NULL, NULL, NULL }, 
     }, 
     { 
	     "printarrays",     
	     BOOL, 
	     "--printarrays", 
	     "     [DEVELOPER OPTION] Writes partition function arrays to \"prefix.pfarrays\".",
	     NULL, 
	     { &PF_PRINT_ARRAYS_ENABLED, NULL, NULL, NULL }, 
     }, 
     { 
	     "exactintloop",    
	     BOOL, 
	     "--exactintloop", 
	     "     [DEVELOPER OPTION] Includes structures with abitrarily many unpaired nucleotides in \n"
	     "     internal loops. Note: using this option increases the running time by a factor of N,\n" 
             "     where N is the base, or nucleotide, sequence length.",
	     NULL, 
	     { &EXACTINTLOOP, NULL, NULL, NULL }, 
     }, 
     { 
	     "checkfraction",   
	     BOOL, 
	     "--checkfraction",       
	     "     [DEVELOPER OPTION] While sampling structures, enable check that for each structure, \n"
	     "     the probability used ampling matches the probability of that structure according to the \n"
	     "     Boltzmann Distribution. Calculate the partition function using sfold reccurences and use \n"
	     "     them in traceback.", 
	     NULL, 
	     { &ST_D2_ENABLE_CHECK_FRACTION, NULL, NULL, NULL }, 
     }, 
     { 
	     "dS", 
             BOOL, 
             "-dS", 
	     "     [DEVELOPER OPTION] Calculate the partition function using sfold reccurences \n"
	     "     and use them in traceback.\n" 
             "     WARNING: this option does not pass --checkfraction test.", 
             NULL, 
	     { &CALC_PF_DS, NULL, NULL, NULL }, 
     }, 
     { 
	     "sampleenergy",    
	     DOUBLE, 
	     "--sampleenergy DOUBLE", 
	     "     [DEVELOPER OPTION] Writes only sampled structures with free energy equal to DOUBLE to \n"
	     "     file \"prefix.sample\". Number of threads must be limited to one (-t 1).\n" 
             "     (Only valid in combination with --sample.)",
	     &ST_D2_ENABLE_UNIFORM_SAMPLE, 
	     { &ST_D2_UNIFORM_SAMPLE_ENERGY, NULL, NULL, NULL }, 
     }, 
     { 
	     "scale",           
	     DOUBLE, 
	     "--scale DOUBLE",        
	     "     [DEVELOPER OPTION] Use scaling factor DOUBLE to approximate partition function, \n" 
             "     default value is 1.07 for sequences with more than 100 nt and zero for shorter sequences.",
	     NULL, 
	     { &scaleFactor, NULL, NULL, NULL }, 
     }, 
     { 
	     "parallelsample",  
	     BOOL, 
	     "--parallelsample",      
	     "     [DEVELOPER OPTION] Paralellizes the sampling of each individual structure.\n" 
             "     (Only valid in combination with --sample.)",
	     NULL, 
	     { &ST_D2_ENABLE_ONE_SAMPLE_PARALLELIZATION, NULL, NULL, NULL }, 
     }, 
     {
	     "countsparallel", 
	     BOOL, 
	     "--counts-parallel", 
	     "     [DEVELOPER OPTION] Hidden (undocumented) option.",
	     NULL, 
	     { &ST_D2_ENABLE_COUNTS_PARALLELIZATION, NULL, NULL, NULL }, 
     },
     { 
	     "separatectfiles", 
	     BOOL, 
	     "--separatectfiles",     
	     "     [DEVELOPER OPTION] Writes each sampled structure to a separate .ct file in the \n"           
             "     CT files output directory. (See --ctfilesdir option.)",
	     NULL, 
	     { &DUMP_CT_FILE, NULL, NULL, NULL }, 
     }, 
     { 
	     "ctfilesdir",      
	     STRING, 
	     "--ctfilesdir DIR]",     
	     "     [DEVELOPER OPTION] Writes any (separate) CT files in the DIR directory.\n" 
             "     Default directory is the working directory specified with -w.\n"
             "     (Only valid in combination with --sample.)",
	     NULL, 
	     { ctFileDumpDir, NULL, NULL, NULL }, 
     }, 
     { 
	     "summaryfile",     
	     STRING, 
	     "--summaryfile NAME",    
	     "     [DEVELOPER OPTION] Also writes a summary of the sampled structures to NAME in DIR.\n" 
             "     The default summary file name is \"stochaSampleSumary.txt\"\n"
	     "     (Only valid in combination with --sample.)",
	     NULL,
	     { stochastic_summery_file_name, NULL, NULL, NULL }, 
     }, 
     { 
	     "advancedouble",   
	     INT, 
	     "--advancedouble INT",   
	     "     [DEVELOPER OPTION] Directs Partition Function and Sampling calculation to use\n"
	     "     INT=1 native double, INT=2 BigNum, INT=3 hybrid, or INT=4 BigNumOptimized.\n"
             "     If this option not used then program will use the best setting depending on \n"
             "     sequence length.",
	     NULL, 
	     { &PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER, NULL, NULL, NULL }, 
     }, 
     { 
	     "bignumprecision", 
	     INT, 
	     "--bignumprecision INT", 
	     "     [DEVELOPER OPTION] Precision used in case BigNum, hybrid, and BigNumOptimized. \n"
	     "     Default value is 512. Minimum value is 64, and precision is ignored if using \n"
	     "     --advancedouble 1.",
	     NULL, 
	     { &g_bignumprecision, NULL, NULL, NULL }, 
     },
     {
	     "uniquemultiloop", 
	     BOOL, 
	     "--unique [0|1]", 
	     "     Set/Reset the UNIQUE_MULTILOOP_DECOMPOSITION routine which ensures\n"
	     "     no duplicate structures are explored.\n"
	     "     By default this option will be switched on for sequences less than\n"
	     "     2000 nt in length and switched off for longer sequences.",
	     NULL, 
	     { &UNIQUE_MULTILOOP_DECOMPOSITION, NULL, NULL, NULL }, 
     },
     {
	     "duplicatecheck", 
	     BOOL,
	     "--duplicatecheck [0|1]", 
	     "     Set/Reset the check if duplicate structure is encountered.\n"
	     "     This check requires that all structures explored be stored;\n"
	     "     this consumes more memory and increases running time,\n"
	     "     but is required if --unique [0] option is used.\n"
	     "     Default behavior will be OFF if unique option is switched ON and\n"
	     "     ON if unique option is OFF.",
	     NULL, 
	     { &is_check_for_duplicates_enabled, NULL, NULL, NULL }, 
     },
};

PyObject * GTFoldPythonConfigSettings(PyObject *kwargs) {
     if(!PyDict_Check(kwargs)) {
	  SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_PYARGS, NULL);
	  return ReturnPythonNone();
     }
     int numOptions = GetArrayLength(GTFoldPythonConfigSettings_kwlist);
     int truthValue = 0;
     PyGILState_STATE pgState = PyGILState_Ensure();
     for(int opt = 0; opt < numOptions; opt++) {
	  PyObject *kv = PyUnicode_FromString(GTFoldPythonConfigSettings_kwlist[opt].keywordID);
	  PyObject *kwdValue = PyDict_GetItem(kwargs, kv);
	  if(kwdValue == NULL) {
	       Py_DECREF(kv);
	       continue;
	  }
	  switch(GTFoldPythonConfigSettings_kwlist[opt].ctype) {
               case BOOL:
	       case INT:
	       case UINT: {
	            int intKwdValue = (int) PyLong_AsLong(kwdValue), varsToSetLength = 0;
                    GetArrayLengthByNonNULL(GTFoldPythonConfigSettings_kwlist[opt].dataRef, &varsToSetLength);
		    for(int i = 0; i < varsToSetLength; i++) {
                         int *varPtr = (int *) GTFoldPythonConfigSettings_kwlist[opt].dataRef[i];
			 *varPtr = intKwdValue;
		    }
		    bool truthVal = intKwdValue >= 0;
                    if(GTFoldPythonConfigSettings_kwlist[opt].boolTruthVar != NULL) 
		         *((int *) GTFoldPythonConfigSettings_kwlist[opt].boolTruthVar) = (int) truthVal;
                    break;
	       }
	       case FLOAT:
	            break;
	       case DOUBLE: {
                    int dblKwdValue = PyFloat_AsDouble(kwdValue), varsToSetLength = 0;
                    GetArrayLengthByNonNULL(GTFoldPythonConfigSettings_kwlist[opt].dataRef, &varsToSetLength);
		    for(int i = 0; i < varsToSetLength; i++) {
                         double *varPtr = (double *) GTFoldPythonConfigSettings_kwlist[opt].dataRef[i];
			 *varPtr = dblKwdValue;
		    }
		    bool truthVal = dblKwdValue >= 0.0;
		    if(GTFoldPythonConfigSettings_kwlist[opt].boolTruthVar != NULL) 
                         *((int *) GTFoldPythonConfigSettings_kwlist[opt].boolTruthVar) = (int) truthVal;
                    break;
	       }
	       case STRING: {
		    PyObject *pyStr = NULL;
		    if(PyUnicode_Check(kwdValue)) {
		         pyStr = PyUnicode_AsUTF8String(kwdValue);
		    }
		    else if(PyBytes_Check(kwdValue)) {
			 pyStr = PyObject_Bytes(kwdValue);
		    }
		    else {
			 SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_PYARGS, 
					  GTFoldPythonConfigSettings_kwlist[opt].keywordID);
			 break;
		    }
                    char *strKwdValue = PyBytes_AsString(pyStr), varsToSetLength = 0;
                    GetArrayLengthByNonNULL(GTFoldPythonConfigSettings_kwlist[opt].dataRef, &varsToSetLength);
		    for(int i = 0; i < varsToSetLength; i++) {
                         char *varPtr = (char *) GTFoldPythonConfigSettings_kwlist[opt].dataRef[i];
			 strcpy(varPtr, strKwdValue);
		    }
		    bool truthVal = true;
		    if(GTFoldPythonConfigSettings_kwlist[opt].boolTruthVar != NULL) 
                         *((int *) GTFoldPythonConfigSettings_kwlist[opt].boolTruthVar) = (int) truthVal;
                    Py_DECREF(pyStr);
		    break;
	       }
	       default:
	            break;

	  }
	  Py_DECREF(kv);
     }
     PyGILState_Release(pgState);
     if(strcmp(outputDir_cstr, "")) {
          strcat(outputDir_cstr, "/");
	  strcat(outputDir_cstr, outputDir);
	  strcpy(outputDir, outputDir_cstr);
     }
     if(CALC_PF_DS) dangles = -1;
     if(dangles == 0) CALC_PF_DO = true;
     else if(dangles == 2) CALC_PF_D2 = true;
     if(EXACTINTLOOP) PF_D2_UP_APPROX_ENABLED = false;
     if(PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER < 0 || PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER > 4) {
          SetLastErrorCode(GTFPYTHON_ERRNO_RUNCFG, 
			   "--advancedouble (PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER) out of range");
	  return ReturnPythonNone();
     }
     ConfigureOutputFileSettings();
     ValidateOptions();
     return ReturnPythonNone();
}

PyObject * PrintGTFoldRunConfiguration(int verboseParamPrint) {
     boltzmann_printRunConfiguration("<NONE>");
     if(VERBOSE || verboseParamPrint) {
          fprintf(CONFIG_STDMSGOUT, 
		  "Printing full listing of runtime configuration parameters:\n"
		  "  >> g_nthreads                               : %d\n"
		  "  >> g_unamode                                : %d\n"
		  "  >> g_dangles                                : %d\n"
		  "  >> g_mismatch                               : %d\n"
		  "  >> g_verbose                                : %d\n"
		  "  >> g_prefilter_mode                         : %d\n"
		  "  >> g_prefilter1                             : %d\n"
		  "  >> g_prefilter2                             : %d\n"
		  "  >> chPairKey                                : %02x\n"
		  "  >> SHAPE_ENABLED                            : %d\n"
		  "  >> g_LIMIT_DISTANCE                         : %d\n"
		  "  >> g_contactDistance                        : %d\n"
		  "  >> g_bignumprecision                        : %d\n"
		  "  >> LIMIT_DISTANCE                           : %d\n"
		  "  >> BPP_ENABLED                              : %d\n"
		  "  >> SUBOPT_ENABLED                           : %d\n"
		  "  >> CONS_ENABLED                             : %d\n"
		  "  >> VERBOSE                                  : %d\n"
		  "  >> SILENT                                   : %d\n"
		  "  >> PARAM_DIR                                : %d\n"
		  "  >> T_MISMATCH                               : %d\n"
		  "  >> UNAMODE                                  : %d\n"
		  "  >> RNAMODE                                  : %d\n"
		  "  >> DEBUG                                    : %d\n"
		  "  >> PF_COUNT_MODE                            : %d\n"
		  "  >> suboptDelta                              : %g\n"
		  "  >> b_prefilter                              : %d\n"
		  "  >> prefilter1                               : %d\n"
		  "  >> prefilter2                               : %d\n"
		  "  >> dangles                                  : %d\n"
		  "  >> LIMIT_DISTANCE                           : %d\n"
		  "  >> contactDistance                          : %d\n"
		  "  >> suboptFile                               : %s\n"
		  "  >> is_check_for_duplicates_enabled          : %d\n"
		  "  >> UNIQUE_MULTILOOP_DECOMPOSITION           : %d\n"
		  "  >> max_structure_count                      : %d\n"
		  "  >> CALC_PART_FUNC                           : %d\n"
		  "  >> RND_SAMPLE                               : %d\n"
		  "  >> DUMP_CT_FILE                             : %d\n"
		  "  >> CALC_PF_DO                               : %d\n"
		  "  >> CALC_PF_DS                               : %d\n"
		  "  >> CALC_PF_D2                               : %d\n"
		  "  >> PF_D2_UP_APPROX_ENABLED                  : %d\n"
		  "  >> PF_PRINT_ARRAYS_ENABLED                  : %d\n"
		  "  >> ST_D2_ENABLE_COUNTS_PARALLELIZATION      : %d\n"
		  "  >> ST_D2_ENABLE_ONE_SAMPLE_PARALLELIZATION  : %d\n"
		  "  >> ST_D2_ENABLE_SCATTER_PLOT                : %d\n"
		  "  >> ST_D2_ENABLE_UNIFORM_SAMPLE              : %d\n"
		  "  >> ST_D2_UNIFORM_SAMPLE_ENERGY              : %g\n"
		  "  >> PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER       : %d\n"
		  "  >> ST_D2_ENABLE_CHECK_FRACTION              : %d\n"
		  "  >> ST_D2_ENABLE_BPP_PROBABILITY             : %d\n"
		  "  >> seqfile                                  : %s\n"
		  "  >> outputPrefix                             : %s\n"
		  "  >> outputDir                                : %s\n"
		  "  >> outputFile                               : %s\n"
		  "  >> paramDir                                 : %s\n"
		  "  >> bppOutFile                               : %s\n"
		  "  >> sampleOutFile                            : %s\n"
		  "  >> energyDecomposeOutFile                   : %s\n"
		  "  >> estimateBppOutputFile                    : %s\n"
		  "  >> scatterPlotOutputFile                    : %s\n"
		  "  >> pfArraysOutFile                          : %s\n"
		  "  >> ctFileDumpDir                            : %s\n"
		  "  >> stochastic_summery_file_name             : %s\n"
                  "  >> shapeFile                                : %s\n"
		  "  >> num_rnd                                  : %d\n"
		  "  >> print_energy_decompose                   : %d\n"
		  "  >> scaleFactor                              : %g\n"
		  "  >> t1                                       : %g\n\n",
		 g_nthreads, g_unamode, g_dangles, g_mismatch, g_verbose, g_prefilter_mode, 
		 g_prefilter1, g_prefilter2, chPairKey, SHAPE_ENABLED, g_LIMIT_DISTANCE, 
		 g_contactDistance, g_bignumprecision, LIMIT_DISTANCE, BPP_ENABLED, 
		 SUBOPT_ENABLED, CONS_ENABLED, VERBOSE, SILENT,  PARAM_DIR, 
		 T_MISMATCH, UNAMODE, RNAMODE, DEBUG, PF_COUNT_MODE, suboptDelta, 
		 b_prefilter, prefilter1, prefilter2, dangles, LIMIT_DISTANCE, 
		 contactDistance, suboptFile, is_check_for_duplicates_enabled, 
		 UNIQUE_MULTILOOP_DECOMPOSITION, max_structure_count, 
		 CALC_PART_FUNC, RND_SAMPLE, DUMP_CT_FILE, CALC_PF_DO, CALC_PF_DS, 
		 CALC_PF_D2, PF_D2_UP_APPROX_ENABLED, PF_PRINT_ARRAYS_ENABLED, 
		 ST_D2_ENABLE_COUNTS_PARALLELIZATION, ST_D2_ENABLE_ONE_SAMPLE_PARALLELIZATION, 
		 ST_D2_ENABLE_SCATTER_PLOT, ST_D2_ENABLE_UNIFORM_SAMPLE, 
		 ST_D2_UNIFORM_SAMPLE_ENERGY, PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER, 
		 ST_D2_ENABLE_CHECK_FRACTION, ST_D2_ENABLE_BPP_PROBABILITY, 
		 seqfile, outputPrefix, outputDir, outputFile, paramDir, bppOutFile, 
		 sampleOutFile, energyDecomposeOutFile, estimateBppOutputFile, 
		 scatterPlotOutputFile, pfArraysOutFile, ctFileDumpDir, 
		 stochastic_summery_file_name, shapeFile, num_rnd, 
		 print_energy_decompose, scaleFactor, t1);
     }
     return ReturnPythonNone();
}

PyObject * SetGTFoldDataDirectory(const char *dataDir, int chLength) {
     if(dataDir == NULL || chLength < 0) {
	  SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CARGS, NULL);
	  return ReturnPythonNone();
     }
     else if(chLength >= STR_BUFFER_SIZE) {
	  SetLastErrorCode(GTFPYTHON_ERRNO_STRLEN, NULL);
     }
     else if(!IsDirectory(dataDir)) {
          PyGILState_STATE pgState = PyGILState_Ensure();
	  PyErr_SetString(PyExc_NotADirectoryError, dataDir);
	  PyGILState_Release(pgState);
     }
     else {
          strncpy(GTFOLD_DATADIR, dataDir, STR_BUFFER_SIZE - 1);
          GTFOLD_DATADIR[STR_BUFFER_SIZE - 1] = '\0';
          strcpy(EN_DATADIR, GTFOLD_DATADIR);
	  if(*CONFIG_DEBUGGING) {
               fprintf(CONFIG_STDMSGOUT, " ** Changed GTFold data directory to \"%s\" ...\n", GTFOLD_DATADIR);
          }
     }
     return ReturnPythonNone();
}

PyObject * SetThermodynamicParameters(const char *energyModelSpec, 
		                      const char *thermoParamsDir) {
     if(energyModelSpec == NULL) {
          SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CARGS, NULL);
	  return ReturnPythonNone();
     }
     if(SetThermodynamicMode(energyModelSpec) != GTFPYTHON_ERRNO_OK) {
          return ReturnPythonNone();
     }
     if(thermoParamsDir != NULL) {
	  return SetGTFoldDataDirectory(thermoParamsDir, strlen(thermoParamsDir));
     }
     return ReturnPythonNone();
}

PyObject * SetDangleParameter(int dangle) {
     if(dangle < 0 || dangle > 2) {
          SetLastErrorCode(GTFPYTHON_ERRNO_DANGLE, NULL);
	  return ReturnPythonNone();
     }
     DANGLE = dangle;
     dangles = dangle;
     return ReturnPythonNone();
}

PyObject * SetTerminalMismatch(int enable) {
     T_MISMATCH = enable != 0;
     return ReturnPythonNone();
}

PyObject * SetLimitContactDistance(int lcDist) {
     if(lcDist < 0) {
          //SetLastErrorCode(GTFPYTHON_ERRNO_INVDIST, NULL);
	  return ReturnPythonNone();
     }
     contactDistance = lcDist;
     LIMIT_DISTANCE = 1;
     return ReturnPythonNone();
}

PyObject * SetPrefilterParameter(int prefilter) {
     if(prefilter <= 0) {
          //SetLastErrorCode(GTFPYTHON_ERRNO_INVPARAM, NULL);
	  return ReturnPythonNone();
     }
     prefilter1 = prefilter2 = prefilter;
     b_prefilter = 1;
     return ReturnPythonNone();
}

PyObject * GetPFuncCount(const char *baseSeq, ConsListCType_t consList, int consLength) {
     if(baseSeq == NULL || consList == NULL || consLength < 0) {
          SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CARGS, NULL);
	  return ReturnPythonNone();
     }
     PF_COUNT_MODE = 1;
     CALC_PART_FUNC = 1;
     MFEStructRuntimeArgs_t rtArgs;
     InitMFEStructRuntimeArgs(&rtArgs);
     rtArgs.baseSeq = baseSeq;
     rtArgs.numBases = strlen(baseSeq);
     if(ParseGetMFEStructureArgs(consList, consLength, &rtArgs) != GTFPYTHON_ERRNO_OK) {
          FreeMFEStructRuntimeArgs(&rtArgs);
	  return ReturnPythonNone();
     }
     if(!ConfigureBoltzmannMainRuntimeParameters(&rtArgs)) {
          FreeMFEStructRuntimeArgs(&rtArgs);
	  FreeGTFoldMFEStructureData(rtArgs.numBases);
	  return ReturnPythonNone();
     }
     char *pfuncValue = "NaN";
     if (CALC_PART_FUNC == true && CALC_PF_DS == true) {
          pfuncValue = ComputeDsPartitionFunction(&rtArgs);
     }
     else if (CALC_PART_FUNC == true && CALC_PF_D2 == true) {
          pfuncValue = ComputeD2PartitionFunction(PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER, &rtArgs);
     }
     else if (CALC_PART_FUNC == true && CALC_PF_DO == true) {
          pfuncValue = ComputeDsPartitionFunction(&rtArgs);
     }
     else {
          SetLastErrorCode(GTFPYTHON_ERRNO_INVBOLTZPARAMS, "Invalid partition function count.");
          FreeMFEStructRuntimeArgs(&rtArgs);
	  FreeGTFoldMFEStructureData(rtArgs.numBases);
	  return ReturnPythonNone();
     }
     PyGILState_STATE pgState = PyGILState_Ensure();
     PyObject *pfuncDbl = PyUnicode_FromString(pfuncValue);
     Py_INCREF(pfuncDbl);
     Free(pfuncValue);
     PyGILState_Release(pgState);
     FreeMFEStructRuntimeArgs(&rtArgs);
     FreeGTFoldMFEStructureData(rtArgs.numBases);
     return pfuncDbl;
}

PyObject * GetPFuncCountSHAPE(const char *baseSeq, SHAPEConstraint_t *scList, int sconsLength) {
     if(baseSeq == NULL || scList == NULL || sconsLength < 0) {
          SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CARGS, NULL);
	  return ReturnPythonNone();
     }
     PF_COUNT_MODE = 1;
     CALC_PART_FUNC = 1;
     MFEStructRuntimeArgs_t rtArgs;
     InitMFEStructRuntimeArgs(&rtArgs);
     rtArgs.baseSeq = baseSeq;
     rtArgs.numBases = strlen(baseSeq);
     if(ParseGetMFEStructureSHAPEArgs(scList, sconsLength, &rtArgs) != GTFPYTHON_ERRNO_OK) {
          FreeMFEStructRuntimeArgs(&rtArgs);
	  return ReturnPythonNone();
     }
     if(!ConfigureBoltzmannMainRuntimeParameters(&rtArgs)) {
          FreeMFEStructRuntimeArgs(&rtArgs);
	  FreeGTFoldMFEStructureData(rtArgs.numBases);
	  return ReturnPythonNone();
     }
     char *pfuncValue = "NaN";
     if (CALC_PART_FUNC == true && CALC_PF_DS == true) {
          pfuncValue = ComputeDsPartitionFunction(&rtArgs);
     }
     else if (CALC_PART_FUNC == true && CALC_PF_D2 == true) {
          pfuncValue = ComputeD2PartitionFunction(PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER, &rtArgs);
     }
     else if (CALC_PART_FUNC == true && CALC_PF_DO == true) {
          pfuncValue = ComputeDsPartitionFunction(&rtArgs);
     }
     else {
          SetLastErrorCode(GTFPYTHON_ERRNO_INVBOLTZPARAMS, "Invalid partition function count.");
          FreeMFEStructRuntimeArgs(&rtArgs);
	  FreeGTFoldMFEStructureData(rtArgs.numBases);
	  return ReturnPythonNone();
     }
     PyGILState_STATE pgState = PyGILState_Ensure();
     PyObject *pfuncDbl = PyUnicode_FromString(pfuncValue);
     Py_INCREF(pfuncDbl);
     Free(pfuncValue);
     PyGILState_Release(pgState);
     FreeMFEStructRuntimeArgs(&rtArgs);
     FreeGTFoldMFEStructureData(rtArgs.numBases);
     return pfuncDbl;
}

PyObject * ComputeBPP(const char *baseSeq, ConsListCType_t consList, int consLength) {
     if(baseSeq == NULL || consList == NULL || consLength < 0) {
          SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CARGS, NULL);
	  return ReturnPythonNone();
     }
     CALC_PART_FUNC = 0;
     BPP_ENABLED = 1;
     MFEStructRuntimeArgs_t rtArgs;
     InitMFEStructRuntimeArgs(&rtArgs);
     rtArgs.baseSeq = baseSeq;
     rtArgs.numBases = strlen(baseSeq);
     if(ParseGetMFEStructureArgs(consList, consLength, &rtArgs) != GTFPYTHON_ERRNO_OK) {
          FreeMFEStructRuntimeArgs(&rtArgs);
	  return ReturnPythonNone();
     }
     if(!ConfigureBoltzmannMainRuntimeParameters(&rtArgs)) {
          FreeMFEStructRuntimeArgs(&rtArgs);
	  FreeGTFoldMFEStructureData(rtArgs.numBases);
	  return ReturnPythonNone();
     }
     PyObject *pyObjReturn = HandleBPP(&rtArgs); // ??? : Release/Acquire the GIL? 
     FreeMFEStructRuntimeArgs(&rtArgs);
     FreeGTFoldMFEStructureData(rtArgs.numBases);
     return pyObjReturn;
}

PyObject * ComputeBPPSHAPE(const char *baseSeq, SHAPEConstraint_t *scList, int sconsLength) {
     if(baseSeq == NULL || scList == NULL || sconsLength < 0) {
          SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CARGS, NULL);
	  return ReturnPythonNone();
     }
     CALC_PART_FUNC = 0;
     BPP_ENABLED = 1;
     MFEStructRuntimeArgs_t rtArgs;
     InitMFEStructRuntimeArgs(&rtArgs);
     rtArgs.baseSeq = baseSeq;
     rtArgs.numBases = strlen(baseSeq);
     if(ParseGetMFEStructureSHAPEArgs(scList, sconsLength, &rtArgs) != GTFPYTHON_ERRNO_OK) {
          FreeMFEStructRuntimeArgs(&rtArgs);
	  return ReturnPythonNone();
     }
     if(!ConfigureBoltzmannMainRuntimeParameters(&rtArgs)) {
          FreeMFEStructRuntimeArgs(&rtArgs);
	  FreeGTFoldMFEStructureData(rtArgs.numBases);
	  return ReturnPythonNone();
     }
     PyObject *pyObjReturn = HandleBPP(&rtArgs); // ??? : Release/Acquire the GIL?
     FreeMFEStructRuntimeArgs(&rtArgs);
     FreeGTFoldMFEStructureData(rtArgs.numBases);
     return pyObjReturn;
}

PyObject * GetMFEStructure(const char *baseSeq, ConsListCType_t consList, int consLength) {
     if(baseSeq == NULL || consList == NULL || consLength < 0) {
          SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CARGS, NULL);
	  return ReturnPythonNone();
     }
     MFEStructRuntimeArgs_t rtArgs;
     InitMFEStructRuntimeArgs(&rtArgs);
     rtArgs.baseSeq = baseSeq;
     rtArgs.numBases = strlen(baseSeq);
     if(ParseGetMFEStructureArgs(consList, consLength, &rtArgs) != GTFPYTHON_ERRNO_OK) {
          FreeMFEStructRuntimeArgs(&rtArgs);
	  return ReturnPythonNone();
     }
     if(InitGTFoldMFEStructureData(&rtArgs) != GTFPYTHON_ERRNO_OK) {
          FreeMFEStructRuntimeArgs(&rtArgs);
	  return ReturnPythonNone();
     }
     if(*CONFIG_DEBUGGING) {
          fprintf(CONFIG_STDMSGOUT, "BASE SEQUENCE: [#%d] %s\n", rtArgs.numBases, rtArgs.baseSeq);
          fprintf(CONFIG_STDMSGOUT, "CONSTRAINTS:\n");
          PrintGTFoldConstraints(rtArgs.mfeConstraints, rtArgs.numConstraints);
     }
     double mfe = ComputeMFEStructure(&rtArgs);
     if(WRITEAUXFILES) {
          ConfigureOutputFileSettings();
          save_ct_file(outputFile, baseSeq, mfe);
     }
     char *dbMFEStruct = ComputeDOTStructureResult(rtArgs.numBases);
     PyObject *mfeTupleRes = PrepareMFETupleResult(mfe, dbMFEStruct); // ??? : Release/Acquire the GIL?
     Free(dbMFEStruct);
     FreeMFEStructRuntimeArgs(&rtArgs);
     FreeGTFoldMFEStructureData(rtArgs.numBases);
     if(mfeTupleRes == NULL) {
          return ReturnPythonNone();
     }
     return mfeTupleRes;
}

PyObject * GetMFEStructureSHAPE(const char *baseSeq, SHAPEConstraint_t *scList, int scLength) {
     if(baseSeq == NULL || scList == NULL || scLength < 0) {
          SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CARGS, NULL);
	  return ReturnPythonNone();
     }
     MFEStructRuntimeArgs_t rtArgs;
     InitMFEStructRuntimeArgs(&rtArgs);
     rtArgs.baseSeq = baseSeq;
     rtArgs.numBases = strlen(baseSeq);
     if(ParseGetMFEStructureSHAPEArgs(scList, scLength, &rtArgs) != GTFPYTHON_ERRNO_OK) {
          FreeMFEStructRuntimeArgs(&rtArgs);
	  return ReturnPythonNone();
     }
     if(InitGTFoldMFEStructureData(&rtArgs) != GTFPYTHON_ERRNO_OK) {
          FreeMFEStructRuntimeArgs(&rtArgs);
	  return ReturnPythonNone();
     }
     if(*CONFIG_DEBUGGING) {
          fprintf(CONFIG_STDMSGOUT, "BASE SEQUENCE: [#%d] %s\n", rtArgs.numBases, rtArgs.baseSeq);
          fprintf(CONFIG_STDMSGOUT, "CONSTRAINTS:\n");
          PrintGTFoldSHAPEConstraints(rtArgs.mfeSHAPEConstraints, rtArgs.numSHAPEConstraints);
     }
     double mfe = ComputeMFEStructure(&rtArgs);
     if(WRITEAUXFILES) {
          ConfigureOutputFileSettings();
          save_ct_file(outputFile, baseSeq, mfe);
     }
     char *dbMFEStruct = ComputeDOTStructureResult(rtArgs.numBases);
     PyObject *mfeTupleRes = PrepareMFETupleResult(mfe, dbMFEStruct); // ??? : Release/Acquire the GIL?
     Free(dbMFEStruct);
     FreeMFEStructRuntimeArgs(&rtArgs);
     FreeGTFoldMFEStructureData(rtArgs.numBases);
     if(mfeTupleRes == NULL) {
          return ReturnPythonNone();
     }
     return mfeTupleRes;
}

PyObject * GetSuboptStructuresWithinRange(const char *baseSeq, double delta) {
     if(baseSeq == NULL) {
          SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CARGS, NULL);
	  return ReturnPythonNone();
     }
     SUBOPT_ENABLED = 1;
     suboptDelta = delta;
     ValidateOptions();
     int baseSeqLength = strlen(baseSeq);
     if(UNIQUE_MULTILOOP_DECOMPOSITION == -1){
          if(baseSeqLength <= 2000){
               UNIQUE_MULTILOOP_DECOMPOSITION = 1;
          }
          else{
               UNIQUE_MULTILOOP_DECOMPOSITION = 0;
          }
     }
     if(is_check_for_duplicates_enabled == -1){
          if(baseSeqLength <= 2000){
               is_check_for_duplicates_enabled = 0;
          }
          if(UNIQUE_MULTILOOP_DECOMPOSITION == 0){
               is_check_for_duplicates_enabled = 1;
          }
     }
     MFEStructRuntimeArgs_t rtArgs;
     InitMFEStructRuntimeArgs(&rtArgs);
     rtArgs.baseSeq = baseSeq;
     rtArgs.numBases = strlen(baseSeq);
     if(InitGTFoldMFEStructureData(&rtArgs) != GTFPYTHON_ERRNO_OK) { // in place of: init_fold(baseSeq);
          FreeMFEStructRuntimeArgs(&rtArgs);
          return ReturnPythonNone();
     } 
     g_dangles = 2;
     //readThermodynamicParameters(GTFOLD_DATADIR, 1, 0, 1, 0);
     if(LoadThermodynamicParameters(ACTIVE_THERMO_PARAMS, GTFOLD_DATADIR) != GTFPYTHON_ERRNO_OK) {
          return ReturnPythonNone();
     }
     int energy = calculate(baseSeqLength);
     if(WRITEAUXFILES) {
          ConfigureOutputFileSettings();
	  write_header_subopt_file(suboptFile, baseSeq, energy);
     }
     double t1 = get_seconds();
     int ssArrCount = 0;
     errno = EXIT_SUCCESS;
     ss_ctype_t *suboptDataArr = SuboptTraceback(baseSeqLength, 100.0 * suboptDelta, suboptFile, WRITEAUXFILES, 
		                                 is_check_for_duplicates_enabled, max_structure_count, 
						 &ssArrCount);
     t1 = get_seconds() - t1;
     if(errno == EDOM) {
          SetLastErrorCode(GTFPYTHON_ERRNO_SUBOPT, "Duplicate structure calculated!");
     }
     if(!SILENT) {
          fprintf(CONFIG_STDMSGOUT, "Subopt traceback running time: %9.6f seconds\n", t1);
	  if(WRITEAUXFILES) 
               fprintf(CONFIG_STDMSGOUT, "Subopt structures saved in %s\n", suboptFile);
	  fprintf(CONFIG_STDMSGOUT, "\n");
     }
     if(suboptDataArr == NULL) {
          SetLastErrorCode(GTFPYTHON_ERRNO_SUBOPT, NULL);
	  free_fold(baseSeqLength);
	  return ReturnPythonNone();
     }
     // ??? : Release/Acquire the GIL?
     PyObject *pyStructsList = StructureListToPythonTupleList((StructData_t *) suboptDataArr, ssArrCount);
     FreeSSMapStructure(suboptDataArr, ssArrCount);
     FreeMFEStructRuntimeArgs(&rtArgs);
     FreeGTFoldMFEStructureData(rtArgs.numBases);
     return pyStructsList;
}

PyObject * SampleBoltzmannStructures(const char *baseSeq, ConsListCType_t consList, 
		                     int consLength, int N) {
     if(baseSeq == NULL || consList == NULL || consLength < 0 || N <= 0) {
          SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CARGS, NULL);
	  return ReturnPythonNone();
     }
     CALC_PART_FUNC = 0;
     num_rnd = N;
     MFEStructRuntimeArgs_t rtArgs;
     InitMFEStructRuntimeArgs(&rtArgs);
     rtArgs.baseSeq = baseSeq;
     rtArgs.numBases = strlen(baseSeq);
     if(ParseGetMFEStructureArgs(consList, consLength, &rtArgs) != GTFPYTHON_ERRNO_OK) {
          FreeMFEStructRuntimeArgs(&rtArgs);
	  return ReturnPythonNone();
     }
     if(!ConfigureBoltzmannMainRuntimeParameters(&rtArgs)) {
          FreeMFEStructRuntimeArgs(&rtArgs);
	  FreeGTFoldMFEStructureData(rtArgs.numBases);
	  return ReturnPythonNone();
     }
     PyObject *sampleStructsListObj = NULL;
     if(CALC_PF_D2) {
          sampleStructsListObj = HandleD2Sample(PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER, N, &rtArgs);
     }
     else {
          sampleStructsListObj = HandleDsSample(N, &rtArgs);
     }
     FreeMFEStructRuntimeArgs(&rtArgs);
     FreeGTFoldMFEStructureData(rtArgs.numBases);
     return sampleStructsListObj;
}

PyObject * SampleBoltzmannStructuresSHAPE(const char *baseSeq, SHAPEConstraint_t *scList, 
		                          int scLength, int N) {
     if(baseSeq == NULL || scList == NULL || scLength < 0 || N <= 0) {
          SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CARGS, NULL);
	  return ReturnPythonNone();
     }
     CALC_PART_FUNC = 0;
     num_rnd = N;
     MFEStructRuntimeArgs_t rtArgs;
     InitMFEStructRuntimeArgs(&rtArgs);
     rtArgs.baseSeq = baseSeq;
     rtArgs.numBases = strlen(baseSeq);
     if(ParseGetMFEStructureSHAPEArgs(scList, scLength, &rtArgs) != GTFPYTHON_ERRNO_OK) {
          FreeMFEStructRuntimeArgs(&rtArgs);
	  return ReturnPythonNone();
     }
     if(!ConfigureBoltzmannMainRuntimeParameters(&rtArgs)) {
          FreeMFEStructRuntimeArgs(&rtArgs);
	  FreeGTFoldMFEStructureData(rtArgs.numBases);
	  return ReturnPythonNone();
     }
     PyObject *sampleStructsListObj = NULL;
     if(CALC_PF_D2) {
          sampleStructsListObj = HandleD2Sample(PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER, N, &rtArgs);
     }
     else {
          sampleStructsListObj = HandleDsSample(N, &rtArgs);
     }
     FreeMFEStructRuntimeArgs(&rtArgs);
     FreeGTFoldMFEStructureData(rtArgs.numBases);
     return sampleStructsListObj;
}

const PyMethodDef GTFoldPython_Methods[] = {
     { 
	     "Init",   
	     GTFoldPythonInit,   
	     METH_NOARGS,            
	     "Description: C source initializations that need to be done once up front\n"
	     "Python Args: Init(reinitLibrary = False)"
     }, 
     { 
	     "Config", 
	     GTFoldPythonConfig, 
	     METH_COEXIST, 
	     "Description: Setup the GTFoldPython library local configuration\n"
	     "Python Args: Config(quiet=0, verbose=0, debugging=0, stdmsgout=\"stderr\")\n"
	     "             - quiet 0|1                   : turn on/off printing of messages\n"
             "             - verbose 0|1                 : turn on/off printing of verbose messages\n"
             "             - debugging 0|1               : turn on/off printing of debugging messages\n"
             "             - stdmsgout \"stderr\"|\"stdout\" : sets default out stream to print messages\n"
	     "See Also:    ConfigExtraSettings(**kwargs)" 
     }, 
     {
	     "ConfigExtraSettings", 
	     GTFoldPythonConfigSettings, 
	     METH_COEXIST, 
	     "Description: Configure various settings and hidden GTFold developer settings\n"
	     "Python Args: ConfigExtraSettings(**kwargs)\n"
	     "See Also:    The description of all available settings (help topic \"config\")\n"
	     "Example:     (Note that all of the following dict keys do not need to be set at once)\n"
	     "$ ipython3\n"
	     ">>> import GTFoldPythonImportAll\n"
             ">>> cfgSettings = {\n"
             "         verbose          : False,\n"
             "         quiet            : False,\n"
             "         debugging        : False,\n"
             "         dangle           : 0,\n"
             "         tmismatch        : True,\n"
             "         limitcdist       : -1,\n"
             "         prefilter        : -1,\n"
             "         energydetail     : True,\n"
             "         estimatebpp      : True,\n"
             "         groupbyfreq      : True,\n"
             "         outputprefix     : \"output_prefix_\",\n"
             "         writeauxfiles    : True,\n"
             "         numthreads       : 4,\n"
             "         workdir          : \"./output\",\n"
             "         rnafold          : True,\n"
             "         unafold          : False,\n"
             "         calcpartition    : True,\n"
             "         printarrays      : True,\n"
             "         exactintloop     : True,\n"
             "         checkfraction    : False,\n"
             "         dS               : False,\n"
             "         sampleenergy     : 10.0,\n"
             "         scale            : 0.75,\n"
             "         parallelsample   : False,\n"
             "         countsparallel   : False,\n"
             "         separatectfiles  : True,\n"
             "         ctfilesdir       : \"./ctfiles\",\n"
             "         summaryfile      : True,\n"
             "         advancedouble    : 1,\n"
             "         bignumprecision  : 512,\n"
             "         uniquemultiloop  : True,\n"
             "         duplicatecheck   : True\n"
             "};\n"
             ">>> GTFP.ConfigExtraSettings(**cfgSettings)\n"
	     ">>> GTFP.PrintRunConfiguration()\n"
     },
     {
	     "PrintRunConfiguration", 
	     PrintGTFoldRunConfiguration, 
	     METH_NOARGS, 
	     "Description: Print a summary of all the relevant internal GTFold settings\n"
	     "Python Args:  PrintRunConfiguration(verbosePrint = True)"
     },
     { 
	     "SetGTFoldDataDirectory", 
	     SetGTFoldDataDirectory, 
	     METH_COEXIST,  
	     "Description: Set the thermodynamic parameters DAT files location\n"
	     "Python Args: SetGTFoldDataDirectory(relDirPath)\n"
	     "             -relDirPath The input path (unless it is absolute) is resolved relative\n"
	     "                         to the location of the calling script\n"
	     "See Also:    The directory \"Python/Testing/ExtraGTFoldData/*\" for valid directories\n"
	     "             (or specify your own custom set of parameters)"
     },
     {
	     "SetThermodynamicParameters", 
	     SetThermodynamicParameters, 
	     METH_COEXIST, 
	     "Description: Set the energy model (aka thermodynamic parameters data set) used\n"
	     "             in the GTFold calculations\n"
	     "Python Args: SetThermodynamicParameters(emodelSpec, dataDir = None)\n"
	     "Currently supported values of the energy model string:\n"
	     "   GTFold, RNAFold, UNAFold, Turner99, Turner04, default\n"
	     "Future energy models we will support:\n"
	     "   DP03, DP09, CC06, CC09; and \"custom\" (see below)\n"
	     "How to specify a custom (modified, e.g., with `GTModify`) energy model data set:\n"
	     "   Let's suppose that you have modified the *.DAT files from one of the stock energy\n"
	     "   model data sets using some algorithm or program like `GTModify`. This means that you\n"
	     "   should have a consistent set of files which are named like the following:\n"
	     "       * miscloop.DAT\n"
	     "       * dangle.DAT\n"
	     "       * stack.DAT\n"
	     "       * loop.DAT, tloop.DAT\n"
	     "       * tstackh.DAT, tstacki.DAT, tstackm.DAT, tstacke.DAT\n"
	     "       * int21.DAT, int22.DAT, int11.DAT\n"
	     "   Let's say that this collection of modified files is located in the directory\n"
	     "   ${MODDATADIR}. Then you can have GTFold perform its computations using the new\n"
	     "   energy model you have created by specifying the data directory as ${MODDATADIR}\n"
	     "   and the energy model name spec as \"default\". In Python3, this is done as follows:\n"
	     "     >>> from GTFoldPythonImportAll import *\n"
	     "     >>> GTFP.SetThermodynamicParameters(THERMO_PARAMS_DEFAULT, \"${MODDATADIR}\", True)\n"
	     "   Note that there is currently no way to specify a custom energy model data set with\n"
	     "   data files named anything but the default names given above. (Request this feature as\n"
	     "   a new issue if this lack of a non-default naming convention bothers you, or otherwise\n"
	     "   impedes progress on your application using our library!)"
     },
     { 
	     "SetDangleParameter",     
	     SetDangleParameter, 
	     METH_COEXIST, 
	     "Description: Set the dangle parameter (0|1|2), restricts treatment of dangling energies\n"
	     "Python Args: SetDangleParameter(dangle)\n"
	     "Values of the parameter: \n"
             "  INT=0      Ignores dangling energies (mostly for debugging).\n"
             "  INT=1      Unpaired nucleotides adjacent to a branch in a multi-loop or external loop\n"
             "             are allowed to dangle on at most one branch in that loop.\n"
             "             This is the default setting for gtmfe.\n"
             "  INT=2      Dangling energies are added for nucleotides on either side of each branch in\n" 
             "             multi-loops and external loops.\n"
             "             This is the default setting for gtboltzmann and gtsubopt.\n"
             "             (This is the same as the -d2 setting in the RNAfold from the "
	     "Vienna RNA Package.)\n"
             "otherwise    INT is ignored and the default setting is used."

     }, 
     { 
	     "SetTerminalMismatch",    
	     SetTerminalMismatch, 
	     METH_COEXIST,
	     "Description: Enable/disable terminal mismatch calculations\n"
	     "Python Args: SetTerminalMismatch(enable)\n"
	     "See Also:    EnableTerminalMismatch(), DisableTerminalMismatch()" 
     },
     { 
	     "SetLimitContactDistance", 
	     SetLimitContactDistance, 
	     METH_COEXIST, 
	     "Description: Set maximum base pair contact distance\n"
	     "Python Args: SetLimitContactDistance(lcDist)\n"
	     "             Set a maximum base pair contact distance to INT. If no limit is given,\n"
             "             base pairs can be over any distance."
     },
     { 
	     "SetPrefilterParameter",   
	     SetPrefilterParameter,   
	     METH_COEXIST, 
	     "Description: Prohibits any basepair which does not have appropriate neighboring\n"
	     "             nucleotides such that it could be part of a helix of this length\n"
	     "Python Args: SetPrefilterParameter(prefilter)" 
     }, 
     { 
	     "GetPFuncCount", 
	     GetPFuncCount, 
	     METH_COEXIST, 
	     "Description: Output the number of possibles structures (using the partition function)\n"
	     "Python Args: GetPFuncCount(baseSeq, consList = [])\n"
	     "See Also:    Help topics \"constraints\" and \"settings\""
     }, 
     { 
	     "GetPFuncCountSHAPE", 
	     GetPFuncCountSHAPE, 
	     METH_COEXIST, 
	     "Description: Output the number of possibles structures (using the partition function) -- \n"
	     "             with SHAPE constraints \n"
	     "Python Args: GetPFuncCountSHAPE(baseSeq, consList = [])\n"
	     "See Also:    Help topic \"constraints\" and \"settings\""
     }, 
     { 
	     "ComputeBPP", 
	     ComputeBPP, 
	     METH_COEXIST, 
	     "Description:  Calculate base pair probabilities and unpaired probabilities\n"
	     "Python Args:  ComputeBPP(baseSeq, consList = [])\n"
	     "Return Value: A list of tuples of the form (i, j, probability)\n"
	     "See Also:     Help topic \"constraints\" and \"settings\"" 
     }, 
     { 
	     "ComputeBPPSHAPE", 
	     ComputeBPPSHAPE, 
	     METH_COEXIST, 
	     "Description:  Calculate base pair probabilities and unpaired probabilities --\n"
	     "              with SHAPE constraints\n"
	     "Python Args:  ComputeBPPSHAPE(baseSeq, consList = [])\n"
	     "Return Value: A list of tuples of the form (i, j, probability)\n"
	     "See Also:     Help topic \"constraints\" and \"settings\"" 
     },
     { 
	     "GetMFEStructure", 
	     GetMFEStructure,    
	     METH_COEXIST, 
	     "Description:  Get the MFE and the MFE DotBracket structure\n"
	     "Python Args:  GetMFEStructure(baseSeq, consList = [])\n"
	     "Return Value: A tuple (mfe, mfeStruct) where the MFE structure is string in DOT notation\n"
	     "See Also:     Help topic \"constraints\""
     }, 
     { 
	     "GetMFEStructureSHAPE", 
	     GetMFEStructureSHAPE, 
	     METH_COEXIST, 
	     "Description:  Get the MFE and its structure -- with SHAPE constraints\n"
	     "Python Args:  GetMFEStructureSHAPE(baseSeq, consList = [])\n"
	     "Return Value: A tuple (mfe, mfeStruct) where the MFE structure is string in DOT notation\n"
	     "See Also:     Help topic \"constraints\""
     }, 
     { 
	     "GetSuboptStructures", 
	     GetSuboptStructuresWithinRange, 
	     METH_COEXIST, 
	     "Description: Compute suboptimal structures within DOUBLE kcal/mole of MFE\n"
	     "Python Args: GetSuboptStructures(baseSeq, delta)\n"
	     "See Also:    Help topic \"settings\"" 
     }, 
     { 
	     "SampleBoltzmannStructures", 
	     SampleBoltzmannStructures, 
	     METH_COEXIST, 
	     "Description:  Sample N structures from the Boltzmann distribution\n"
	     "Python Args:  SampleBoltzmannStructures(baseSeq, N, consList = [])\n"
	     "Return Value: A list of tuples of the form (estProb, actualProb, energy, dotStruct)\n"
	     "See Also:     Help topics \"constraints\" and \"settings\""
     }, 
     { 
	     "SampleBoltzmannStructuresSHAPE", 
	     SampleBoltzmannStructuresSHAPE, 
	     METH_COEXIST, 
	     "Description:  Sample N structures from the Boltzmann distributions -- with SHAPE constraints\n"
             "Python Args:  SampleBoltzmannStructuresSHAPE(baseSeq, N, consList = [])\n"
             "Return Value: A list of tuples of the form (estProb, actualProb, energy, dotStruct)\n"
             "See Also:     Help topics \"constraints\" and \"settings\"" 
     }, 
     {
	     "DisplayDetailedHelp", 
	     DisplayDetailedHelp, 
	     METH_NOARGS, 
	     "Description: Display detailed help about all available methods and topics\n"
	     "Python Args: DisplayDetailedHelp()\n"
	     "See Also:    DisplayHelp(funcHelpTopic)"
     }, 
     {
	     "DisplayHelp", 
	     DisplayHelp,
	     METH_COEXIST,
	     "Description: Display help about selected help or topic (use topics \"?\" or \"all\"\n"
	     "             to list all help topics)\n"
	     "Python Args: DisplayHelp(funcHelpTopic)\n"
	     "See Also:    DisplayDetailedHelp()"
     },
     { 
	     NULL, 
	     NULL, 
	     0, 
	     NULL 
     },
};

PyObject * DisplayDetailedHelp(void) {
     for(int fidx = 0; fidx < GetArrayLength(GTFoldPython_Methods) - 1; fidx++) {
          DisplayHelp(GTFoldPython_Methods[fidx].ml_name);
     }
     DisplayHelp("settings");
     DisplayHelp("constraints");
     return ReturnPythonNone();
}

PyObject * DisplayDetailedHelpSettings(void) {
     TerminalPrint(CONFIG_STDMSGOUT, PRINT_HELP_MAINHDR_ANSIFMT, 
		   "DISPLAYING MANUAL INFORMATION FOR TOPIC: config|settings\n\n");
     for(int sidx = 0; sidx < GetArrayLength(GTFoldPythonConfigSettings_kwlist); sidx++) {
          PrintHelpListItem(">>", "Setting:       ", GTFoldPythonConfigSettings_kwlist[sidx].keywordID);
	  PrintHelpListItem(">>", "Value Type:    ", CPrimitiveTypeToString(GTFoldPythonConfigSettings_kwlist[sidx].ctype));
	  PrintHelpListItem(">>", "GTFold Options:", GTFoldPythonConfigSettings_kwlist[sidx].gtfoldOptions);
	  PrintHelpListItem(">>", "Description:", ""); 
	  TerminalPrint(CONFIG_STDMSGOUT, PRINT_HELP_DOCSTR_ANSIFMT, 
			"%s\n", GTFoldPythonConfigSettings_kwlist[sidx].help);
	  fprintf(CONFIG_STDMSGOUT, "\n");
     }	
     return ReturnPythonNone();
}

PyObject * DisplayHelp(const char *methodName) {
     if(methodName == NULL) {
          SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CARGS, NULL);
          return ReturnPythonNone();
     }
     if(!strcmp(methodName, "?") || !strcasecmp(methodName, "help")) { 
          TerminalPrint(CONFIG_STDMSGOUT, PRINT_HELP_MAINHDR_ANSIFMT, "LIST OF ALL HELP TOPICS:");
	  fprintf(CONFIG_STDMSGOUT, "\n");
	  for(int fidx = 0; fidx < GetArrayLength(GTFoldPython_Methods) - 1; fidx++) {
               PrintHelpListItem("*", "", GTFoldPython_Methods[fidx].ml_name);
	  }
	  PrintHelpListItem("*", "", "constraints");
	  PrintHelpListItem("*", "", "config|settings");
	  PrintHelpListItem("*", "", "?|help|all");
          fprintf(CONFIG_STDMSGOUT, "\n");
	  return ReturnPythonNone();
     }
     else if(!strcasecmp(methodName, "all")) {
	  return DisplayDetailedHelpSettings();
     }
     else if(!strcasecmp(methodName, "config") || !strcasecmp(methodName, "settings")) {
	  return DisplayDetailedHelpSettings();
     }
     else if(!strcasecmp(methodName, "constraints")) {
          TerminalPrint(CONFIG_STDMSGOUT, PRINT_HELP_MAINHDR_ANSIFMT, 
			"DISPLAYING MANUAL INFORMATION FOR TOPIC: constraints");
	  fprintf(CONFIG_STDMSGOUT, "\n");
	  TerminalPrint(CONFIG_STDMSGOUT, PRINT_HELP_DOCSTR_ANSIFMT, 
			"There are two types of constraints we will consider with GTFold: \n"
			"(1) F/P constraint syntax; and (2) SHAPE constraint syntax.\n"
	                "There is also a helper script in "
		         "\"Python/Utils/ForcedDOTToConstraints.py\"\nthat converts DOT-style\n" 
		         "constraints like\n\"....<<<<<..xxxxx.>>>>>..........(((((.......)))))..\"\n"
	                 "documented at https://www.tbi.univie.ac.at/RNA/tutorial/#verbatim-34.\n\n");
	  TerminalPrint(CONFIG_STDMSGOUT, PRINT_HELP_DOCSTR_ANSIFMT | BOLD, 
			"F/P constraint syntax:\n");
	  TerminalPrint(CONFIG_STDMSGOUT, PRINT_HELP_DOCSTR_ANSIFMT, 
                        "The constraints given in constraint file should be formated as follows:\n"
                        "P i j k      Prohibits the formation of base pairs (i,j) (i+1,j-1) ... (i+k-1, j-k+1).\n"
                        "F i j k      Forces the formation of base pairs (i,j) (i+1,j-1) ... (i+k-1, j-k+1).\n"
                        "P i 0 k      Makes the bases from i to i+k-1 single stranded bases.\n"
                        "F i 0 k      Forces the bases from i to i+k-1 to be paired\n"
                        "             (without specifying their pairing parterns).\n"
                        "Note that k must be positive, and j-i must be at least 4.\n\n");
	  TerminalPrint(CONFIG_STDMSGOUT, PRINT_HELP_DOCSTR_ANSIFMT | BOLD, 
			  "SHAPE constraint syntax:\n");
	  TerminalPrint(CONFIG_STDMSGOUT, PRINT_HELP_DOCSTR_ANSIFMT, 
			"For file format specs, see:\n"
                        "http://rna.urmc.rochester.edu/Releases/5.8/manual/Text/File_Formats.html#SHAPE\n\n"
                        "SHAPE values should be given in a file with two single-space-delimited columns,\n"
                        "for example:\n"
                        "--------\n"
                        "1 0.1\n"
                        "2 0.001\n"
                        "3 1.67\n"
                        "etc.,\n"
                        "--------\n"
                        "where the first column is the nucleotide position (INT) and the second column is the\n"
                        "SHAPE reactivity[1] (DOUBLE) for that position. The file should have no header. Not all\n" 
                        "positions need to be included in the file, and the values do not need to be in order of\n"
                        "increasing position. Negative SHAPE reactivities are ignored.\n\n");
	  TerminalPrint(CONFIG_STDMSGOUT, PRINT_HELP_DOCSTR_ANSIFMT | BOLD, 
		        "Python Example (in `ipython3`):\n");
	  TerminalPrint(CONFIG_STDMSGOUT, PRINT_HELP_DOCSTR_ANSIFMT, 
		        ">>> import GTFoldPythonImportAll\n"
		        ">>> fpCons = GTFPUtils.ReadFPConstraintsFromFile(\"file.cons\")\n"
	                ">>> GTFP.GetMFEStructure(\"ACGUACGU\", fpCons)\n"
			">>> shapeCons = GTFPUtils.ReadSHAPEConstraintsFromFile(\"file.shape\")\n"
			">>> GTFP.GetMFEStructureSHAPE(\"ACGUACGU\", shapeCons)\n");
	  fprintf(CONFIG_STDMSGOUT, "\n");
	  return ReturnPythonNone();
     }
     int helpTopicIdx = -1;
     for(int fidx = 0; fidx < GetArrayLength(GTFoldPython_Methods) - 1; fidx++) {
          if(!strcasecmp(methodName, GTFoldPython_Methods[fidx].ml_name)) {
	       helpTopicIdx = fidx;
	       break;
	  }
     }
     if(helpTopicIdx < 0) {
          TerminalPrint(CONFIG_STDMSGOUT, PRINT_HELP_ERRORSTR_ANSIFMT, 
			"Unable to locate help for topic \"%s\".\n", methodName);
	  TerminalPrint(CONFIG_STDMSGOUT, PRINT_HELP_ERRORSTR_ANSIFMT, 
			"Try \"?\" or \"help\" to display a list of all "
			"available settings, \nor \"all\" to display detailed help "
		        "information about all possible topics.\nRunning this function "
		        "with \"config\" or \"settings\" will list detailed help about\n"
		        "all of the GTFold configuration settings.\n");
	  fprintf(CONFIG_STDMSGOUT, "\n");
	  return ReturnPythonNone();
     }
     TerminalPrint(CONFIG_STDMSGOUT, PRINT_HELP_MAINHDR_ANSIFMT, 
		   "DISPLAYING MANUAL INFORMATION FOR TOPIC: %s\n", methodName);
     TerminalPrint(CONFIG_STDMSGOUT, PRINT_HELP_DOCSTR_ANSIFMT, 
		   "%s\n", GTFoldPython_Methods[helpTopicIdx].ml_doc);
     fprintf(CONFIG_STDMSGOUT, "\n");
     return ReturnPythonNone();
}

#ifdef PY3K
PyMODINIT_FUNC PyInit_GTFoldPython(void) {
     PyGILState_STATE pgState = PyGILState_Ensure();
     PyObject *moduleObj = PyModule_Create(&GTFoldPythonModule);
     PyGILState_Release(pgState);
     if(moduleObj == NULL) {
          return ReturnPythonNone();
     }
     return moduleObj;
}
struct PyModuleDef GTFoldPythonModule = {
     PyModuleDef_HEAD_INIT,
     "GTFoldPython",
     "Python3 wrapper for the historical GTFold library and C/C++ sources",
     -1,
     GTFoldPython_Methods
};
#endif

void ModuleInterfaceDeps(void) {
     // this function is just to get all the symbols registered by the linker, 
     // it is never intended to be run, so throw an assertion in the event on user error:
     assert(0);
     short nullConsList[1][4];
     memset(nullConsList, 0, 4 * sizeof(short));
     SHAPEConstraint_t *nullSHAPEConsList;
     memset(nullSHAPEConsList, 0, sizeof(SHAPEConstraint_t));
     GTFoldPythonInit();
     GTFoldPythonConfig(0, 0, 0, NULL);
     PrintGTFoldRunConfiguration(true);
     SetGTFoldDataDirectory(NULL, 0);
     SetDangleParameter(0);
     SetTerminalMismatch(0);
     SetLimitContactDistance(0);
     SetPrefilterParameter(0);
     GetPFuncCount(NULL, nullConsList, 0);
     GetPFuncCountSHAPE(NULL, nullSHAPEConsList, 0);
     ComputeBPP(NULL, nullConsList, 0);
     ComputeBPPSHAPE(NULL, nullSHAPEConsList, 0);
     GetMFEStructure(NULL, nullConsList, 0);
     GetMFEStructureSHAPE(NULL, nullSHAPEConsList, 0);
     GetSuboptStructuresWithinRange(NULL, 0.0);
     SampleBoltzmannStructures(NULL, nullConsList, 0, 0);
     SampleBoltzmannStructuresSHAPE(NULL, nullSHAPEConsList, 0, 0);
     DisplayDetailedHelp();
     DisplayHelp(NULL);
}

