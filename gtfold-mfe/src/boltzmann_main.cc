#include <iostream>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <cstring>
#include<sstream>
#include <stdio.h>
#include <stdlib.h>

#include "global.h"
#include "loader.h"
#include "algorithms-partition.h"
#include "boltzmann_main.h"
#include "partition-func.h"
#include "partition-func-d2.h"
#include "mfe_main.h"
#include "stochastic-sampling.h"
#include "stochastic-sampling-d2.h"
#include "algorithms.h"
#include "traceback.h"
#include "utils.h"
#include "AdvancedDouble.h"
#include "shapereader.h"
#include "options.h"

using namespace std;

//int CALC_PART_FUNC = true;
//int RND_SAMPLE = false;
int DUMP_CT_FILE = false;
int CALC_PF_DO = false;
int CALC_PF_DS = false;
int CALC_PF_D2 = true; // making D2 mode as default option
int PF_D2_UP_APPROX_ENABLED = true; // making short internal loop code to run as default
int PF_PRINT_ARRAYS_ENABLED = false; // making short internal loop code to run as default
int ST_D2_ENABLE_COUNTS_PARALLELIZATION = true; // making parallelization of sample counts as default
int ST_D2_ENABLE_ONE_SAMPLE_PARALLELIZATION = false;
int ST_D2_ENABLE_SCATTER_PLOT = false;
int ST_D2_ENABLE_UNIFORM_SAMPLE = false;
double ST_D2_UNIFORM_SAMPLE_ENERGY = 0.0;

int PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER = 0; // 0 (default value) means decide automatically, 
                                            // 1 means native double, 
					    // 2 means BigNum, 
					    // 3 means hybrid, 
					    // 4 means bigNumOptimized
int ST_D2_ENABLE_CHECK_FRACTION = false;
int ST_D2_ENABLE_BPP_PROBABILITY = false;

//char seqfile[256] = "";
//char outputPrefix[256] = "";
//char outputDir[256] = "";
//char outputFile[256] = "";
//char paramDir[256] = ""; // default value
//char bppOutFile[256] = "";
char sampleOutFile[256] = "";
char energyDecomposeOutFile[256] = "";
char estimateBppOutputFile[256] = "";
char scatterPlotOutputFile[256] = "";
char pfArraysOutFile[256] = "";
char ctFileDumpDir[256] = "";
char stochastic_summery_file_name[256] = "stochaSampleSummary.txt";
//char shapeFile[256] = "";

//int num_rnd = 0;
//int print_energy_decompose = 0;
double scaleFactor=1.0;//default value will be 1.07 in case of seq len is more than 100 else zero

static std::string seq;
double t1 = 0.0;
	
static void handleBpp();
static void handleD2Sample();
static void handleDsSample();
static void handleDsPartitionFunction();
static void handleD2PartitionFunction();
void decideAutomaticallyForAdvancedDoubleSpecifier();
template <class T> static void computeD2PartitionFunction(T pf_d2);
template <class T> static void computeD2Sample(T st_d2);

static void print_usage() {
	printf("Usage: gtboltzmann [OPTION]... FILE\n\n");

	printf("   FILE is an RNA sequence file containing only the sequence or in FASTA format.\n\n");

	printf("OPTIONS\n");

	printf("   --bpp		Calculate base pair probabilities for the predicted structure\n");
	printf("			and print to output-prefix.bpp.\n");
	printf("   -d, --dangle INT	Restricts treatment of dangling energies (INT=0,2). See below for details.\n");
	printf("   --detailedhelp       Display detailed help message, and exit.\n"); 
	printf("                        Includes examples and additional options useful to developers.\n");
	printf("   -e, --energydetail   Writes loop-by-loop energy decomposition of structures to\n");
	printf("			output-prefix.energy. When using this function in combination\n");
	printf("			with --sample, number of threads must be limited to one (-t 1).\n");
	printf("   --estimatebpp	Writed a csv file containing, for each sampled base pair, that base pair and it's frequency\n");
	printf("			to output-prefix.sbpp. This option is ignored if not using --sample.\n");
	printf("   --groupbyfreq        Write a csv file (output-prefix.frequency) containing, for each sampled structure, \n"); 
	printf("                        a line with the structure's probability under the Boltzmann Distribution followed by \n"); 
	printf("                        the normalized frequency of that structure, \n"); 
	printf("                        where (normalized frequency) = (structure frequency)/(number of structures sampled)\n");
	printf("			Only valid in combination with --sample.\n");
	printf("   -h, --help           Output help (this message) and exit.\n");
	printf("   -l|--limitcd  INT	Set a maximum base pair contact distance to INT. If no\n");
	printf(" 		      	limit is given, base pairs can be over any distance.\n");
	printf("   -o, --output NAME    Write output files with prefix given in NAME\n");
	printf("   -p  --paramdir DIR   Path to directory from which parameters are to be read\n");
	printf("   --pfcount		Output the number of possible structures (using partition function).\n");
	printf("   -s|--sample   INT	Sample INT structures from Boltzmann distribution. \n"); 
	printf("                        Writes structures to file output-prefix.samples.\n");
	printf("   -t|--threads INT	Limit number of threads used to INT.\n");
	printf("   --useSHAPE FILE      Use SHAPE constraints from FILE.\n");
	printf("   -v, --verbose	Run in verbose mode (includes partition function table printing.)\n");
	printf("   -w, --workdir DIR    Path of directory where output files will be written.\n");
    
    printf("\nSHAPE syntax:\n");
    printf("\tSHAPE values should be given in a file with two space-delimited columns, for example\n");
    printf("\t\t1 0.1\n");
    printf("\t\t2 0.001 \n");
    printf("\t\t3 1.67 \n");
    printf("\t\tetc.,\n");
    printf("\twhere the first column is the nucleotide position (INT) and the second column is the SHAPE reactivity[1] (DOUBLE) for that position. The file \n");
    printf("\tshould have no header. Not all positions need to be included in the file, and the values do not need to be in order of increasing position. Negative\n");
    printf("\tSHAPE reactivities are ignored. \n");
}

