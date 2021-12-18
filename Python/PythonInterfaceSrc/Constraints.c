/* Constraints.c : GTFold constraints initialization methods and local storage;
 * Author: Maxie D. Schmidt (maxieds@gmail.com)
 * Created: 2020.01.22
 */

#include <stdlib.h>
#include <stdio.h>
#include <ctype.h>

#include "include/constraints.h"
#include "include/constants.h"
#include "include/main-c.h"
#include "include/mfe_main.h"
#include "include/options.h"
#include "include/shapereader.h"
#include "include/global.h"

#include "Constraints.h"
#include "ErrorHandling.h"
#include "Utils.h"
#include "MFEStruct.h"

Constraint_t ParseSingleConstraint(ConsCType_t consTypeArr) {
     Constraint_t cons = (Constraint_t) {
           consTypeArr[0], 
   	      consTypeArr[1],
	      consTypeArr[2],
	      consTypeArr[3]
     };
     return cons;
}

Constraint_t * ParseConstraintsList(ConsListCType_t consList, int consLength) {
     if(consList == NULL || sizeof(consList) == 0 || consLength < 0) {
          SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CARGS, NULL);
	  return NULL;
     }
     Constraint_t *consArr = (Constraint_t *) malloc(consLength * sizeof(Constraint_t));
     if(consArr == NULL) {
	  SetLastErrorCode(GTFPYTHON_ERRNO_NOMEM, NULL);
	  return NULL;
     }
     for(int ci = 0; ci < consLength; ci++) {
          consArr[ci] = ParseSingleConstraint(consList[ci]);
     }
     return consArr;
}

int CountForcedConstraints(Constraint_t *consList, int consLength) {
     int fconsCount = 0;
     for(int ci = 0; ci < consLength; ci++) {
           if(consList[ci].consType == F) fconsCount++;
     }
     return fconsCount;
}

int CheckForcedConstraintValid(Constraint_t cons, int prevConsLength, int baseSeqLength) {
     char consError[STR_BUFFER_SIZE];
     if(cons.i < 1 || cons.i >= baseSeqLength - TURN) {
          sprintf(consError, "\nBase %d from constraint 'F %d %d %d' is out of bounds: "
			     "For constraint 'F i j k' value i must be between 1 and the sequence length - %d, "
			     "where the sequence length is %d \n",
                             cons.i, cons.i, cons.j, cons.k, TURN, baseSeqLength);
          SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CONSTRAINT, consError);
	  return ErrorCodeErrno.errorCode;
     }	  
     if(cons.j != 0 && (cons.j <= cons.i + TURN || cons.j > baseSeqLength)) {
          sprintf(consError, "\nBase %d from constraint 'F %d %d %d' has an illegal value: "
			     "For constraint 'F i j k' value j must be either 0 or between "
			     "i + %d and the sequence length of %d \n",
                             cons.j, cons.i, cons.j, cons.k, TURN, baseSeqLength);
          SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CONSTRAINT, consError);
	  return ErrorCodeErrno.errorCode;
     }
     if(cons.k < 1) {
          sprintf(consError, "\nValue %d from constraint 'F %d %d %d' is too small: "
			     "For constraint 'F i j k' value k must be at least 1\n",
                             cons.j, cons.i, cons.j, baseSeqLength);
	  SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CONSTRAINT, consError);
	  return ErrorCodeErrno.errorCode;
     }
     if(cons.j != 0 && (cons.j - cons.i - 2 * cons.k + 2 <= TURN)) {
          sprintf(consError, "\nValue %d from constraint 'F %d %d %d' is too large: "
			     "For constraint 'F i j k' the values must satisfy the inequality (j-k+1)-(i+k-1) > %d \n",
                             cons.k, cons.i, cons.j, cons.k, TURN);
	  SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CONSTRAINT, consError);
	  return ErrorCodeErrno.errorCode;
     }
     if(cons.j == 0 && (cons.i + cons.k - 1 > baseSeqLength)) {
          sprintf(consError, "\nValue %d from constraint 'F %d %d %d' is too large: "
			     "For constraint 'F i 0 k' the value i + k  - 1 can be at most the "
			     "sequence length, in this case %d \n",
			     cons.k, cons.i, cons.j, cons.k, baseSeqLength);
	  SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CONSTRAINT, consError);
	  return ErrorCodeErrno.errorCode;
     }
     return GTFPYTHON_ERRNO_OK;
}

