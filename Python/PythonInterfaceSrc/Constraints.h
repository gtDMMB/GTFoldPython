/* Constraints.h : C-type definitions and parser functions for the input 
 *                 Python-type constraints;
 * Author: Maxie D. Schmidt (maxieds@gmail.com)
 * Created: 2020.01.09
 */

#ifndef __CONSTRAINTS_H__
#define __CONSTRAINTS_H__

#include "PythonConfig.h"

struct _MFEStructRuntimeArgs_t;
//typedef struct _MFEStructRuntimeArgs_t _MFEStructRuntimeArgs_t;

#define P                            ((int) 0x00000000) //((short) 80) //((short) 'P')
#define F                            ((int) 0x01010101) //((short) 70) //((short) 'F')

// Each constraint is specified as a 3-tuple, [i, j, k]: 
// Constraint types:
// F i 0 k   # Force nucleotides i...i+k-1 to be paired
// F i j k   # Force helix of size k starting with (i,j) to be formed
// P i 0 k   # Prohibit nucleotides i...i+k-1 to be paired
// P i j k   # Prohibit pairs (i,j),...,(i+k-1,j-k+1)
// Constraint syntax:
// F i j k   # force (i,j)(i+1,j-1),.......,(i+k-1,j-k+1) pairs.
// P i j k   # prohibit (i,j)(i+1,j-1),.......,(i+k-1,j-k+1) pairs.
// P i 0 k   # make bases from i to i+k-1 single stranded bases.
typedef struct {
     int consType;
     int i; 
     int j; 
     int k;
} Constraint_t;

typedef int ConsCType_t[4];
typedef int ConsListCType_t[][4];

Constraint_t ParseSingleConstraint(ConsCType_t consTypeArr);
Constraint_t * ParseConstraintsList(ConsListCType_t consList, int consLength);

int CountForcedConstraints(Constraint_t *consList, int consLength);
int CheckForcedConstraintValid(Constraint_t cons, int prevConsLength, int baseSeqLength);
int ParseForcedConstraint(Constraint_t cons, int prevConsLength);

int CountProhibitedConstraints(Constraint_t *consList, int consLength);
int CheckProhibitedConstraintValid(Constraint_t cons, int prevConsLength, int baseSeqLength);
int ParseProhibitedConstraint(Constraint_t cons, int prevConstLength);

int LoadGTFoldConstraints(Constraint_t *consList, int consLength, int baseSeqLength);
int InitGTFoldConstraints(struct _MFEStructRuntimeArgs_t *rtArgs);
void PrintGTFoldConstraints(Constraint_t *consList, int numCons);
void FreeGTFoldConstraints(int numCons);

// Implements a structure to store individual SHAPE constraints:
typedef struct {
     int basePos;
     double shape;
} SHAPEConstraint_t;

int LoadGTFoldSHAPEConstraints(SHAPEConstraint_t *scList, int sconsLength, int baseSeqLength);
void PrintGTFoldSHAPEConstraints(SHAPEConstraint_t *scList, int numCons);

#endif