static void print_usage_developer_options() {
	printf("\n\nDeveloper OPTIONS\n");
	printf("   --partition          Calculate the partition function (default is using d2 dangling mode).\n");
	printf("   --printarrays        Writes partition function arrays to prefix.pfarrays. \n");
	printf("   --exactintloop       Includes structures with abitrarily many unpaired nucleotides in internal loops.\n");
	printf("                        Note: using this option increases the running time by a factor of N,\n");
	printf("                        where N is the sequence length.\n");
	printf("   --checkfraction	While sampling structures, enable check that for each structure, the probability used \n"); 
	printf("			sampling matches the probability of that structure according to the Boltzmann Distribution.\n");
	printf("   -dS                  Calculate the partition function using sfold reccurences and use them in traceback.\n"); 
	printf("                        WARNING: this option does not pass --checkfraction test.\n");
	printf("   --sampleenergy DOUBLE      Writes only sampled structures with free energy equal to DOUBLE to file prefix.sample. \n"); 
	printf("                        Only valid in combination with --sample. Number of threads must be limited to one (-t 1).\n");
	printf("   --scale DOUBLE	Use scaling facotr DOUBLE to approximate partition function, \n"); 
	printf("                        default value is 1.07 for sequences with more than 100 nt and zero for shorter sequences.\n");
	printf("   --parallelsample     Paralellizes the sampling of each individual structure.\n");
	printf("			Only valid in combination with --sample.\n");
	printf("   --separatectfiles [--ctfilesdir DIR] [--summaryfile NAME] Writes each sampled structure to a separate .ct file \n");
	printf("			in the DIR directory. Also writes a summary of the sampled structures to NAME in DIR.\n");
	printf("                        Default directory is the working directory specified with -w, and the default summary file\n");
	printf("                        name is stochaSampleSumary.txt Only valid in combination with --sample. \n");
	printf("   --advancedouble INT	Directs Partition Function and Sampling calculation to use\n");
	printf("			INT=1 native double, INT=2 BigNum, INT=3 hybrid, or INT=4 BigNumOptimized.\n");
	printf("			If this option not used then program will use the best setting depending on sequence length.\n");
	printf("   --bignumprecision INT	Precision used in case BigNum, hybrid, and BigNumOptimized. Default value is 512.\n");
	printf("			Minimum value is 64, and precision is ignored if using --advancedouble 1.\n");
	printf("\nSetting default parameter directory:\n");
	printf("\tTo run properly, GTfold requires access to a set of parameter files. If you are using one of the prepackaged binaries, you may need (or chose) to \n");
	printf("\tset the GTFOLDDATADIR environment variable to specify the directory in whihc GTfold should look to find default parameter files. In a terminal \n");
	printf("\twindow, use either the command \n");
	printf("\t\texport GTFOLDDATADIR=DIR\n");
	printf("\t\tfor BASH shell users, or \n");
	printf("\t\tsetenv GTFOLDDATADIR=DIR\n");
	printf("\t\tfor tcsh shell users. Alternatively, you may use the --paramdir option described above. \n");
	printf("\tGTfold will by default look for parameter files in the following directories: \n");
	printf("\t\t(1)      The directory pointed to by environment variable GTFOLDDATADIR \n");
	printf("\t\t(2)      The install directory (eg. /usr/local/share/gtfold), if (1) fails. \n");
	printf("\t\t(3)      The subdirectory 'data' of the current directory, if (1) and (2) fail. \n");
	printf("\n");
}

static void print_examples(){
	printf("\n\nEXAMPLES:\n\n");
	printf("1. Sample structures stochastically:\n\n");
	printf("gtboltzmann [-s INT] [[-d 0|2]|[-dS]] [-t n] [-o outputPrefix] [-v] [--estimatebpp] [-p DIR] [-w DIR] [-l] [--useSHAPE FILE] <seq_file>\n\n");
	printf("2. Calculate base pair probabilities:\n\n");
	printf("gtboltzmann --bpp [-d 2] [-o outputPrefix] [-v] [-p DIR] [-w DIR] [-l] [--useSHAPE FILE] <seq_file>\n\n");
	printf("\n\n");
}

