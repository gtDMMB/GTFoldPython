#include "loader.h"
#include "options.h"

#include <sstream>

using namespace std;

int ILSA;
int NOISOLATE;
int PARAM_DIR = false;
int LIMIT_DISTANCE;
int BPP_ENABLED;
int SUBOPT_ENABLED;
int CONS_ENABLED = false;
int VERBOSE = false;
int SILENT = true;
int  SHAPE_ENABLED = 0;
int T_MISMATCH = false;
int UNAMODE = false;
int RNAMODE = false;
int b_prefilter = false;
int CALC_PART_FUNC = false;
int RND_SAMPLE = false;
int PF_COUNT_MODE = false;
int DEBUG = false;

char seqfile[256] = "";
char outputPrefix[256] = "";
char outputDir[256] = "";
char outputFile[256] = "";
char paramDir[256] = ""; // default value
char bppOutFile[256] = "";
char shapeFile[256] = "";
char suboptFile[256] = "";
char constraintsFile[256] = "";

int num_rnd = 0;
int dangles=-1;
int prefilter1=2;
int prefilter2=2;

float suboptDelta = 0.0;
int nThreads = -1;
int contactDistance = -1;

