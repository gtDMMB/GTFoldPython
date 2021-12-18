/* BoltzmannSampling.c : Implementation of the GTFold boltzmann_main.cc and related sampling routines;
 * Author: Maxie D. Schmidt (maxieds@gmail.com) 
 * Created: 2020.02.07
 */

#include <sys/stat.h>
#include <sys/types.h>

#include "include/options.h"
#include "include/global.h"
#include "include/boltzmann_main.h"
#include "include/subopt_main.h"
#include "include/loader.h"
#include "include/utils.h"
#include "include/algorithms-partition.h"
#include "include/stochastic-sampling.h"
#include "include/stochastic-sampling-d2.h"
#include "include/AdvancedDouble.h"

#include "BoltzmannSampling.h"
#include "Utils.h"
#include "ErrorHandling.h"
#include "GTFoldPython.h"
#include "LoadThermoParams.h"

int OUTPUT_FILES_CONFIG = 0;

void ConfigureOutputFileSettings(void) {
    if(OUTPUT_FILES_CONFIG) {
         SetLastErrorCode(GTFPYTHON_ERRNO_OUTFILESCFG, NULL);
	 return;
    }
    // If output dir specified
    if(strcmp(outputDir, "")) {
	 if(!IsDirectory(outputDir) && 
	    mkdir(outputDir, S_IRWXU | S_IRGRP | S_IWGRP) != -1 && 
	    errno != EEXIST) {
              if(!SILENT) {
	           fprintf(CONFIG_STDMSGOUT, 
			   "Could not create directory \"%s\".\n"
			   "Writing output files to the CWD instead.\n");
	      }
	      strcpy(outputDir, "");
	 }
	 else if(outputDir[strlen(outputDir) - 1] != '/') {
	      strcat(outputDir, "/");
	 }
    }
    if(ctFileDumpDir != NULL && strlen(ctFileDumpDir) > 0) {
         char nextCTDir[STR_BUFFER_SIZE] = { '\0' };
	 strcat(nextCTDir, outputDir);
	 strcat(nextCTDir, ctFileDumpDir);
	 if(IsDirectory(nextCTDir) || 
	    mkdir(nextCTDir, S_IRWXU | S_IRGRP | S_IWGRP) != -1 || errno == EEXIST) { 
	      // success creating the directory:
	      strcpy(ctFileDumpDir, nextCTDir);
	      if(ctFileDumpDir[strlen(ctFileDumpDir) - 1] != '/') {
	           strcat(ctFileDumpDir, "/");
	      }
	 }
	 else {
	      if(!SILENT) {
	           fprintf(CONFIG_STDMSGOUT, 
		           "Unable to create CT file output directory \"%s\".\n", nextCTDir);
	      }
	      strcpy(ctFileDumpDir, "");
	 }
    }
    SetFileOutPath(outputFile, ctFileDumpDir, outputPrefix, "sample", ".ct");
    SetFileOutPath(bppOutFile, outputDir, outputPrefix, "bpp", ".txt");
    SetFileOutPath(sampleOutFile, outputDir, outputPrefix, "sampleout", ".samples");
    SetFileOutPath(energyDecomposeOutFile, outputDir, outputPrefix, "energydecomp", ".energy");
    SetFileOutPath(estimateBppOutputFile, outputDir, outputPrefix, "estbpp", ".sbpp");
    SetFileOutPath(scatterPlotOutputFile, outputDir, outputPrefix, "scatterplot", ".frequency");
    SetFileOutPath(pfArraysOutFile, outputDir, outputPrefix, "partfuncarrays", ".pfarrays");
    SetFileOutPath(suboptFile, outputDir, outputPrefix, "subpopt_ss", ".txt");
    SetFileOutPath(stochastic_summery_file_name, ctFileDumpDir, outputPrefix, "stochsummary", ".out");
    OUTPUT_FILES_CONFIG = 1;
}