static void print_examples_developer_options(){
	printf("\n\nDeveloper Options EXAMPLES:\n\n");
	printf("1. Calculate Partition function:\n\n");
	printf("gtboltzmann [--partition] [[-d 0|2]|[-dS]] [-t n] [-o outputPrefix] [--exactintloop] [-v] [-p DIR] [-w DIR] [-l] [--scale DOUBLE] [--advancedouble INT] [--bignumprecision INT] [--useSHAPE FILE] <seq_file>\n\n");
	printf("2. Sample structures stochastically:\n\n");
	printf("gtboltzmann -s INT [[-d 0|2]|[-dS]] [-t n] [-o outputPrefix] [--exactintloop] [-v] [--groupbyfreq] [--estimatebpp] [--parallelsample] [-p DIR] [-w DIR] [-l] [--scale DOUBLE] [--advancedouble INT] [--bignumprecision INT] [--useSHAPE FILE] <seq_file>\n\n");
	printf("gtboltzmann -s INT [[-d 0|2]|[-dS]] -t 1 [-o outputPrefix] [--exactintloop] [-v] [--groupbyfreq] [--sampleenergy DOUBLE] [-e] [--checkfraction] [--estimatebpp] [--parallelsample] [-p DIR] [-w DIR] [-l] [--scale DOUBLE] [--advancedouble INT] [--bignumprecision INT] [--useSHAPE FILE] <seq_file>\n\n");
	printf("gtboltzmann -s INT --separatectfiles [--ctfilesdir dump_dir_path] [--summaryfile dump_summery_file_name] [-d 2] [--exactintloop] [-v] [-p DIR] [-w DIR] [-l] [--scale DOUBLE] [--advancedouble INT] [--bignumprecision INT] [--useSHAPE FILE] <seq_file>\n\n");
	printf("\n\n");
}


static void help() {
	print_usage();
	print_examples();
	exit(-1);
}

static void detailed_help(){
	print_usage();
	print_examples();
	print_usage_developer_options();
	print_examples_developer_options();
	exit(-1);
}

void boltzmann_printRunConfiguration(const char *cseq) {
	string seq = cseq;
	if(!SILENT) printf("\nRun Configuration:\n");

	if (PF_COUNT_MODE == true) {
		if(!SILENT) printf("+ running with --pfcount option\n");
	}
	if (BPP_ENABLED == true) {
		if(!SILENT) printf("+ running with --bpp option\n");
	}
	if(dangles==0 && !PF_COUNT_MODE){//if (CALC_PF_DO && !CALC_PF_DS && !CALC_PF_D2 && !PF_COUNT_MODE) 
		if(!SILENT) printf("+ running in dangle d0 mode\n");
	}
	if(dangles==-1 && CALC_PF_DS){//if (!CALC_PF_DO && CALC_PF_DS && !CALC_PF_D2) 
		if(!SILENT) printf("+ running in dangle dS mode\n");
	}
	if(dangles==2 && !PF_COUNT_MODE){//if (!CALC_PF_DO && !CALC_PF_DS && CALC_PF_D2)
		if(!SILENT) printf("- running in dangle d2 mode\n");
	}
	if (PARAM_DIR == true) {
		if(!SILENT) printf("+ running with customized param dir: %s\n",paramDir);
	}
	if (RND_SAMPLE == true) {
		if(!SILENT) printf("- running to calculate %d samples\n", num_rnd);
	}
	if (contactDistance != -1) {
		if(!SILENT) printf("- maximum contact distance: %d\n", contactDistance);
	}
	if(strcmp(shapeFile, "")){
                if(!SILENT) printf("- using SHAPE data file: %s\n", shapeFile);
        }

	if(!SILENT) printf("- thermodynamic parameters: %s\n", EN_DATADIR);
	if(!SILENT) printf("- input sequence file: %s\n", seqfile);
	if(!SILENT) printf("- sequence length: %d\n", (int)seq.length());
	if(!SILENT) printf("- output file: %s\n", outputFile);
	if(RND_SAMPLE) if(!SILENT) printf("- samples output file: %s\n", sampleOutFile);
	if(BPP_ENABLED) if(!SILENT) printf("- bpp output file: %s\n", bppOutFile);
	if(PF_PRINT_ARRAYS_ENABLED) if(!SILENT) printf("+ partition function array print output file: %s\n", pfArraysOutFile);
	if(print_energy_decompose==1) if(!SILENT) printf("+ energy decompose output file: %s\n", energyDecomposeOutFile);
	if(!SILENT) printf("- scale factor: %f\n", scaleFactor);
	if(!SILENT){
		if(PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER==1) printf("- Partition Function and Sampling calculation to use: native double\n");
		else if(PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER==2) printf("+ Partition Function and Sampling calculation to use: BigNum\n");
		else if(PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER==3) printf("+ Partition Function and Sampling calculation to use: hybrid of native double and bignum\n");
		else if(PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER==4) printf("+ Partition Function and Sampling calculation to use: BigNumOptimized\n");
	}
	if(!SILENT) if(PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER==2 || PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER==3 || PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER==4) printf("- bignum precision: %d\n ", g_bignumprecision);
	printf("\n");
}

