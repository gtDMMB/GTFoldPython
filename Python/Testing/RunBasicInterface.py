#### TestBasicInterface.py 

import sys, os
from GTFoldPythonImportAll import *

## Initialize the library:
print("*** Initializing the library")
GTFP.Init()
GTFP.Config(quiet = False, debugging = False, verbose = False, stdmsgout = "stderr")

## Display detailed help, and help on a specific topic:
print("*** Displaying help topics for GTFoldPython")
GTFP.DisplayDetailedHelp()
GTFP.DisplayHelp("?")
GTFP.DisplayHelp("settings")

## Configure the library: 
print("*** Configuring the library")
configSettings = {
    'outputprefix'    : "testrun_", 
    'writeauxfiles'   : 1, 
    'numthreads'      : 2, 
    'calcpartition'   : 0, 
    'printarrays'     : 0, 
    'separatectfiles' : 1, 
    'ctfilesdir'      : "ctfiles",            # need not already exist
    'summaryfile'     : "summary.out", 
    'workdir'         : os.path.expanduser("~/TestGTFoldPython"), # need not already exist
}
GTFP.ConfigExtraSettings(configSettings)
GTFP.SetDangleParameter(0)
GTFP.SetTerminalMismatch(True)
GTFP.SetLimitContactDistance(-1) # same as if not set
GTFP.SetPrefilterParameter(-1)   # same as if not set

## Configure the energy model and thermodynamic parameters
## NOTE: Paths relative to the current running script location
#GTFP.SetGTFoldDataDirectory("../Testing/ExtraGTFoldThermoData/GTFoldTurner04/") 
#GTFP.SetThermodynamicParameters(TURNER04, None)
GTFP.SetThermodynamicParametersFromDefaults(TURNER04)

## Print the runtime configuration that we ust changed:
print("*** Printing out the active runtime configuration")
GTFP.PrintRunConfiguration()

## d.16.a.H.volcanii.bpseq:
baseSeqLong = "AUUCCGGUUGAUCCUGCCGGAGGUCAUUGCUAUUGGGGUCCGAUUUAGCCAUGCUAGUUGCACGAGUUCAUACUCGUGGCGAAAAGCUCAGUAACACGUGGCCAAACUACCCUACAGAGAACGAUAACCUCGGGAAACUGAGGCUAAUAGUUCAUACGGGAGUCAUGCUGGAAUGCCGACUCCCCGAAACGCUCAGGCGCUGUAGGAUGUGGCUGCGGCCGAUUAGGUAGACGGUGGGGUAACGGCCCACCGUGCCGAUAAUCGGUACGGGUUGUGAGAGCAAGAGCCCGGAGACGGAAUCUGAGACAAGAUUCCGGGCCCUACGGGGCGCAGCAGGCGCGAAACCUUUACACUGCACGCAAGUGCGAUAAGGGGACCCCAAGUGCGAGGGCAUAUAGUCCUCGCUUUUCUCGACCGUAAGGCGGUCGAGGAAUAAGAGCUGGGCAAGACCGGUGCCAGCCGCCGCGGUAAUACCGGCAGCUCAAGUGAUGACCGAUAUUAUUGGGCCUAAAGCGUCCGUAGCCGGCCACGAAGGUUCAUCGGGAAAUCCGCCAGCUCAACUGGCGGGCGUCCGGUGAAAACCACGUGGCUUGGGACCGGAAGGCUCGAGGGGUACGUCCGGGGUAGGAGUGAAAUCCCGUAAUCCUGGACGGACCACCGAUGGCGAAAGCACCUCGAGAAGACGGAUCCGACGGUGAGGGACGAAAGCUAGGGUCUCGAACCGGAUUAGAUACCCGGGUAGUCCUAGCUGUAAACGAUGCUCGCUAGGUGUGACACAGGCUACGAGCCUGUGUUGUGCCGUAGGGAAGCCGAGAAGCGAGCCGCCUGGGAAGUACGUCCGCAAGGAUGAAACUUAAAGGAAUUGGCGGGGGAGCACUACAACCGGAGGAGCCUGCGGUUUAAUUGGACUCAACGCCGGACAUCUCACCAGCUCCGACUACAGUGAUGACGAUCAGGUUGAUGACCUUAUCACGACGCUGUAGAGAGGAGGUGCAUGGCCGCCGUCAGCUCGUACCGUGAGGCGUCCUGUUAAGUCAGGCAACGAGCGAGACCCGCACUUCUAAUUGCCAGCAGCAGUUUCGACUGGCUGGGUACAUUAGAAGGACUGCCGCUGCUAAAGCGGAGGAAGGAACGGGCAACGGUAGGUCAGUAUGCCCCGAAUGAGCUGGGCUACACGCGGGCUACAAUGGUCGAGACAAUGGGUUGCUAUCUCGAAAGAGAACGCUAAUCUCCUAAACUCGAUCGUAGUUCGGAUUGAGGGCUGAAACUCGCCCUCAUGAAGCUGGAUUCGGUAGUAAUCGCAUUUCAAUAGAGUGCGGUGAAUACGUCCCUGCUCCUUGCACACACCGCCCGUCAAAGCACCCGAGUGAGGUCCGGAUGAGGCCACCACACGGUGGUCGAAUCUGGGCUUCGCAAGGGGGCUUAAGUCGUAACAAGGUAGCCGUAGGGGAAUCUGCGGCUGGAUCACCUCCUG"