void ValidateOptions(void) {
    if(!SILENT) fprintf(CONFIG_STDMSGOUT, "\nValidating Options:\n");
    /* boltzmann_main.cc validation: */
    if(PF_COUNT_MODE){
            if(RND_SAMPLE){
                    if(!SILENT && VERBOSE) fprintf(CONFIG_STDMSGOUT, 
				        "Ignoring --sample Option with --pfcount \n"
				        "option and Program will continue with --pfcount "
					"option only.\n\n");
                    RND_SAMPLE = false;
            }
    }
    if(BPP_ENABLED){
                //do nothing
    }
    else if(CALC_PART_FUNC && !RND_SAMPLE){ // partition function
            if(print_energy_decompose==1){
                    if(!SILENT && VERBOSE) fprintf(CONFIG_STDMSGOUT, 
				        "Ignoring the option -e or --energy, as it will be "
					"valid with --sample option.\n\n");
            }
            if(ST_D2_ENABLE_SCATTER_PLOT && !ST_D2_ENABLE_BPP_PROBABILITY){
                    if(!SILENT && VERBOSE) fprintf(CONFIG_STDMSGOUT, 
				        "Ignoring the option --groupbyfreq, as it will be "
					"valid with --sample option.\n\n");
            }
            if(ST_D2_ENABLE_UNIFORM_SAMPLE){
                    if(!SILENT && VERBOSE) fprintf(CONFIG_STDMSGOUT, 
				        "Ignoring the option --sampleenergy, as it will be "
					"valid with --sample option.\n\n");
            }
            if(ST_D2_ENABLE_CHECK_FRACTION){
                    if(!SILENT && VERBOSE) fprintf(CONFIG_STDMSGOUT, 
				        "Ignoring the option --checkfraction, as it will be "
					"valid with --sample option.\n\n");
            }
            if(ST_D2_ENABLE_BPP_PROBABILITY){
                    if(!SILENT && VERBOSE) fprintf(CONFIG_STDMSGOUT, 
				        "Ignoring the option --estimatebpp, as it will be "
					"valid with --sample option.\n\n");
            }
            if(ST_D2_ENABLE_ONE_SAMPLE_PARALLELIZATION){
                    if(!SILENT && VERBOSE) fprintf(CONFIG_STDMSGOUT, 
				        "Ignoring the option --parallelsample, as it will be "
					"valid with --sample option.\n\n");
            }
    }
    else if(!CALC_PART_FUNC && RND_SAMPLE){ // sample
            //nothing to check
    } 
    else if(CALC_PART_FUNC && RND_SAMPLE){ // both partition function and sample
            if(!SILENT && VERBOSE) {
	        fprintf(CONFIG_STDMSGOUT, 
		        "Program proceeding with sampling as both partition function "
			"calculation and sampling calculation option are used.\n\n");
	    }
            CALC_PART_FUNC = false;
    }
    else if(!CALC_PART_FUNC && !RND_SAMPLE){ // neither partition function nor sample
            if(!SILENT && VERBOSE) {
	        fprintf(CONFIG_STDMSGOUT, 
		        "WARNING: [gtboltzman] program exiting as neither partition function \n"
		        "         calculation nor sampling calculation option is used.\n\n");
    
	    }
    }
    /* mfe_main.cc validation: NONE */
    /* subopt_main.cc validation: */
    if (UNIQUE_MULTILOOP_DECOMPOSITION != 0 && UNIQUE_MULTILOOP_DECOMPOSITION != 1) {
            UNIQUE_MULTILOOP_DECOMPOSITION = -1;
            if(!SILENT && VERBOSE) {
	         fprintf(CONFIG_STDMSGOUT, 
			 "Ignoring --unique option as it accepts only numbers 0 and 1 and \n"
	                 "program will continue with --unique value as default choice.\n");
	    }
    }
    if (max_structure_count < 0) {
            max_structure_count = -1;
            if(!SILENT && VERBOSE) {
	         fprintf(CONFIG_STDMSGOUT, 
		         "Ignoring --maxcount option as it accepts only positive numbers and \n"
			 "program will continue with maxcount value as -1 which means there is \n"
			 "no restriction on maximum count of structures\n");
	    }
    }
    if (is_check_for_duplicates_enabled != 0 && is_check_for_duplicates_enabled != 1) {
            is_check_for_duplicates_enabled = 0;
            if(!SILENT && VERBOSE) {
		    fprintf(CONFIG_STDMSGOUT, 
			    "Ignoring --duplicatecheck option as it accepts only numbers \n"
			    "0 and 1 and program will continue with default choice of \n"
			    "--duplicatecheck.\n");
            }
    }
    if(!SILENT && VERBOSE) {
        printf("\n");
    }
}