static void validate_options(string seq){
	if(!SILENT) printf("\nValidating Options:\n");
	if(PF_COUNT_MODE){
		if(RND_SAMPLE){
			if(!SILENT) printf("Ignoring --sample Option with --pfcount option and Program will continue with --pfcount option only.\n\n");
			RND_SAMPLE = false;
		}
	}
	if(BPP_ENABLED){
		//do nothing
	}
	else if(CALC_PART_FUNC && !RND_SAMPLE){//partition function
		if(print_energy_decompose==1){
			if(!SILENT) printf("Ignoring the option -e or --energy, as it will be valid with --sample option.\n\n");
		}
		if(ST_D2_ENABLE_SCATTER_PLOT && !ST_D2_ENABLE_BPP_PROBABILITY){
			if(!SILENT) printf("Ignoring the option --groupbyfreq, as it will be valid with --sample option.\n\n");
		}
		if(ST_D2_ENABLE_UNIFORM_SAMPLE){
			if(!SILENT) printf("Ignoring the option --sampleenergy, as it will be valid with --sample option.\n\n");
		}
		if(ST_D2_ENABLE_CHECK_FRACTION){
			if(!SILENT) printf("Ignoring the option --checkfraction, as it will be valid with --sample option.\n\n");
		}
		if(ST_D2_ENABLE_BPP_PROBABILITY){
			if(!SILENT) printf("Ignoring the option --estimatebpp, as it will be valid with --sample option.\n\n");
		}
		//if(ST_D2_ENABLE_COUNTS_PARALLELIZATION){
		//      printf("Ignoring the option --counts-parallel, as it will be valid with --sample option.\n\n");
		//}
		if(ST_D2_ENABLE_ONE_SAMPLE_PARALLELIZATION){
			if(!SILENT) printf("Ignoring the option --parallelsample, as it will be valid with --sample option.\n\n");
		}
	}
	else if(!CALC_PART_FUNC && RND_SAMPLE){//sample
		//nothing to check
	}
	else if(CALC_PART_FUNC && RND_SAMPLE){//both partition function and sample
		//printf("Program proceeding with sampling as both partition function calculation and sampling calculation option are used.\n\n");
		CALC_PART_FUNC = false;
	}
	else if(!CALC_PART_FUNC && !RND_SAMPLE){//neither partition function nor sample
		printf("Program exiting as neither partition function calculation nor sampling calculation option is used.\n\n");
		help();
		exit(-1);	
	}

	printf("\n");
}

static bool isNumeric( const char* pszInput)
{
	int nNumberBase = 10;
	string base = "0123456789ABCDEF";
	string input = pszInput;

	return (input.find_first_not_of(base.substr(0, nNumberBase)) == string::npos);
}