int ParseForcedConstraint(Constraint_t cons, int prevConsLength) {
     //FBP[prevConsLength][0] = (((int) cons.i) << 16) | cons.j;
     //FBP[prevConsLength][1] = ((int) cons.k) << 16;
     FBP[prevConsLength][0] = (int) cons.i;
     FBP[prevConsLength][1] = (int) cons.j;
     FBP[prevConsLength][2] = (int) cons.k;
     return GTFPYTHON_ERRNO_OK;
}

int CountProhibitedConstraints(Constraint_t *consList, int consLength) {
     int pconsCount = 0;
     for(int ci = 0; ci < consLength; ci++) {
           if(consList[ci].consType == P) pconsCount++;
     }
     return pconsCount;
}
int CheckProhibitedConstraintValid(Constraint_t cons, int prevConsLength, int baseSeqLength) {
     char consError[STR_BUFFER_SIZE];
     if(cons.i < 1 || (cons.j != 0 && cons.i >= baseSeqLength - TURN)) {
          sprintf(consError, "\nBase %d from constraint 'P %d %d %d' is out of bounds: "
			      "For constraint 'P i j k' value i must be between 1 and the sequence length - %d, "
			      "where the sequence length is %d \n",
                              prevConsLength, cons.i, cons.i, cons.j, cons.k, TURN, baseSeqLength);
	  SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CONSTRAINT, consError);
	  return ErrorCodeErrno.errorCode;
     }
     if(cons.j != 0 && (cons.j <= cons.i + TURN || cons.j > baseSeqLength)) {
          sprintf(consError, "\nBase %d from constraint 'P %d %d %d' has an illegal value: "
			     "For constraint 'P i j k' value j must be either 0 or between i + %d "
			     "and the sequence length of %d \n", 
			     prevConsLength, cons.j, cons.i, cons.j, cons.k, TURN, baseSeqLength);
	  SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CONSTRAINT, consError);
     	  return ErrorCodeErrno.errorCode;
     }
     if(cons.k < 1) {
          sprintf(consError, "\nValue %d from constraint 'P %d %d %d' is too small: "
			     "For constraint 'P i j k' value k must be at least 1\n", 
			     prevConsLength, cons.j, cons.i, cons.j, baseSeqLength);
	  SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CONSTRAINT, consError);
	  return ErrorCodeErrno.errorCode;
     }
     if(cons.j != 0 && (cons.j - cons.i - 2 * cons.k + 2 <= TURN)) {
          sprintf(consError, "\nValue %d from constraint 'P %d %d %d' is too large: "
			     "For constraint 'P i j k' the values must satisfy the inequality "
			     "(j-k+1)-(i+k-1) > %d \n", 
			     prevConsLength, cons.k, cons.i, cons.j, cons.k, TURN);
	  SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CONSTRAINT, consError);
	  return ErrorCodeErrno.errorCode;
     }
     if(cons.j == 0 && (cons.i + cons.k - 1 > baseSeqLength)) {
          sprintf(consError, "\nValue %d from constraint 'P %d %d %d' is too large: "
			     "For constraint 'P i 0 k' the value i + k  - 1 can be at "
			     "most the sequence length, in this case %d \n", 
			     prevConsLength, cons.k, cons.i, cons.j, cons.k, baseSeqLength);
	  SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CONSTRAINT, consError);
	  return ErrorCodeErrno.errorCode;
     }
     return GTFPYTHON_ERRNO_OK;
}

int ParseProhibitedConstraint(Constraint_t cons, int prevConsLength) {
     //int lowerInt = cons.i, upperInt = cons.k;
     //lowerInt = ((lowerInt << 16) & 0xffff0000) | cons.j;
     //PBP[prevConsLength][0] = lowerInt;
     //upperInt = (upperInt << 16) & 0xffff0000;
     //PBP[prevConsLength][1] = upperInt;
     //
     //PBP[prevConsLength][0] = (((int) cons.i) << 16) | cons.j;
     //PBP[prevConsLength][1] = ((int) cons.k) << 16;
     PBP[prevConsLength][0] = (int) cons.i;
     PBP[prevConsLength][1] = (int) cons.j;
     PBP[prevConsLength][2] = (int) cons.k;
     return GTFPYTHON_ERRNO_OK;
}