void * ConfigureBoltzmannMainRuntimeParameters(MFEStructRuntimeArgs_t *rtArgs) {
     if(rtArgs == NULL) {
	  SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CARGS, NULL);
          return NULL;
     }
     CALC_PART_FUNC = 1;
     RND_SAMPLE = 1;
     g_LIMIT_DISTANCE = LIMIT_DISTANCE;
     g_contactDistance = contactDistance;
     if(InitGTFoldMFEStructureData(rtArgs) != GTFPYTHON_ERRNO_OK) {
          FreeMFEStructRuntimeArgs(rtArgs);
          return NULL;
     }
     if(*CONFIG_DEBUGGING) {
          fprintf(CONFIG_STDMSGOUT, "BASE SEQUENCE: [#%d] %s\n", rtArgs->numBases, rtArgs->baseSeq);
          fprintf(CONFIG_STDMSGOUT, "CONSTRAINTS:\n");
          PrintGTFoldConstraints(rtArgs->mfeConstraints, rtArgs->numConstraints);
          PrintGTFoldSHAPEConstraints(rtArgs->mfeSHAPEConstraints, rtArgs->numSHAPEConstraints);
     }
     //readThermodynamicParameters(GTFOLD_DATADIR, 1, 0, 0, 0);
     if(LoadThermodynamicParameters(ACTIVE_THERMO_PARAMS, GTFOLD_DATADIR) != GTFPYTHON_ERRNO_OK) {
          return NULL;
     }
     if(scaleFactor==-1){ // that is if scaleFactor is not input by the user, and we 
                          // only need to decide for its default value
          if(rtArgs->numBases < 1000){
               scaleFactor=0.0;
          }
          else{
               scaleFactor=1.07;
          }
     }
     if(PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER == 0){
          decideAutomaticallyForAdvancedDoubleSpecifier();
     }
     if(PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER == 2 || PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER == 3 ||
        PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER == 4){
          mpf_set_default_prec(g_bignumprecision);
     }
     if(*CONFIG_DEBUGGING) {
          PrintGTFoldRunConfiguration(true);
     }
     if (LIMIT_DISTANCE) {
          if (!SILENT && VERBOSE && rtArgs->numBases < (unsigned int) contactDistance) {
               fprintf(CONFIG_STDMSGOUT, 
		       "\nContact distance limit is higher than the sequence length. \n"
                       "Continuing without restraining contact distance.\n");
          }
          else if(!SILENT && VERBOSE) 
	       fprintf(CONFIG_STDMSGOUT, 
		       "\nLimiting contact distance to %d\n", contactDistance);
     }
     if(scaleFactor != 0.0){
          double mfe = ComputeMFEStructure(rtArgs);
          scaleFactor = scaleFactor * mfe;
     }
     return rtArgs;
}

PyObject * HandleBPP(MFEStructRuntimeArgs_t *rtArgs) {
     if(rtArgs == NULL) {
          SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CARGS, NULL);
	  return ReturnPythonNone();
     }
     double **_Q,  **_QM, **_QB, **_P;
     _Q  = mallocTwoD(rtArgs->numBases + 1, rtArgs->numBases + 1);
     _QM = mallocTwoD(rtArgs->numBases + 1, rtArgs->numBases + 1);
     _QB = mallocTwoD(rtArgs->numBases + 1, rtArgs->numBases + 1);
     _P  = mallocTwoD(rtArgs->numBases + 1, rtArgs->numBases + 1);

     fill_partition_fn_arrays(rtArgs->numBases, _Q, _QB, _QM);
     fillBasePairProbabilities(rtArgs->numBases, _Q, _QB, _QM, _P);
     if(WRITEAUXFILES) {
          printBasePairProbabilitiesDetail(rtArgs->numBases, structure, _P, bppOutFile);
          if(!SILENT) fprintf(CONFIG_STDMSGOUT, "Saved BPP output in %s\n", bppOutFile);
     }
     PyGILState_STATE pgState = PyGILState_Ensure();
     int nb = rtArgs->numBases, lstIdx = 0;
     PyObject *pyStructObj = PyList_New(nb * (nb - 1) >> 1);
     for(int i = 1; i <= rtArgs->numBases; i++) {
          for(int j = 1; j < i; j++) {
               PyObject *bppProbPair = PyTuple_New(3);
	       PyTuple_SetItem(bppProbPair, 0, PyLong_FromLong(i));
	       PyTuple_SetItem(bppProbPair, 1, PyLong_FromLong(j));
	       PyTuple_SetItem(bppProbPair, 2, PyFloat_FromDouble(_P[MIN(i,j)][MAX(i,j)]));
	       Py_INCREF(bppProbPair);
	       PyList_SetItem(pyStructObj, lstIdx++, bppProbPair);
	  }
     }
     Py_INCREF(pyStructObj);
     PyGILState_Release(pgState);
      
     freeTwoD(_Q,  rtArgs->numBases + 1, rtArgs->numBases + 1);
     freeTwoD(_QM, rtArgs->numBases + 1, rtArgs->numBases + 1);
     freeTwoD(_QB, rtArgs->numBases + 1, rtArgs->numBases + 1);
     freeTwoD(_P,  rtArgs->numBases + 1, rtArgs->numBases + 1);
     return pyStructObj;
}