static void parse_options(int argc, char** argv) {
	int i;

	for(i=1; i<argc; i++) {
		if(argv[i][0] == '-') {
			if(strcmp(argv[i], "--help") == 0 || strcmp(argv[i], "-h") == 0) {
				help(); 
			} else if(strcmp(argv[i], "--detailedhelp") == 0 ) {
				detailed_help();
			} else if (strcmp(argv[i], "--paramdir") == 0 || strcmp(argv[i], "-p") == 0) {
				if(i+1 < argc) {
					strcpy(paramDir, argv[++i]);
					PARAM_DIR = true;
				}
				else {
					help();
				}
			} else if(strcmp(argv[i], "--threads") == 0 || strcmp(argv[i], "-t") == 0) {
				if(i+1 < argc){
					g_nthreads = atoi(argv[++i]);
				}
				else help();
			} else if(strcmp(argv[i], "--bignumprecision") == 0 ) {
                                if(i+1 < argc){
                                        g_bignumprecision = atoi(argv[++i]);
					if(g_bignumprecision<64){
						printf("Error: Min value of bignumprecision required is 64, exiting..");
						help();
					}
                                }
                                else help();
                        } else if(strcmp(argv[i], "--output") == 0 || strcmp(argv[i], "-o") == 0) {
				if(i+1 < argc)
					strcpy(outputPrefix, argv[++i]);
				else
					help();
			} else if (strcmp(argv[i], "--workdir") == 0 || strcmp(argv[i], "-w") == 0) {
				if(i+1 < argc)//if(i < argc)
					strcpy(outputDir, argv[++i]);
				else
					help();
			} else if(strcmp(argv[i], "--bpp") == 0) {
				BPP_ENABLED = true;
				CALC_PART_FUNC = false;
			} else if (strcmp(argv[i],"--partition") == 0) {
				CALC_PART_FUNC = true;
			} else if (strcmp(argv[i],"--printarrays") == 0) {
				PF_PRINT_ARRAYS_ENABLED = true;
			} else if (strcmp(argv[i], "--verbose") == 0 || strcmp(argv[i], "-v") == 0) {
			        g_verbose = 1;
			}
			else if (strcmp(argv[i], "--energydetail") == 0 || strcmp(argv[i], "-e") == 0) {
				print_energy_decompose = 1;
			}
			else if (strcmp(argv[i], "--dangle") == 0 || strcmp(argv[i], "-d") == 0) {
				std::string cmd = argv[i];
				if(i+1 < argc) {//if(i < argc)
					dangles = atoi(argv[++i]);
					if (!(dangles == 0 || dangles == 2)) {
						dangles = 2;
						printf("Ignoring %s option as it accepts either 0 or 2, proceeding with taking value for dangle as 2\n", cmd.c_str());
					}
					if(dangles==0) CALC_PF_DO = true;
					else if(dangles==2) CALC_PF_D2 = true;
				} else
					help();
			}
			else if (strcmp(argv[i],"-dS") == 0) {
				CALC_PF_DS = true;  
				dangles=-1;
			} else if (strcmp(argv[i],"-d0") == 0) {
				CALC_PF_DO = true;
				dangles=0;  
			} else if (strcmp(argv[i],"-d2") == 0) {
				//help();
				CALC_PF_D2 = true;
				dangles=2;
			} else if(strcmp(argv[i],"--exactintloop") == 0){ 
				PF_D2_UP_APPROX_ENABLED = false;
			} else if(strcmp(argv[i],"--groupbyfreq") == 0){
				ST_D2_ENABLE_SCATTER_PLOT = true;
			} else if(strcmp(argv[i],"--sampleenergy") == 0){
				ST_D2_ENABLE_UNIFORM_SAMPLE = true;
				if(i+1 < argc){ST_D2_UNIFORM_SAMPLE_ENERGY = atof(argv[++i]);}//if(i < argc){ST_D2_UNIFORM_SAMPLE_ENERGY = atof(argv[++i]);}
				else help();
			} else if(strcmp(argv[i],"--scale") == 0){
				if(i+1 < argc){scaleFactor = atof(argv[++i]);}
				else help();
			} else if(strcmp(argv[i],"--checkfraction") == 0){
				ST_D2_ENABLE_CHECK_FRACTION = true;
			} else if(strcmp(argv[i],"--estimatebpp") == 0){ 
				ST_D2_ENABLE_BPP_PROBABILITY = true;
				ST_D2_ENABLE_SCATTER_PLOT = true;
			} else if(strcmp(argv[i],"--counts-parallel") == 0){
				ST_D2_ENABLE_COUNTS_PARALLELIZATION = true;
			} else if(strcmp(argv[i],"--parallelsample") == 0){ 
				ST_D2_ENABLE_ONE_SAMPLE_PARALLELIZATION = true;
			} else if (strcmp(argv[i],"--pfcount") == 0) {
				CALC_PART_FUNC = true;
				PF_COUNT_MODE = true;
			} else if (strcmp(argv[i], "--advancedouble") == 0) {
				if(i+1 < argc) {
					PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER = atoi(argv[++i]);
					if (PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER < 1 || PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER > 4) {
						help();  
					}
				} else
					help();
			} else if (strcmp(argv[i],"--sample") == 0 || strcmp(argv[i], "-s") == 0) {
				RND_SAMPLE = true;
				if(i+1 < argc){//if(i < argc)
					//if(is_int(argv[i+1]))		
					if(isNumeric(argv[i+1])){		
						num_rnd = atoi(argv[++i]);
					}
					else {
						printf("Error: %s is not a valid integer.\n\n",argv[i+1]);
						help();
					}
				}
				else
					help();
				if(i+1 < argc){//if(i < argc)//--separatectfiles [--ctfilesdir dump_dir_name] [--summaryfile dump_summery_file_name]
					//printf("i=%d, argc=%d, argv[i]=%s, \n",i,argc,argv[i]);
					if (strcmp(argv[i+1],"--separatectfiles") == 0){
						i=i+1;
						DUMP_CT_FILE = true;
						if (i+1 < argc && strcmp(argv[i+1],"--ctfilesdir") == 0){//if (i < argc && strcmp(argv[i+1],"--ctfilesdir") == 0)
							i=i+1;
							if(i+1 < argc)//if(i < argc)
								strcpy(ctFileDumpDir, argv[++i]);
							else
								help();
						}
						if (i+1 < argc && strcmp(argv[i+1],"--summaryfile") == 0){//if (i < argc && strcmp(argv[i+1],"--summaryfile") == 0)
							i=i+1;
							if(i+1 < argc)//if(i < argc)
								strcpy(stochastic_summery_file_name, argv[++i]);
							else
								help();
						}
					}
				}
			} else if (strcmp(argv[i],"--limitcd") == 0 || strcmp(argv[i], "-l") == 0) {
				if(i+1 < argc) {//if(i < argc)
					LIMIT_DISTANCE = true;
					contactDistance = atoi(argv[++i]);
				}
				else
					help();
			} else if (strcmp(argv[i], "--useSHAPE") == 0){
        			if( i+1 < argc){
          				strcpy(shapeFile, argv[++i]);
          				SHAPE_ENABLED = 1;
        			}
        			else
          				help();
      			}
			else{
				printf("Error: Option %s is Undefined option\n", argv[i]);
				help();
			}
		} else {
			strcpy(seqfile, argv[i]);
		}
	}

	if(!strcmp(seqfile, "")) {
		printf("Error: Missing input file.\n");
		help();
	}

	// If no output file specified, create one
	if(!strcmp(outputPrefix, "")) {
		// base it off the input file
		int outputPrefixLength = strlen(outputPrefix);
		if(outputPrefix[outputPrefixLength - 1] != '/') {
	             strcat(outputPrefix, "/");
		}
		strcat(outputPrefix, seqfile);

		size_t pos;
		// extract file name from the path
		const char *lastSlashPos = strrchr(outputPrefix, '/');
		if(lastSlashPos != NULL) {
		     char basename[256];
		     size_t slashIndex = lastSlashPos - &(outputPrefix[0]) + 1;
		     strcpy(basename, &(outputPrefix[slashIndex]));
		     strcpy(outputPrefix, basename);
		}
		//if ((pos=outputPrefix.find_last_of('/')) > 0) {
		//	outputPrefix = outputPrefix.substr(pos+1);
		//}

		// and if an extension exists, remove it ...
		const char *extPos = strrchr(outputPrefix, '.');
		if(extPos != NULL) {
		     size_t dotIndex = extPos - &(outputPrefix[0]) - 1;
		     outputPrefix[dotIndex] = '\0';
		}
		//if(outputPrefix.find(".") != string::npos)
		//	outputPrefix.erase(outputPrefix.rfind("."));
	}

	// If output dir specified
	if (!strcmp(outputDir, "")) {
		strcat(outputFile, outputDir);
		strcat(outputFile, "/");
		strcat(bppOutFile, outputDir);
		strcat(bppOutFile, "/");
		strcat(sampleOutFile, outputDir);
		strcat(sampleOutFile, "/");
		strcat(energyDecomposeOutFile, outputDir);
		strcat(energyDecomposeOutFile, "/");
		strcat(estimateBppOutputFile, outputDir);
		strcat(estimateBppOutputFile, "/");
		strcat(scatterPlotOutputFile, outputDir);
		strcat(scatterPlotOutputFile, "/");
		strcat(pfArraysOutFile, outputDir);
		strcat(pfArraysOutFile, "/");

	}
	// ... and append the .ct
	strcat(outputFile, outputPrefix);
	strcat(outputFile, ".ct");
	strcat(bppOutFile, outputPrefix);	
	strcat(bppOutFile, "_bpp.txt");
	strcat(sampleOutFile, outputPrefix);	
	strcat(sampleOutFile, ".samples");
	strcat(energyDecomposeOutFile, outputPrefix);	
	strcat(energyDecomposeOutFile, ".energy");
	strcat(estimateBppOutputFile, outputPrefix);	
	strcat(estimateBppOutputFile, ".sbpp");
	strcat(scatterPlotOutputFile, outputPrefix);	
	strcat(scatterPlotOutputFile, ".frequency");
	strcat(pfArraysOutFile, outputPrefix);
	strcat(pfArraysOutFile, ".pfarrays");

}
/*
   double get_seconds() {
   struct timeval tv;
   gettimeofday(&tv, NULL);
   return (double) tv.tv_sec + (double) tv.tv_usec / 1000000.0;
   }*/