int LoadGTFoldConstraints(Constraint_t *consList, int consLength, int baseSeqLength) {
     if(consList == NULL || sizeof(consList) == 0 || consLength == 0) {
	     return GTFPYTHON_ERRNO_OK; // No normal constraints ... 
     }
     nFBP = CountForcedConstraints(consList, consLength);
     nPBP = CountProhibitedConstraints(consList, consLength);
     if(nFBP + nPBP == 0) {
	     SetLastErrorCode(GTFPYTHON_ERRNO_OK, "No Constraints found.");
	     return ErrorCodeErrno.errorCode;
     }
     FBP = (int **) calloc(nFBP, sizeof(int *));
     PBP = (int **) calloc(nPBP, sizeof(int *));
     int fit = 0, pit = 0, it = 0;
     for (it = 0; it < nFBP; it++) {
          FBP[it] = (int *) calloc(2, sizeof(int));
     }
     for(it = 0; it < nPBP; it++) {
          PBP[it] = (int *) calloc(2, sizeof(int));
     }
     int fcCount = 0, pcCount = 0;
     for(int ci = 0; ci < consLength; ci++) {
	  if(CheckForcedConstraintValid(consList[ci], ci, baseSeqLength)) {
          return GTFPYTHON_ERRNO_INVALID_CONSTRAINT;
       }
       int addConsStatus = GTFPYTHON_ERRNO_OK;
          if(consList[ci].consType == F && 
	      !CheckForcedConstraintValid(consList[ci], ci, baseSeqLength)) {
	       addConsStatus = ParseForcedConstraint(consList[ci], fcCount++);
	  }
	  else if(consList[ci].consType == P && 
	          !CheckProhibitedConstraintValid(consList[ci], ci, baseSeqLength)) {
               addConsStatus = ParseProhibitedConstraint(consList[ci], pcCount++);
	  } 
	  else if(consList[ci].consType != F && consList[ci].consType != P) {
	       SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CONSTRAINT, 
		                "Invalid constraint char type specified.");
	       return ErrorCodeErrno.errorCode;
	  }
	  if(addConsStatus != GTFPYTHON_ERRNO_OK) {
	       return addConsStatus;
	  }
     }
     SetLastErrorCode(GTFPYTHON_ERRNO_OK, NULL);
     return ErrorCodeErrno.errorCode;

}

