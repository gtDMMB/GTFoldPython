# RNAstructure Installation and Overview: Thermodynamic Parameter Tables

## What are thermodynamic parameters?

RNAstructure uses a set of nearest neighbor parameters to estimate the folding stability of structures. For RNA, these are called Turner rules.

A tutorial for understanding and using these parameters is available at the [NNDB](https://rna.urmc.rochester.edu/NNDB/). 
The latest set of rules (and those used by RNAstructure) are the Turner 2004 rules.

## Where are the thermodynamic parameters located?

The tables are located in the GTFoldPython subdirectory ``Python/Testing/ExtraGTFoldThermoData``.
See also the [gtDMMB project GTModify](https://github.com/gtDMMB/GTModify) for information on how to modify and prepare these sets of 
thermodynamic parameter data for use with GTFold. 

## What does each table contain? 

The tables are formatted starting with the nucleotide/alphabet type. rna predes the RNA tables. dna precedes the DNA tables. b-test precedes a set of test tables for RNA that include a 'B' nucleotide that is the same as 'A'. These are used to test the code to ensure the alphabet works beyond A, C, G, and U/T.

The suffix indicates the type of parameter. dg are free energy change at 37 degrees C parameters and dh are enthalpy change parameters. dat is used for tables that specify the alphabet information.

&ast;*.specification.dat indicates the alphabet and pairs.

&ast;*.coaxial.&ast;* are parameters for flush coaxial stacking where two helix ends stack without an intervening mismatch.

&ast;*.coaxstack.&ast;* are parameters for coaxial stacking of helices with an intervening mismatch. This is for the stack where the backbone is not continuous.

&ast;*.dangle.&ast;* are parameters for dangling ends on pairs.

&ast;*.hexaloop.&ast;* are parameters for hairpin loops of 6 unpaired nucleotides that have stabilities not well modeled by the parameters.

&ast;*.int11.&ast;* are parameters for 1×1 internal loops.

&ast;*.int21.&ast;* are parameters for 2×1 internal loops.

&ast;*.int22.&ast;* are parameters for 2×2 internal loops.

&ast;*.loop.&ast;* are parameters for loop initiations.

&ast;*.misloop.&ast;* are parameters that do not fit into other tables.

&ast;*.stack.&ast;* are parameters for helical stacking.

&ast;*.tloop.&ast;* are parameters for hairpin loops of 4 unpaired nucleotides that have stabilities not well modeled by the parameters.

&ast;*.triloop.&ast;* are parameters for hairpin loops of 3 unpaired nucleotides that have stabilities not well modeled by the parameters.

&ast;*.tstack.&ast;* are parameters for terminal mismatches in exterior loops.

&ast;*.tstackcoax.&ast;* are parameters for coaxial stacking of helices with an intervening mismatch. This is for the stack where the backbone is continuous.

&ast;*.tstackh.&ast;* are parameters for first mismtaches in hairpin loops.

&ast;*.tstacki.&ast;* are parameters for the mismatches in internal loops.

&ast;*.tstacki23.&ast;* are parameters for the mismatches in 2×3 internal loops.

&ast;*.tstackm.&ast;* are parameters for the mismatches in multibranch loops.

Note that for many terminal stack tables, the AU/GU helix end penalty is included for computational speed.