int boltzmann_main(int argc, char** argv) {
	parse_options(argc, argv);
	validate_options(seqfile);
	if (read_sequence_file(seqfile, seq) == FAILURE) {
		printf("Failed to open sequence file: %s.\n\n", seqfile);
		exit(-1);
	}
	parse_mfe_options(argc, argv);
	init_fold(seq.c_str());
	g_LIMIT_DISTANCE = LIMIT_DISTANCE;
	g_contactDistance = contactDistance;

	readThermodynamicParameters(paramDir, PARAM_DIR, 0, 0, 0);

	// Debug 9/30/13
	// If length < 1000: do not use scaling
	if(scaleFactor==-1){//that is if scaleFactor is not input by the user, and we only need to decide for its default value
		if(seq.length() < 1000){
			scaleFactor=0.0;
		}
		else{
			scaleFactor=1.07;
		}
	}
	if(PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER==0){
		decideAutomaticallyForAdvancedDoubleSpecifier();
	}
	if(PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER==2 || PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER==3 || PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER==4){
		mpf_set_default_prec(g_bignumprecision);
	}
	
	boltzmann_printRunConfiguration(seq.c_str());

	if (LIMIT_DISTANCE) {
		if (seq.length() < (unsigned int)contactDistance) 
			printf("\nContact distance limit is higher than the sequence length. Continuing without restraining contact distance.\n");
		else printf("\nLimiting contact distance to %d\n",contactDistance);
	}
	if(scaleFactor!=0.0){
		//double mfe = calculate_mfe(argc, argv);
		double mfe = calculate_mfe(seq.length());
		cout<<"mfe "<<mfe<<endl;
		scaleFactor = scaleFactor*mfe;
	}
	

	if (CALC_PART_FUNC == true && CALC_PF_DS == true) {
		handleDsPartitionFunction();	
	}
	else if (CALC_PART_FUNC == true && CALC_PF_D2 == true) {
		handleD2PartitionFunction();	
	}  
	else if (CALC_PART_FUNC == true && CALC_PF_DO == true) {
		handleDsPartitionFunction();	
	}
	else if (CALC_PART_FUNC == true) {
		handleDsPartitionFunction();	
	} else if (RND_SAMPLE == true) {
		if(CALC_PF_D2 == true){
			handleD2Sample();
		}
		else{
			handleDsSample();	
		}
	} else if(BPP_ENABLED) {
		handleBpp();
	} else {
		printf("No valid option specified !\n\n");
		help();
	}

	free_fold(seq.length());
	printf("\n");
	return EXIT_SUCCESS;
}