/* Start sampling functions and data: */
#include <map>
#include <string>
#include <utility>
#include <iostream>

typedef std::map< std::string,std::pair<int,double> > RawSampleDataList_t;

PyObject * PackageBatchSampleOutputForPython(RawSampleDataList_t rawSampleData) {
     PyGILState_STATE pgState = PyGILState_Ensure();
     PyObject *structObjList = PyList_New(rawSampleData.size());
     PyGILState_Release(pgState);
     int lstIdx = 0;
     std::map< std::string,std::pair<int,double> >::iterator iter;
     for(iter = rawSampleData.begin(); iter != rawSampleData.end();  ++iter) {
          const std::string& ss = iter->first;
          const std::pair<int, double>& pp = iter->second;
          const double& estimated_p =  (double) pp.first / (double) num_rnd;
          const double& energy = pp.second;
          double actual_p = pow(2.718281, -1.0 * energy * 100 / RT) / U;
	  pgState = PyGILState_Ensure();
	  PyObject *structTuple = PyTuple_New(4);
	  PyTuple_SetItem(structTuple, 0, PyFloat_FromDouble(estimated_p));
	  PyTuple_SetItem(structTuple, 1, PyFloat_FromDouble(actual_p));
          PyTuple_SetItem(structTuple, 2, PyFloat_FromDouble(energy));
	  PyTuple_SetItem(structTuple, 3, PyUnicode_FromString(ss.c_str()));
	  Py_INCREF(structTuple);
	  PyList_SetItem(structObjList, lstIdx++, structTuple);
	  PyGILState_Release(pgState);
     }
     pgState = PyGILState_Ensure();
     Py_INCREF(structObjList);
     PyGILState_Release(pgState);
     return structObjList;
}

template<typename T>
RawSampleDataList_t HandleD2Sample(StochasticTracebackD2<T> std2, int N, 
		       MFEStructRuntimeArgs_t *rtArgs) {
     RawSampleDataList_t rawStructList;
     if(!SILENT) fprintf(CONFIG_STDMSGOUT, "\nComputing stochastic traceback...\n");
     int pf_count_mode = 0;
     if(PF_COUNT_MODE) pf_count_mode=1;
     int no_dangle_mode = 0;
     if(CALC_PF_DO) no_dangle_mode=1;
     t1 = get_seconds();
     std2.initialize(rtArgs->numBases, pf_count_mode, no_dangle_mode, print_energy_decompose, 
		     PF_D2_UP_APPROX_ENABLED, ST_D2_ENABLE_CHECK_FRACTION, energyDecomposeOutFile, 
		     scaleFactor);
     t1 = get_seconds() - t1;
     if(!SILENT) fprintf(CONFIG_STDMSGOUT, 
		         "D2 Traceback initialization (partition function computation) "
		         "running time: %f seconds\n", t1);
     t1 = get_seconds();
     if(!DUMP_CT_FILE) {
          if(ST_D2_ENABLE_COUNTS_PARALLELIZATION && g_nthreads != 1)
               rawStructList = std2.batch_sample_parallel(N, ST_D2_ENABLE_SCATTER_PLOT, 
			                  ST_D2_ENABLE_ONE_SAMPLE_PARALLELIZATION,
			                  ST_D2_ENABLE_BPP_PROBABILITY, sampleOutFile, 
		 		          estimateBppOutputFile, scatterPlotOutputFile);
          else rawStructList = std2.batch_sample(N, ST_D2_ENABLE_SCATTER_PLOT, 
			                  ST_D2_ENABLE_ONE_SAMPLE_PARALLELIZATION, 
					  ST_D2_ENABLE_UNIFORM_SAMPLE, 
					  ST_D2_UNIFORM_SAMPLE_ENERGY, 
					  ST_D2_ENABLE_BPP_PROBABILITY, 
					  sampleOutFile, estimateBppOutputFile, 
					  scatterPlotOutputFile);   
     }
     else  {
          rawStructList = std2.batch_sample_and_dump(N, ctFileDumpDir, 
			                             stochastic_summery_file_name, 
						     rtArgs->baseSeq, seqfile);
     }
     t1 = get_seconds() - t1;
     if(!SILENT) fprintf(CONFIG_STDMSGOUT, 
		         "D2 Traceback computation running time: %f seconds\n", t1);
     if(PF_PRINT_ARRAYS_ENABLED) std2.printPfMatrixesToFile(pfArraysOutFile);
     std2.free_traceback();
     return rawStructList;
}

