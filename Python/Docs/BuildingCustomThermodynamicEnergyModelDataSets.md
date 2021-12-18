# Creating custom energy models to load into GTFold

## Overview

The gtDMMB research group has been hard at work on [GTModify software](https://github.com/gtDMMB/GTModify), 
a C-sourced program that can modify the 
[energy model DAT files](https://github.gatech.edu/gtDMMB/GTFoldPython/blob/master/Python/Docs/ThermodynamicParameters.md#what-does-each-table-contain) as 
```
**.specification.dat indicates the alphabet and pairs.

*.coaxial.* are parameters for flush coaxial stacking where two helix ends stack without an intervening mismatch.

*.coaxstack.* are parameters for coaxial stacking of helices with an intervening mismatch. This is for the stack where the backbone is not continuous.

*.dangle.* are parameters for dangling ends on pairs.

*.hexaloop.* are parameters for hairpin loops of 6 unpaired nucleotides that have stabilities not well modeled by the parameters.

*.int11.* are parameters for 1×1 internal loops.

*.int21.* are parameters for 2×1 internal loops.

*.int22.* are parameters for 2×2 internal loops.

*.loop.* are parameters for loop initiations.

*.misloop.* are parameters that do not fit into other tables.

*.stack.* are parameters for helical stacking.

*.tloop.* are parameters for hairpin loops of 4 unpaired nucleotides that have stabilities not well modeled by the parameters.

*.triloop.* are parameters for hairpin loops of 3 unpaired nucleotides that have stabilities not well modeled by the parameters.

*.tstack.* are parameters for terminal mismatches in exterior loops.

*.tstackcoax.* are parameters for coaxial stacking of helices with an intervening mismatch. This is for the stack where the backbone is continuous.

*.tstackh.* are parameters for first mismtaches in hairpin loops.

*.tstacki.* are parameters for the mismatches in internal loops.

*.tstacki23.* are parameters for the mismatches in 2×3 internal loops.

*.tstackm.* are parameters for the mismatches in multibranch loops.
```
and, as commented in the [C-source to GTFold here](https://github.gatech.edu/gtDMMB/GTFoldPython/blob/master/Python/Docs/SourceCodeHackingAndParameters.md#from-commented_constantstxt) reproduced below:
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
The ``GTFoldPython`` library now supports several standard variants of the 
[NNDB energy models](http://rna.urmc.rochester.edu/NNDB/tutorials.html) 
included with the stock [GTFold distribution]() data files 
[linked here]().

## Another standard method: Specifying the energy model via text-based parameter lists

There appears to be another standard method of specifying these values via a text-file-based list of parameters 
which are described, for example explicitly, [here (turner_parameters_fm363_constrdangles.txt)](https://www.cs.ubc.ca/~andrones/contributions/CG_v2.0/Simfold-template/data/turner_parameters_fm363_constrdangles.txt) and in symbolic form below:
```cpp
stack[0][3][0][3]
stack[0][3][1][2]
stack[0][3][2][1]
stack[0][3][2][3]
stack[0][3][3][0]
stack[0][3][3][2]
stack[1][2][0][3]
stack[1][2][1][2]
stack[1][2][2][1]
stack[1][2][2][3]
stack[1][2][3][2]
stack[2][1][0][3]
stack[2][1][1][2]
stack[2][1][2][3]
stack[2][1][3][2]
stack[2][3][0][3]
stack[2][3][2][3]
stack[2][3][3][2]
stack[3][0][0][3]
stack[3][0][2][3]
stack[3][2][2][3]
tstackh[0][3][0][0]
tstackh[0][3][0][1]
tstackh[0][3][0][2]
tstackh[0][3][0][3]
tstackh[0][3][1][0]
tstackh[0][3][1][1]
tstackh[0][3][1][2]
tstackh[0][3][1][3]
tstackh[0][3][2][0]
tstackh[0][3][2][1]
tstackh[0][3][2][2]
tstackh[0][3][2][3]
tstackh[0][3][3][0]
tstackh[0][3][3][1]
tstackh[0][3][3][2]
tstackh[0][3][3][3]
tstackh[1][2][0][0]
tstackh[1][2][0][1]
tstackh[1][2][0][2]
tstackh[1][2][0][3]
tstackh[1][2][1][0]
tstackh[1][2][1][1]
tstackh[1][2][1][2]
tstackh[1][2][1][3]
tstackh[1][2][2][0]
tstackh[1][2][2][1]
tstackh[1][2][2][2]
tstackh[1][2][2][3]
tstackh[1][2][3][0]
tstackh[1][2][3][1]
tstackh[1][2][3][2]
tstackh[1][2][3][3]
tstackh[2][1][0][0]
tstackh[2][1][0][1]
tstackh[2][1][0][2]
tstackh[2][1][0][3]
tstackh[2][1][1][0]
tstackh[2][1][1][1]
tstackh[2][1][1][2]
tstackh[2][1][1][3]
tstackh[2][1][2][0]
tstackh[2][1][2][1]
tstackh[2][1][2][2]
tstackh[2][1][2][3]
tstackh[2][1][3][0]
tstackh[2][1][3][1]
tstackh[2][1][3][2]
tstackh[2][1][3][3]
tstackh[2][3][0][0]
tstackh[2][3][0][1]
tstackh[2][3][0][2]
tstackh[2][3][0][3]
tstackh[2][3][1][0]
tstackh[2][3][1][1]
tstackh[2][3][1][2]
tstackh[2][3][1][3]
tstackh[2][3][2][0]
tstackh[2][3][2][1]
tstackh[2][3][2][2]
tstackh[2][3][2][3]
tstackh[2][3][3][0]
tstackh[2][3][3][1]
tstackh[2][3][3][2]
tstackh[2][3][3][3]
tstackh[3][0][0][0]
tstackh[3][0][0][1]
tstackh[3][0][0][2]
tstackh[3][0][0][3]
tstackh[3][0][1][0]
tstackh[3][0][1][1]
tstackh[3][0][1][2]
tstackh[3][0][1][3]
tstackh[3][0][2][0]
tstackh[3][0][2][1]
tstackh[3][0][2][2]
tstackh[3][0][2][3]
tstackh[3][0][3][0]
tstackh[3][0][3][1]
tstackh[3][0][3][2]
tstackh[3][0][3][3]
tstackh[3][2][0][0]
tstackh[3][2][0][1]
tstackh[3][2][0][2]
tstackh[3][2][0][3]
tstackh[3][2][1][0]
tstackh[3][2][1][1]
tstackh[3][2][1][2]
tstackh[3][2][1][3]
tstackh[3][2][2][0]
tstackh[3][2][2][1]
tstackh[3][2][2][2]
tstackh[3][2][2][3]
tstackh[3][2][3][0]
tstackh[3][2][3][1]
tstackh[3][2][3][2]
tstackh[3][2][3][3]
misc.internal_AU_closure
misc.internal_AG_mismatch
misc.internal_UU_mismatch
int11[0][3][3][3][0][3]
int11[0][3][3][3][1][2]
int11[0][3][3][3][2][1]
int11[0][3][3][3][3][0]
int11[1][2][0][0][1][2]
int11[1][2][0][0][2][1]
int11[1][2][0][1][1][2]
int11[1][2][0][1][2][1]
int11[1][2][0][2][1][2]
int11[1][2][0][2][2][1]
int11[1][2][1][0][1][2]
int11[1][2][1][1][1][2]
int11[1][2][1][1][2][1]
int11[1][2][1][3][1][2]
int11[1][2][1][3][2][1]
int11[1][2][2][0][1][2]
int11[1][2][2][2][1][2]
int11[1][2][2][2][2][1]
int11[1][2][3][1][1][2]
int11[1][2][3][3][0][3]
int11[1][2][3][3][1][2]
int11[1][2][3][3][2][1]
int11[2][1][0][0][1][2]
int11[2][1][0][1][1][2]
int11[2][1][0][2][1][2]
int11[2][1][1][1][1][2]
int11[2][1][1][3][1][2]
int11[2][1][2][2][1][2]
int11[2][1][3][3][0][3]
int11[2][1][3][3][1][2]
int11[3][0][3][3][0][3]
misc.internal11_basic_mismatch
misc.internal11_GG_mismatch
int21[1][2][0][0][1][2][0]
int21[1][2][0][0][1][2][1]
int21[1][2][0][0][1][2][2]
int21[1][2][0][1][1][2][0]
int21[1][2][0][1][1][2][1]
int21[1][2][0][1][1][2][2]
int21[1][2][0][2][1][2][0]
int21[1][2][0][2][1][2][1]
int21[1][2][0][2][1][2][2]
int21[1][2][1][0][1][2][0]
int21[1][2][1][0][1][2][1]
int21[1][2][1][0][1][2][3]
int21[1][2][1][1][1][2][0]
int21[1][2][1][1][1][2][1]
int21[1][2][1][1][1][2][3]
int21[1][2][1][3][1][2][0]
int21[1][2][1][3][1][2][1]
int21[1][2][1][3][1][2][3]
int21[1][2][2][0][1][2][0]
int21[1][2][2][0][1][2][2]
int21[1][2][2][2][1][2][0]
int21[1][2][2][2][1][2][2]
int21[1][2][3][1][1][2][1]
int21[1][2][3][1][1][2][3]
int21[1][2][3][3][1][2][1]
int21[1][2][3][3][1][2][3]
int21[2][1][0][0][2][1][0]
int21[2][1][0][0][2][1][1]
int21[2][1][0][0][2][1][2]
int21[2][1][0][1][2][1][0]
int21[2][1][0][1][2][1][1]
int21[2][1][0][1][2][1][2]
int21[2][1][0][2][2][1][0]
int21[2][1][0][2][2][1][1]
int21[2][1][0][2][2][1][2]
int21[2][1][1][0][2][1][0]
int21[2][1][1][0][2][1][1]
int21[2][1][1][0][2][1][3]
int21[2][1][1][1][2][1][0]
int21[2][1][1][1][2][1][1]
int21[2][1][1][1][2][1][3]
int21[2][1][1][3][2][1][0]
int21[2][1][1][3][2][1][1]
int21[2][1][1][3][2][1][3]
int21[2][1][2][0][2][1][0]
int21[2][1][2][0][2][1][2]
int21[2][1][2][2][2][1][0]
int21[2][1][2][2][2][1][2]
int21[2][1][3][1][2][1][1]
int21[2][1][3][1][2][1][3]
int21[2][1][3][3][2][1][1]
int21[2][1][3][3][2][1][3]
misc.internal21_match
misc.internal21_AU_closure
int22[0][3][0][0][3][0][0][0]
int22[0][3][0][1][3][0][1][0]
int22[0][3][0][2][3][0][2][0]
int22[0][3][1][0][3][0][0][1]
int22[0][3][1][1][3][0][1][1]
int22[0][3][1][3][3][0][3][1]
int22[0][3][2][0][3][0][0][2]
int22[0][3][2][2][3][0][2][2]
int22[0][3][2][3][3][0][3][2]
int22[0][3][3][1][3][0][1][3]
int22[0][3][3][2][3][0][2][3]
int22[0][3][3][3][3][0][3][3]
int22[1][2][0][0][2][1][0][0]
int22[1][2][0][1][2][1][1][0]
int22[1][2][0][2][2][1][2][0]
int22[1][2][1][0][2][1][0][1]
int22[1][2][1][1][2][1][1][1]
int22[1][2][1][3][2][1][3][1]
int22[1][2][2][0][2][1][0][2]
int22[1][2][2][2][2][1][2][2]
int22[1][2][2][3][2][1][3][2]
int22[1][2][3][1][2][1][1][3]
int22[1][2][3][2][2][1][2][3]
int22[1][2][3][3][2][1][3][3]
int22[2][1][0][0][1][2][0][0]
int22[2][1][0][1][1][2][1][0]
int22[2][1][0][2][1][2][2][0]
int22[2][1][1][0][1][2][0][1]
int22[2][1][1][1][1][2][1][1]
int22[2][1][1][3][1][2][3][1]
int22[2][1][2][0][1][2][0][2]
int22[2][1][2][2][1][2][2][2]
int22[2][1][2][3][1][2][3][2]
int22[2][1][3][1][1][2][1][3]
int22[2][1][3][2][1][2][2][3]
int22[2][1][3][3][1][2][3][3]
int22[3][0][0][0][0][3][0][0]
int22[3][0][0][1][0][3][1][0]
int22[3][0][0][2][0][3][2][0]
int22[3][0][1][0][0][3][0][1]
int22[3][0][1][1][0][3][1][1]
int22[3][0][1][3][0][3][3][1]
int22[3][0][2][0][0][3][0][2]
int22[3][0][2][2][0][3][2][2]
int22[3][0][2][3][0][3][3][2]
int22[3][0][3][1][0][3][1][3]
int22[3][0][3][2][0][3][2][3]
int22[3][0][3][3][0][3][3][3]
misc.internal22_delta_same_size
misc.internal22_delta_different_size
misc.internal22_delta_1stable_1unstable
misc.internal22_delta_AC
misc.internal22_match
dangle_top[0][3][0]
dangle_top[0][3][1]
dangle_top[0][3][2]
dangle_top[0][3][3]
dangle_top[1][2][0]
dangle_top[1][2][1]
dangle_top[1][2][2]
dangle_top[1][2][3]
dangle_top[2][1][0]
dangle_top[2][1][1]
dangle_top[2][1][2]
dangle_top[2][1][3]
dangle_top[2][3][0]
dangle_top[2][3][1]
dangle_top[2][3][2]
dangle_top[2][3][3]
dangle_top[3][0][0]
dangle_top[3][0][1]
dangle_top[3][0][2]
dangle_top[3][0][3]
dangle_top[3][2][0]
dangle_top[3][2][1]
dangle_top[3][2][2]
dangle_top[3][2][3]
dangle_bot[0][3][0]
dangle_bot[0][3][1]
dangle_bot[0][3][2]
dangle_bot[0][3][3]
dangle_bot[1][2][0]
dangle_bot[1][2][1]
dangle_bot[1][2][2]
dangle_bot[1][2][3]
dangle_bot[2][1][0]
dangle_bot[2][1][1]
dangle_bot[2][1][2]
dangle_bot[2][1][3]
dangle_bot[2][3][0]
dangle_bot[2][3][1]
dangle_bot[2][3][2]
dangle_bot[2][3][3]
dangle_bot[3][0][0]
dangle_bot[3][0][1]
dangle_bot[3][0][2]
dangle_bot[3][0][3]
dangle_bot[3][2][0]
dangle_bot[3][2][1]
dangle_bot[3][2][2]
dangle_bot[3][2][3]
internal_penalty_by_size[4]
internal_penalty_by_size[5]
internal_penalty_by_size[6]
bulge_penalty_by_size[1]
bulge_penalty_by_size[2]
bulge_penalty_by_size[3]
bulge_penalty_by_size[4]
bulge_penalty_by_size[5]
bulge_penalty_by_size[6]
hairpin_penalty_by_size[3]
hairpin_penalty_by_size[4]
hairpin_penalty_by_size[5]
hairpin_penalty_by_size[6]
hairpin_penalty_by_size[7]
hairpin_penalty_by_size[8]
hairpin_penalty_by_size[9]
misc.terminal_AU_penalty
misc.hairpin_GGG
misc.hairpin_c1
misc.hairpin_c2
misc.hairpin_c3
misc.multi_offset
misc.multi_helix_penalty
misc.multi_free_base_penalty
misc.intermolecular_initiation
tloop[0].energy
tloop[1].energy
tloop[2].energy
tloop[3].energy
tloop[4].energy
tloop[5].energy
tloop[6].energy
tloop[7].energy
tloop[8].energy
tloop[9].energy
tloop[10].energy
tloop[11].energy
tloop[12].energy
tloop[13].energy
tloop[14].energy
tloop[15].energy
tloop[16].energy
tloop[17].energy
tloop[18].energy
tloop[19].energy
tloop[20].energy
tloop[21].energy
tloop[22].energy
tloop[23].energy
tloop[24].energy
tloop[25].energy
tloop[26].energy
tloop[27].energy
tloop[28].energy
tloop[29].energy
```
This method of specifying the energy model appears to be described and justified in the modified NNDB-like model methodology in the 
paper *Improved free energy parameters for RNA pseudoknotted secondary structure prediction* by M. Andronescu, C. Pop and A. E. Condon 
from 2016 (see [link to full text here](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2802035/)). 

### Software for parsing the parameter list energy model formats

A guide to using these 
parameter lists is documented on [this site](https://www.cs.ubc.ca/~andrones/contributions/CG_v2.0/CG_prediction.html). 
Another solid bet for re-usable code to populate the GTFold-like energy model structures can be taken from the 
[Simfold software project](https://github.com/HosnaJabbari/CCJ/tree/master/simfold), though that application is not the primary 
usage for ``simfold``.

### Notes on some other semi-standardized modified energy model data sets specified by parameter lists

Several apparently at least semi-standard variants of the Turner-Matthews NNDB energy model parameter files have been specified 
using this parameter list format, including, but not limited to, the following named data set specifications:
* **(MT99)**: The well-known *Turner99* data set ([link](http://www.cs.ubc.ca/labs/beta/Publications/PaperMaterials/PseudoRNA/results/parameters_MT99.txt))
* **(MT09)**: Another variant of the Matthews-Turner data set ([link](http://www.cs.ubc.ca/labs/beta/Publications/PaperMaterials/PseudoRNA/results/parameters_MT09.txt))
* **(DP03)**: The *Dirks and Pierce '03 model* data set ([link](http://www.cs.ubc.ca/labs/beta/Publications/PaperMaterials/PseudoRNA/results/parameters_DP03.txt))
* **(DP09)**: The *Dirks and Pierce '09 model* data set ([link](http://www.cs.ubc.ca/labs/beta/Publications/PaperMaterials/PseudoRNA/results/parameters_DP09.txt))
* **(CC06)**: The *Cao and Chen '06 model'* data set ([link](http://www.cs.ubc.ca/labs/beta/Publications/PaperMaterials/PseudoRNA/results/parameters_CC06.txt))
* **(CC09)**: The *Cao and Chen '09 model'* data set ([link](http://www.cs.ubc.ca/labs/beta/Publications/PaperMaterials/PseudoRNA/results/parameters_CC09.txt))