int InitGTFoldConstraints(struct _MFEStructRuntimeArgs_t *rtArgs) {
     if(rtArgs == NULL) {
          return GTFPYTHON_ERRNO_INVALID_CARGS;
     }
     if(rtArgs ->numConstraints > 0 || rtArgs->numSHAPEConstraints > 0) {
          CONS_ENABLED = 1;
          enable_constraints(true);
     }
     else {
          CONS_ENABLED = 0;
          enable_constraints(false);
          SetLastErrorCode(GTFPYTHON_ERRNO_OK, NULL);
          return GTFPYTHON_ERRNO_OK;
     }
     int baseSeqLength = rtArgs->numBases;
     int loadConsStatus = LoadGTFoldConstraints(rtArgs->mfeConstraints, rtArgs->numConstraints, baseSeqLength);
     if(loadConsStatus != GTFPYTHON_ERRNO_OK) {
          return loadConsStatus;
     }
     loadConsStatus = LoadGTFoldSHAPEConstraints(rtArgs->mfeSHAPEConstraints, rtArgs->numSHAPEConstraints, baseSeqLength);
     if(loadConsStatus != GTFPYTHON_ERRNO_OK) {
	     return loadConsStatus;
     }
     // initialize extern'ed varaibles:
     int i, j, it, k, a, b;
     ind = (int *) calloc((baseSeqLength + 1), sizeof(int));
     if (ind == NULL) {
          SetLastErrorCode(GTFPYTHON_ERRNO_NOMEM, "Cannot allocate variable 'ind'");
	     return ErrorCodeErrno.errorCode;
     }
     for(i = 1; i <= baseSeqLength; i++){
          ind[i] = (i * (i - 1)) >>  1; // n * (n - 1) / 2
     }
     int LLL =((baseSeqLength + 1) * baseSeqLength) / 2 + 1;    
     BP = (int *) calloc(LLL, sizeof(int));
     if(BP == NULL) {
          SetLastErrorCode(GTFPYTHON_ERRNO_NOMEM, "Cannot allocate variable 'constraints'");
	     return ErrorCodeErrno.errorCode;
     }
     // ZS: initialize all basepairing constraints to 0 (default is nothing known)
     for(i = 0; i < LLL; i++){
          BP[i] = 0;
     }
     // ZS: for ambiguous bases (right now this only handles 'N' and 'X'), force single-stranded. 
     for(i = 1; i <= baseSeqLength; i++){
          if(RNA[i] == 'N' || RNA[i] == 'X'){
               // force single-stranded
               BP(i, i) = 3;
               // Prohibit pairing with anything else
               for(j = i + 1; j <= baseSeqLength; j++){
                    BP(i, j) = 2;
               }
          }
     }
     // CM: set forced basepairs
     char consError[STR_BUFFER_SIZE];
     for(it = 0; it < nFBP; it++) {

           if(FBP[it][1] == 0){ // OF THE FORM: F i 0 k
                // For bases i through i+k-1, say they must be in some pair
                for (i = FBP[it][0]; i < FBP[it][0] + FBP[it][2]; i++) {
                     if(BP(i, i) == 0){
                          BP(i, i) = 6;
                     }
                     // NOTE: If BP(i, i) == 4 or 6, ignore
                }
           }
           else {  // OF THE FORM: F i j k, j != 0
                   // => Require the stack from (i,j) to (i+k-1,j-k+1)
                for(k = 1; k <= FBP[it][2]; k++) {

                     i = FBP[it][0] + k - 1;
                     j = FBP[it][1] - k + 1;

                     if(BP(i, i) == 4 && BP(i, j) != 1) { // Base i is already in a pair
                          sprintf(consError, "Constraint 'F %d %d %d' is trying to force the pair "
					     "(%d,%d), but base %d is forced to be in a different pair "
				             "by a previous 'F i j k' constraint\n",
                                             FBP[it][0], FBP[it][1], FBP[it][2], i, j, i);
			  SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CONSTRAINT, consError);
	                  return ErrorCodeErrno.errorCode;
		     }
                     else if(BP(j, j) == 4 && BP(i, j) != 1) { // Base j is already in a pair
                          sprintf(consError, "Constraint 'F %d %d %d' is trying to force the pair "
					     "(%d,%d), but base %d is forced to be in a different pair "
				             "by a previous 'F i j k' constraint\n",
                                             FBP[it][0], FBP[it][1], FBP[it][2], i, j, j);
			  SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CONSTRAINT, consError);
	                  return ErrorCodeErrno.errorCode;
		     }
                     else if(BP(i, j) == 2) { // Pseudoknot!
                          sprintf(consError, "Constraint 'F %d %d %d' is trying to force the pair "
					     "(%d,%d), but this pair conflicts with a previous 'F i j k' "
					     "constraint\n\n",
                                             FBP[it][0], FBP[it][1], FBP[it][2], i, j);
			  SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CONSTRAINT, consError);
	                  return ErrorCodeErrno.errorCode;
                    }
                    else if(!canPair(RNA[i], RNA[j])) {
                         sprintf(consError, "Constraint 'F %d %d %d' is trying to force the pair "
					    "(%d,%d), but the pair is non-canonical\n",
                                            FBP[it][0], FBP[it][1], FBP[it][2], i, j);
			 SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CONSTRAINT, consError);
	                 return ErrorCodeErrno.errorCode;
                    }
                    else {
                         // Require the pair (i,j)
                         BP(i, i) = 4;
                         BP(j, j) = 4;
                         BP(i, j) = 1;
                         // Nothing else can pair with i or j, and no pseudoknots
                         for(b = i + 1; b < j; b++) {
                              BP(i, b) = 2;
                              BP(b, j) = 2;
                         }
                         // To avoid rewriting, these only need to be set for k = 1
                         if(k == 1) {
                              for(a = 1; a < i; a++) {
                                   for (b = i; b <= j; b++) {
                                        BP(a, b) = 2;
                                   }
                              }
                              for (a = i; a <= j; a++) {
                                   for (b = j + 1; b <= baseSeqLength; b++) {
                                        BP(a, b) = 2;
                                   }
                              }
                         }
		    }
		}
	   }     
     }
     // CM: set prohibited basepairs
     for(it = 0; it < nPBP; it++){

           if(PBP[it][1] != 0) { // OF THE FORM: P i j k, j != 0
                                  // => Prohibit the stack (i,j) to (i+k-1,j-k+1)
                for(k = 1; k <= PBP[it][2]; k++) {
                     i = PBP[it][0] + k - 1;
                     j = PBP[it][1] - k + 1;
                     // Pair (i,j) is required by some constraint
                     if(BP(i, j) == 1) {
                          sprintf(consError, "Constraint 'P %d %d %d' is trying to prohibit pair (%d,%d), "
					     "but this pair is required by a 'F i j k' constraint\n",
                                             PBP[it][0], PBP[it][1], PBP[it][2], i, j);
                          SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CONSTRAINT, consError);
	                  return ErrorCodeErrno.errorCode;
                     }
                     else {
                          BP(i,j) = 2;
                          BP(i,i) = 5; // This is only for the sake of print_constraints
                          BP(j,j) = 5; // This is only for the sake of print_constraints
                     }
                }
           }
           else { // OF THE FORM: P i 0 k
                  // => For bases i to i+k-1, say they must be single-stranded
                for (i = PBP[it][0]; i < PBP[it][0] + PBP[it][2]; i++) {
                     // Base i is in a required pair
                     if(BP(i, i) == 4 || BP(i, i) == 6) {
                          sprintf(consError, "Constraint 'P %d %d %d' is trying to prohibit base %d from being paired, "
					     "but this base is required to be paired by a 'F i j k' constraint\n",
                                             PBP[it][0], PBP[it][1], PBP[it][2], i);
                          SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CONSTRAINT, consError);;
	                  return ErrorCodeErrno.errorCode;
                     }
                     else {
                          BP(i, i) = 3;
                          for(a = 1; a < i; a++) {
                               BP(a, i) = 2;
                          }
                          for (a = i + 1; a <= baseSeqLength; a++) {
                               BP(i, a) = 2;
                          }
                     }    
		     }
		}
     }
     SetLastErrorCode(GTFPYTHON_ERRNO_OK, NULL);
     return ErrorCodeErrno.errorCode;

}