PyObject * HandleD2Sample(int advDblSpec, int N, MFEStructRuntimeArgs_t *rtArgs) {
     if(N <= 0 || rtArgs == NULL) {
          SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CARGS, NULL);
	  return ReturnPythonNone();
     }
     RawSampleDataList_t rawStructArr;
     switch(advDblSpec) {
          case 1: {
	       StochasticTracebackD2<AdvancedDouble_Native> std2;
	       rawStructArr = HandleD2Sample<AdvancedDouble_Native>(std2, N, rtArgs);
	       break;
	   }
          case 2: {
	       StochasticTracebackD2<AdvancedDouble_BigNum> std2;
	       rawStructArr = HandleD2Sample<AdvancedDouble_BigNum>(std2, N, rtArgs);
	       break;
	   }
          case 3: {
	       StochasticTracebackD2<AdvancedDouble_Hybrid> std2;
	       rawStructArr = HandleD2Sample<AdvancedDouble_Hybrid>(std2, N, rtArgs);
	       break;
	   }
          case 4: {
	       StochasticTracebackD2<AdvancedDouble_BigNumOptimized> std2;
	       rawStructArr = HandleD2Sample<AdvancedDouble_BigNumOptimized>(std2, N, rtArgs);
	       break;
	   }
	  default:
	       SetLastErrorCode(GTFPYTHON_ERRNO_INVBOLTZPARAMS, NULL);
	       return ReturnPythonNone();
     }
     return PackageBatchSampleOutputForPython(rawStructArr);
}