void decideAutomaticallyForAdvancedDoubleSpecifier(){
	// Debug 9/30/13:
	// if length < 1000 use native double
	// else if length >= 1000 but scaling is default 1.07 use native double
	// else use BigNum computation
	//
	if(seq.length() < 1000)
	{
		PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER = 1;
	}
	else if (seq.length() >= 1000 && scaleFactor >= 1.07)
	{
		PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER = 1;
	}
	else
	{
		PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER = 4;
	}
	
	//if( seq.length()<1000 || (seq.length()>1000 && scaleFactor>=1.0) || (seq.length()>3000 && scaleFactor>=1.25)){
	/*if( seq.length()<=1000 || scaleFactor>=1.07 ){
		PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER=1;
	}
	else {
		PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER=4;
	}
	//else PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER=1;
	*/
}

static void handleD2PartitionFunction(){
	if( PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER==1 ){
		PartitionFunctionD2<AdvancedDouble_Native> pf_d2;
		computeD2PartitionFunction< PartitionFunctionD2< AdvancedDouble_Native > >(pf_d2);
	}
	else if( PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER==2 ){
		PartitionFunctionD2<AdvancedDouble_BigNum> pf_d2;
		computeD2PartitionFunction< PartitionFunctionD2< AdvancedDouble_BigNum > >(pf_d2);
	}
	else if( PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER==3 ){
		PartitionFunctionD2<AdvancedDouble_Hybrid> pf_d2;
		computeD2PartitionFunction< PartitionFunctionD2< AdvancedDouble_Hybrid > >(pf_d2);
	}
	else if( PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER==4 ){
		PartitionFunctionD2<AdvancedDouble_BigNumOptimized> pf_d2;
		computeD2PartitionFunction< PartitionFunctionD2< AdvancedDouble_BigNumOptimized > >(pf_d2);
	}

}
	
template <class T>
static void computeD2PartitionFunction(T pf_d2){
	int pf_count_mode = 0;
        if(PF_COUNT_MODE) pf_count_mode=1;
        int no_dangle_mode = 0;
        if(CALC_PF_DO) no_dangle_mode=1;
        //printf("\nComputing partition function in -d2 mode ..., pf_count_mode=%d, no_dangle_mode=%d, PF_D2_UP_APPROX_ENABLED=%d\n", pf_count_mode, no_dangle_mode,PF_D2_UP_APPROX_ENABLED);
	printf("\nComputing partition function...\n");
	t1 = get_seconds();
	pf_d2.calculate_partition(seq.length(),pf_count_mode,no_dangle_mode,PF_D2_UP_APPROX_ENABLED,scaleFactor);
	t1 = get_seconds() - t1;
	printf("partition function computation running time: %f seconds\n", t1);
	if(PF_PRINT_ARRAYS_ENABLED) pf_d2.printAllMatrixesToFile(pfArraysOutFile);
	pf_d2.free_partition();
}

static void handleD2Sample(){
	if( PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER==1 ){
		StochasticTracebackD2<AdvancedDouble_Native> st_d2;
        	computeD2Sample< StochasticTracebackD2< AdvancedDouble_Native > >(st_d2);
        }
        else if( PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER==2 ){
		StochasticTracebackD2<AdvancedDouble_BigNum> st_d2;
        	computeD2Sample< StochasticTracebackD2< AdvancedDouble_BigNum > >(st_d2);
        }
        else if( PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER==3 ){
		StochasticTracebackD2<AdvancedDouble_Hybrid> st_d2;
        	computeD2Sample< StochasticTracebackD2< AdvancedDouble_Hybrid > >(st_d2);
        }
	else if( PF_ST_D2_ADVANCED_DOUBLE_SPECIFIER==4 ){
		StochasticTracebackD2<AdvancedDouble_BigNumOptimized> st_d2;
        	computeD2Sample< StochasticTracebackD2< AdvancedDouble_BigNumOptimized > >(st_d2);
        }

}