void PrintGTFoldConstraints(Constraint_t *consList, int numCons) {
     if(consList == NULL || sizeof(consList) == 0 || numCons <= 0) {
          return;
     }
     for(int ci = 0; ci < numCons; ci++) {
          fprintf(CONFIG_STDMSGOUT, "  >> CONS #% 3d: %c % 2d % 2d % 2d\n", ci + 1, 
		  consList[ci].consType, consList[ci].i, consList[ci].j, consList[ci].k);
     }
     fprintf(CONFIG_STDMSGOUT, "\n");
     //print_constraints(numCons);
}

void FreeGTFoldConstraints(int numCons) {
     free_constraints(numCons);
}

int LoadGTFoldSHAPEConstraints(SHAPEConstraint_t *scList, int sconsLength, int baseSeqLength) {
     if(scList == NULL) { // No SHAPE constraints ... 
	   return GTFPYTHON_ERRNO_OK;
     }
     else if(sconsLength < 0 || baseSeqLength <= 0) {
          SetLastErrorCode(GTFPYTHON_ERRNO_INVALID_CARGS, NULL);
	     return ErrorCodeErrno.errorCode;
     }
     // a wrapper around GTFold's shapereader.cc::readSHAPEarray:
     SHAPE_ENABLED = 1;
     SHAPEarray = (double *) calloc(baseSeqLength + 1, sizeof(double));
     SHAPEenergies = (int *) calloc(baseSeqLength + 1, sizeof(int));
     for(int bi = 0; bi < baseSeqLength; bi++) {
          SHAPEarray[bi] = -999;
	  SHAPEenergies[bi] = 0;
     }
     int opStatus = GTFPYTHON_ERRNO_OK;
     for(int ci = 0; ci < sconsLength; ci++) {
          int consPos = scList[ci].basePos;
	     double shapeNum = scList[ci].shape;
	     if(consPos <= baseSeqLength) {
               SHAPEarray[consPos] = shapeNum;
	          SHAPEenergies[consPos] = calcShapeEnergy(shapeNum);
	     }
	     else {
	          if(!*CONFIG_QUIET) {
	               fprintf(CONFIG_STDMSGOUT, 
			             "Invalid SHAPE position indicator (ignoring line): [#%d] %d, %g\n", 
                             ci + 1, consPos, shapeNum);
	          }
	          opStatus = GTFPYTHON_ERRNO_INVALID_CONSTRAINT;
	     }
     }
     return opStatus;
}

void PrintGTFoldSHAPEConstraints(SHAPEConstraint_t *scList, int numCons) {
     if(scList == NULL || sizeof(scList) == 0 || numCons <= 0) {
          return;
     }
     for(int ci = 0; ci < numCons; ci++) {
          fprintf(CONFIG_STDMSGOUT, "  >> SHAPE CONS #% 3d: % 3d, %1.3g\n", ci + 1, 
		  scList[ci].basePos, scList[ci].shape);
     }
     fprintf(CONFIG_STDMSGOUT, "\n");
     //print_constraints(numCons);
}