RawSampleDataList_t ComputeDsBatchSample(int N, int baseSeqLength, const char *baseSeq) {
     //// data dump preparation code starts here
     std::stringstream ss;
     std::ofstream summaryoutfile;
     std::string seqname;
     if((DUMP_CT_FILE || WRITEAUXFILES) && !strcmp(ctFileDumpDir, "")) {
          char abspath[1000];
          char *tmp = getcwd(abspath, 1000);
          if(tmp != abspath){ 
               SetLastErrorCode(GTFPYTHON_ERRNO_OTHER, "Error in getcwd.");
	       DUMP_CT_FILE = 0;
          }
	  else {
	       strcpy(ctFileDumpDir, abspath);
	  }
     }
     if(DUMP_CT_FILE || WRITEAUXFILES) { 
          summaryoutfile.open(stochastic_summery_file_name);
	  std::string seqfileTemp = seqfile;
	  seqname = seqfileTemp.substr(seqfileTemp.find_last_of("/\\") + 1, seqfileTemp.length() - 1);
          if(!SILENT) {
	       cerr << "Using ctFileDumpDir = " << ctFileDumpDir << endl;
               cerr << "Using stochastic_summary_file_name = "; 
	       cerr << stochastic_summery_file_name << endl;
	  }
     }
     //// data dump preparation code ends here
     srand(time(NULL));
     int *structure = new int[baseSeqLength + 1];
     std::map< std::string,std::pair<int,double> >  uniq_structs;
     if(N > 0) {
          if(!SILENT) fprintf(CONFIG_STDMSGOUT, "\nSampling structures...\n");
          int count;
          for(count = 1; count <= num_rnd; ++count) {
               memset(structure, 0, (baseSeqLength + 1) * sizeof(int));
               double energy = rnd_structure(structure, baseSeqLength);
               std::string ensemble(baseSeqLength + 1, '.');
               for(int i = 1; i <= (int) baseSeqLength; ++i) {
                    if(structure[i] > 0 && ensemble[i] == '.') {
                         ensemble[i] = '(';
                         ensemble[structure[i]] = ')';
                    }
	       }
	       std::map<std::string,std::pair<int,double> >::iterator iter ;
               if((iter = uniq_structs.find(ensemble.substr(1))) != uniq_structs.end()) {
                    std::pair<int, double>& pp = iter->second;
                    pp.first++;
               }
               else {
                    uniq_structs.insert(make_pair(ensemble.substr(1), 
					std::pair<int, double>(1, energy)));
	       }
               //// data dump code starts here again
	       if(DUMP_CT_FILE || WRITEAUXFILES) {
                    std::stringstream ss2;
                    ss2 << ctFileDumpDir << "/" << seqname << "_" << count << ".ct";
                    save_ct_file_from_structure(ss2.str().c_str(), baseSeq, energy, structure);
		    if(WRITEAUXFILES) {
                         summaryoutfile << ss2.str() << " " << ensemble.substr(1);
			 summaryoutfile << " " << energy << std::endl;
		    }
	       }
               //// data dump code ends here again
          }
          int pcount = 0;
          int maxCount = 0; std::string bestStruct;
          double bestE = INFINITY;
          std::map< std::string, std::pair<int, double> >::iterator iter;
          for(iter = uniq_structs.begin(); iter != uniq_structs.end(); ++iter) {
               const std::string& ss = iter->first;
               const std::pair<int, double>& pp = iter->second;
               const double& estimated_p =  (double) pp.first / (double) N;
               const double& energy = pp.second;
               double actual_p = pow(2.718281, -1.0 * energy * 100 / RT) / U;
               if(!SILENT) {
	            fprintf(CONFIG_STDMSGOUT, "%s %lf %lf %lf %d\n", ss.c_str(), 
		            energy, actual_p, estimated_p, pp.first);
	       }
	       pcount += pp.first;
               if(pp.first > maxCount) {
                    maxCount = pp.first;
                    bestStruct  = ss;
                    bestE = pp.second;
               }
	  }
	  if(pcount != N) {
	       SetLastErrorCode(GTFPYTHON_ERRNO_BSAMP, 
			        "Insufficient number of structures obtained.");
	  }
	  if(!SILENT) {
               fprintf(CONFIG_STDMSGOUT, "\nMax frequency structure : \n%s e=%lf freq=%d p=%lf\n", 
		       bestStruct.c_str(), bestE, maxCount, (double) maxCount / (double) N);
	  }
     }
     if(DUMP_CT_FILE || WRITEAUXFILES) {
          summaryoutfile.close();
     }
     delete [] structure;
     return uniq_structs;
}

PyObject * HandleDsSample(int N, MFEStructRuntimeArgs_t *rtArgs) {
     if(N <= 0 || rtArgs == NULL) {
          SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CARGS, NULL);
	  return ReturnPythonNone();
     }
     int pf_count_mode = 0;
     if(PF_COUNT_MODE) pf_count_mode=1;
     int no_dangle_mode = 0;
     if(CALC_PF_DO) no_dangle_mode=1;
     if(!SILENT) {   
          fprintf(CONFIG_STDMSGOUT, 
	          "\nComputing stochastic traceback in -dS mode ..., "
	          "pf_count_mode=%d, no_dangle_mode=%d\n", pf_count_mode, no_dangle_mode);
          fprintf(CONFIG_STDMSGOUT, "\nComputing stochastic traceback...\n");
     }
     double U = calculate_partition(rtArgs->numBases, pf_count_mode, no_dangle_mode);
     t1 = get_seconds();
     RawSampleDataList_t rawStructsList = 
	                 ComputeDsBatchSample(N, rtArgs->numBases, rtArgs->baseSeq);
     t1 = get_seconds() - t1;
     if(!SILENT) {
          fprintf(CONFIG_STDMSGOUT, "Traceback computation running time: %9.6f seconds\n", t1);
     }
     free_partition();
     return PackageBatchSampleOutputForPython(rawStructsList);
}
 