template <class T>
static void computeD2Sample(T st_d2){
	printf("\nComputing stochastic traceback...\n");
	int pf_count_mode = 0;
	if(PF_COUNT_MODE) pf_count_mode=1;
	int no_dangle_mode = 0;
	if(CALC_PF_DO) no_dangle_mode=1;
	t1 = get_seconds();
	st_d2.initialize(seq.length(), pf_count_mode, no_dangle_mode, print_energy_decompose, PF_D2_UP_APPROX_ENABLED,ST_D2_ENABLE_CHECK_FRACTION, energyDecomposeOutFile,scaleFactor);
	t1 = get_seconds() - t1;
	printf("D2 Traceback initialization (partition function computation) running time: %f seconds\n", t1);
	t1 = get_seconds();
	if(DUMP_CT_FILE==false){
		if(ST_D2_ENABLE_COUNTS_PARALLELIZATION && g_nthreads!=1)
			st_d2.batch_sample_parallel(num_rnd,ST_D2_ENABLE_SCATTER_PLOT,ST_D2_ENABLE_ONE_SAMPLE_PARALLELIZATION,ST_D2_ENABLE_BPP_PROBABILITY, sampleOutFile, estimateBppOutputFile, scatterPlotOutputFile);
		else st_d2.batch_sample(num_rnd,ST_D2_ENABLE_SCATTER_PLOT,ST_D2_ENABLE_ONE_SAMPLE_PARALLELIZATION,ST_D2_ENABLE_UNIFORM_SAMPLE,ST_D2_UNIFORM_SAMPLE_ENERGY,ST_D2_ENABLE_BPP_PROBABILITY, sampleOutFile, estimateBppOutputFile, scatterPlotOutputFile);
	}
	else  st_d2.batch_sample_and_dump(num_rnd, ctFileDumpDir, stochastic_summery_file_name, seq, seqfile);
	t1 = get_seconds() - t1;
	printf("D2 Traceback computation running time: %f seconds\n", t1);
	if(PF_PRINT_ARRAYS_ENABLED) st_d2.printPfMatrixesToFile(pfArraysOutFile);
	st_d2.free_traceback();
}


static void handleDsPartitionFunction(){
	int pf_count_mode = 0;
	if(PF_COUNT_MODE) pf_count_mode=1;
	int no_dangle_mode = 0;
	if(CALC_PF_DO) no_dangle_mode=1;
	//printf("\nComputing partition function in -dS mode ..., pf_count_mode=%d, no_dangle_mode=%d\n", pf_count_mode, no_dangle_mode);
	printf("\nComputing partition function...\n");
	t1 = get_seconds();
	calculate_partition(seq.length(),pf_count_mode,no_dangle_mode);
	t1 = get_seconds() - t1;
	printf("partition function computation running time: %9.6f seconds\n", t1);
	//calculate_partition(seq.length(),0,0);
	free_partition();
}

static void handleDsSample(){
	int pf_count_mode = 0;
	if(PF_COUNT_MODE) pf_count_mode=1;
	int no_dangle_mode = 0;
	if(CALC_PF_DO) no_dangle_mode=1;
	//printf("\nComputing stochastic traceback in -dS mode ..., pf_count_mode=%d, no_dangle_mode=%d\n", pf_count_mode, no_dangle_mode);
	printf("\nComputing stochastic traceback...\n");
	double U = calculate_partition(seq.length(),pf_count_mode,no_dangle_mode);
	t1 = get_seconds();
	if(DUMP_CT_FILE==false) batch_sample(num_rnd, seq.length(), U);
	else batch_sample_and_dump(num_rnd, seq.length(), U, ctFileDumpDir, stochastic_summery_file_name, seq, seqfile); 
	t1 = get_seconds() - t1;
	printf("Traceback computation running time: %9.6f seconds\n", t1);
	free_partition();
}

static void handleBpp(){
	printf("\n");
	printf("Calculating partition function\n");
	double ** Q,  **QM, **QB, **P;
	Q = mallocTwoD(seq.length() + 1, seq.length() + 1);
	QM = mallocTwoD(seq.length() + 1, seq.length() + 1);
	QB = mallocTwoD(seq.length() + 1, seq.length() + 1);
	P = mallocTwoD(seq.length() + 1, seq.length() + 1);


	fill_partition_fn_arrays(seq.length(), Q, QB, QM);
	fillBasePairProbabilities(seq.length(), Q, QB, QM, P);
	printBasePairProbabilitiesDetail(seq.length(), structure, P, bppOutFile);
	printf("Saved BPP output in %s\n",bppOutFile);

	freeTwoD(Q, seq.length() + 1, seq.length() + 1);
	freeTwoD(QM, seq.length() + 1, seq.length() + 1);
	freeTwoD(QB, seq.length() + 1, seq.length() + 1);
	freeTwoD(P, seq.length() + 1, seq.length() + 1);
}