## yeast.fa: 
baseSeqShort = "GCCGUGAUAGUUUAAUGGUCAGAAUGGGCGCUUGUCGCGUGCCAGAUCGGGGUUCAAUUCCCCGUCGCGGCGCCA"
baseSeqVeryShort = "GCCGUGAUAGUUUAA"
baseSeqFPCons = "GCAUUGGAGAUGGCAUUCCUCCAUUAACAAACCGCUGCGCCCGUAGCAGCUGAUGAUGCCUACAGA"

## Constraints: 
consListDefault = []
# Load F/P constraints from file: ....<<<<<..((((((.>>>>>..........(((((.......)))))....))))))......
consListFP = GTFPUtils.ReadFPConstraintsFromFile("../Testing/SampleFiles/demo2.cons") 
consListFP2 = GTFPUtils.GetFPConstraintsFromString("....<<<<<..((((((.>>>>>..........(((((.......)))))....))))))......")
consListSHAPE = GTFPUtils.ReadSHAPEConstraintsFromFile("../Testing/SampleFiles/demo1.shape")

## Find the MFE and MFE structure:
print("*** Finding MFE for d.16.a.H.volcanii:")
(mfe, mfeDOTStruct) = GTFP.GetMFEStructure(baseSeqLong, consListDefault)
print("MFE %1.3f => MFE DOT STRUCT \"%s\"\n\n" % (mfe, mfeDOTStruct))
#(mfe, mfeDOTStruct) = GTFP.GetMFEStructureSHAPE(baseSeqLong, consListSHAPE)

## Get the partition function counts:
print("*** Computing the PF counts")
dblStr = GTFP.GetPFuncCount(baseSeqShort)
print("GetPFunctCount: {0}".format(dblStr))
dblStr = GTFP.GetPFuncCountSHAPE(baseSeqVeryShort, consListSHAPE)
print("GetPFuncCountSHAPE: {0}\n".format(dblStr))

## Compute BPP:
print("*** Finding BPP lists")
bppProbsList = GTFP.ComputeBPP(baseSeqShort, consListDefault)
#bppProbsList = GTFP.ComputeBPPSHAPE(baseSeqShort, consListSHAPE)
for (idx, (i, j, p)) in enumerate(bppProbsList):
    print("[#{3}] Base Pair {0} <-> {1} @ probability {2}".format(i, j, p, idx + 1))

## Sample some structures from the Boltzmann distribution
print("*** Sampling structures from the Boltzmann distribution")
N = 3
structsList = GTFP.SampleBoltzmannStructures(baseSeqShort, N, consListDefault)
#structsList = GTFP.SampleBoltzmannStructuresSHAPE(baseSeqShort, N, consListSHAPE)
# TODO: print 
for (idx, (ep, ap, e, struct)) in enumerate(structsList):
    print("[#% 2d] Structure with estimated/actual probability %g/%g and energy %g" % (idx + 1, ep, ap, e))
    print("        {0}".format(struct))
print("")

## Find suboptimal structures
print("*** Finding suboptimal structures for a short sequence and small delta (TAKES A WHILE...)")
delta = 1.0
suboptStructs = GTFP.GetSuboptStructures(baseSeqFPCons, delta)
print("NUM SUBOPT STRUCTS FOUND = %d WITHIN %g OF OPT" % (len(suboptStructs), delta))
for (dotStruct, e) in suboptStructs:
    print("   >> STRUCT [energy = % 3d]: %s" % (e, dotStruct));

## Thats it!
print("\n")

