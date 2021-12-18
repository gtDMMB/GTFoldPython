### GTFoldPythonUnitTests.py : Run unit tests to verify basic functionality of GTFoldPython;
#### Author: Maxie D. Schmidt (maxieds@gmail.com)
#### Created: 2020.01.27

from GTFoldPython import GTFoldPython
from GTFoldPythonImportAll import *

import unittest
import sys
import logging
import inspect
import re
import os
import os.path
import inspect
from enum import Flag

class GTFPTestSuiteTypes(Flag):
    
    NO_TESTS                = 0
    MFE_BASE_TESTS          = 1
    MFE_ROGERS_RNADB_TESTS  = 2
    MFE_CUSTOM_PARAMS_TESTS = 4
    PFUNC_TESTS             = 8
    SUBOPT_TESTS            = 16
    NOT_PASSING             = 32
    ALL_TESTS               = 0xffff

    @staticmethod
    def GetVariableName(gtfpEnumVarName):
        localVarsList = inspect.currentframe().f_back.f_locals.items()
        varNamesList = [ vname for vname, vval in localVarsList if vval is gtfpEnumVarName ]
        varNamesList = list(map(lambda vname: str(vname).split('.')[0], varNamesList))
        if len(varNamesList) == 0:
            return "UNKNOWN-TEST-SUITE"
        return varNamesList[0]
    ##

    def __int__(self):
        return int(self.value)
    ##

##

TEST_SUITE_RUNTYPE = int(os.getenv('GTFP_TEST_SUITE', str(0xffff)), 16)
GTFP_UNIT_TEST_DEBUGGING = bool(int(os.getenv('GTFP_TEST_DEBUGGING', "0")))

class GTFoldPythonUnitTests(unittest.TestCase):

    NO_TESTS         = GTFPTestSuiteTypes.NO_TESTS
    MFE_BASE_TESTS   = GTFPTestSuiteTypes.MFE_BASE_TESTS
    MFE_RNADB_TESTS  = GTFPTestSuiteTypes.MFE_ROGERS_RNADB_TESTS
    MFE_CUSTOM_TESTS = GTFPTestSuiteTypes.MFE_CUSTOM_PARAMS_TESTS
    PFUNC_TESTS      = GTFPTestSuiteTypes.PFUNC_TESTS
    SUBOPT_TESTS     = GTFPTestSuiteTypes.SUBOPT_TESTS
    NOT_PASSING      = ~int(GTFPTestSuiteTypes.NOT_PASSING) & 0x0000ffff
    
    UnitTestDecorArgs = lambda testType, invertBoolean=False: (
        TEST_SUITE_RUNTYPE & int(testType) == 0 if not invertBoolean else TEST_SUITE_RUNTYPE & int(testType) != 0, 
        "! %s" % GTFPTestSuiteTypes.GetVariableName(testType) 
    )

    TESTDATADIR_RELATIVE_PATH = "./Testing/TestData/"
    TESTDATADIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 
                               os.path.abspath(TESTDATADIR_RELATIVE_PATH))

    @staticmethod
    def LoadInputSequenceFromFile(seqFilePath):
        (orgName, baseSeq) = ("", "")
        with open(seqFilePath, "r") as fp:
            for seqline in fp:
                seqline = seqline.replace('\n', '')
                if seqline[0] == '>':
                    orgName = seqline.replace('>', '')
                    continue
                baseSeq = seqline
                fp.close()
                return (orgName, baseSeq)
        return (orgName, baseSeq)
    ##

    @staticmethod
    def LoadOutputStructFromFile(outputStructFilePath):
        (orgName, mfeDOTStruct) = GTFoldPythonUnitTests.LoadInputSequenceFromFile(outputStructFilePath)
        return mfeDOTStruct
    ##
    
    @staticmethod
    def LoadOutputMFEFromFile(outputMFEFilePath):
        with open(outputMFEFilePath, "r") as fp:
            mfeStr = fp.readline()
        return float(mfeStr)
    ##

    @staticmethod
    def LoadConstraintsFromFile(consFilePath):
        consFileExt = os.path.splitext(os.path.basename(consFilePath))[1].lower()
        if consFileExt == ".shape":
            return GTFPUtils.ReadSHAPEConstraintsFromFile(consFilePath)
        else:
            return GTFPUtils.ReadFPConstraintsFromFile(consFilePath)
    ##

    def AssertLastMFETupleEquals(self, mfe, mfeDOTStruct):
        assertRetValue = True
        if mfe != self._lastMFE or mfeDOTStruct != self._lastMFEStruct:
            print(" ... TEST FAILED! [XX]")
            print("ACTUAL:     ", self._lastMFE, self._lastMFEStruct)
            print("EXPECTED:   ", mfe, mfeDOTStruct)
            if GTFP_UNIT_TEST_DEBUGGING:
                print("PRINTING RUNTIME CONFIG -- AFTER FAIL:\n")
                GTFoldPython.PrintRunConfiguration(True)
                sys.exit(-101)
            assertRetValue = False
        else:
            print(" ... TEST PASSED! [OK]")
        self.assertEqual(mfe, self._lastMFE)
        self.assertEqual(mfeDOTStruct, self._lastMFEStruct)
        return assertRetValue
    ##
 
    _testNumber = 0

    def DescribeUnitTest(self, testDesc):
        GTFoldPythonUnitTests._testNumber += 1
        self._testPurpose = testDesc;
    ##

    def DefineConstraints(self, consList):
        self._testConstraints = consList
    ##

    def NameOrganism(self, orgName, accNo = ""):
        self._orgName = orgName
        self._orgAccNo = accNo
    ##

    def OrganismBaseSequence(self, baseSeq):
        self._orgBaseSeq = baseSeq
    ##

    def ComputeMFEData(self):
        (mfe, mfeStruct) = GTFoldPython.GetMFEStructure(self._orgBaseSeq, self._testConstraints)
        self._lastMFE = mfe
        self._lastMFEStruct = mfeStruct
    ##
    
    def PrintTestInfo(self, stackOffset=3):
        testMethod = inspect.stack()[stackOffset].function
        orgPrintName = self._orgName
        if self._orgAccNo != "":
            orgPrintName += " (" + self._orgAccNo + ")"
        basePrintSeq = self._orgBaseSeq if len(self._orgBaseSeq) <= 16 else \
                self._orgBaseSeq[0:8] + " ... " + self._orgBaseSeq[-15:]
        numConstF = [ cons[0] for cons in self._testConstraints].count(GTFoldPython.F)
        numConstP = [ cons[0] for cons in self._testConstraints].count(GTFoldPython.P)
        constPrintStatus = "None enabled" if len(self._testConstraints) == 0 else \
                "%d Total, %d Forced, %d Prohibited" % (numConstF + numConstP, numConstF, numConstP)
        print("========== GTFOLD-PYTHON UNIT TEST INFO: (" + str(testMethod) + ")")
        print("    UNIT-TEST ## %d" % GTFoldPythonUnitTests._testNumber)
        if self._testPurpose != None and self._testPurpose != '': 
            print("    >> Test Purpose:    %s" % self._testPurpose)
        if orgPrintName != None and orgPrintName != '':
            print("    >> Organism:        %s" % orgPrintName)
        if basePrintSeq != None and basePrintSeq != '':
            print("    >> Base Sequence:   %s [% 4d bases ]" % (basePrintSeq, len(self._orgBaseSeq)))
        if constPrintStatus != None and constPrintStatus != '':
            print("    >> Constraints:     %s" % constPrintStatus)
        print("////", end='', flush=True)
    ##

    def setUp(self):
        GTFoldPython._ConstructLibGTFold()
        GTFoldPython.Config(debugging=0, quiet=1, verbose=0)
        if GTFP_UNIT_TEST_DEBUGGING:
            print("PRINTING RUNTIME CONFIG -- AT TEST SETUP:\n")
            GTFoldPython.PrintRunConfiguration(True)
        self._testPurpose = ""
        self._testConstraints = []
        self._orgName = ""
        self._orgAccNo = ""
        self._orgBaseSeq = ""
        self._testResultExpectedMFE = None
        self._testResultExpectedMFEStruct = None
    ##

    def setUpMFEBaseTest(self, tpParamsCode="Turner99"):
        GTFoldPython.EnableTerminalMismatch()
        extraConfigDict = {
            'rnafold' : 0,
            'unafold' : 0
        }    
        #GTFoldPython.SetDangleParameter(0)
        #GTFoldPython.SetLimitContactDistance(-1)
        #GTFoldPython.SetPrefilterParameter(2)
        GTFoldPython.ConfigExtraSettings(extraConfigDict)
        GTFoldPython.SetThermodynamicParametersFromDefaults(tpParamsCode)
    ##

    def setUpMFERogersTypeTest(self):
        GTFoldPython.DisableTerminalMismatch()
        GTFoldPython.SetLimitContactDistance(-1)
        extraConfigDict = {
            'rnafold' : 0,
            'unafold' : 0
        }    
        GTFoldPython.ConfigExtraSettings(extraConfigDict)
        GTFoldPython.SetThermodynamicParametersFromDefaults("Turner99")
    ##

    def setUpMFECustomParametersTypeTest(self, extraConfig={}, tpCode="Turner99", tpParamsDir="Turner99"):
        GTFoldPython.Init(True)
        GTFoldPython.DisableTerminalMismatch()
        GTFoldPython.SetLimitContactDistance(-1)
        GTFoldPython.SetPrefilterParameter(2)
        GTFoldPython.ConfigExtraSettings(extraConfig)
        defaultDataDir = GTFPConfig.GetThermodynamicParametersDirectory(tpParamsDir)
        GTFoldPython.SetThermodynamicParameters(tpCode, defaultDataDir)
    ##

    def tearDown(self):
        pass
    ##

    def TestTypeV1_NoConstraints(self, inputSeq, outputStruct, outputMFE):
        self.setUpMFEBaseTest()
        self.DescribeUnitTest("Basic MFE calculation without constraints")
        (orgName, baseSeq) = GTFoldPythonUnitTests.LoadInputSequenceFromFile(inputSeq)
        self.NameOrganism(orgName)
        self.OrganismBaseSequence(baseSeq)
        self.DefineConstraints([])
        self.ComputeMFEData()
        (mfe, mfeStruct) = (GTFoldPythonUnitTests.LoadOutputMFEFromFile(outputMFE), 
                            GTFoldPythonUnitTests.LoadOutputStructFromFile(outputStruct))
        self.PrintTestInfo()
        self.AssertLastMFETupleEquals(mfe, mfeStruct)
    ##

    def RunTestTypeV1_NoConstraints(self, inputSeqBaseName):
        inputSeqBaseName = GTFoldPythonUnitTests.TESTDATADIR + "/" + inputSeqBaseName
        self.TestTypeV1_NoConstraints(inputSeqBaseName + ".fasta", 
                                      inputSeqBaseName + ".mfestruct.dot", 
                                      inputSeqBaseName + ".mfe");
    ##

    def TestTypeV2_WithConstraints(self, inputSeq, consFile, outputStruct, outputMFE):
        self.setUpMFEBaseTest()
        self.DescribeUnitTest("Basic MFE calculation *with* constraints")
        (orgName, baseSeq) = GTFoldPythonUnitTests.LoadInputSequenceFromFile(inputSeq)
        self.NameOrganism(orgName)
        self.OrganismBaseSequence(baseSeq)
        self.DefineConstraints(GTFoldPythonUnitTests.LoadConstraintsFromFile(consFile))
        self.PrintTestInfo()
        self.ComputeMFEData()
        (mfe, mfeStruct) = (GTFoldPythonUnitTests.LoadOutputMFEFromFile(outputMFE), 
                            GTFoldPythonUnitTests.LoadOutputStructFromFile(outputStruct))
        self.AssertLastMFETupleEquals(mfe, mfeStruct)
    ##

    def RunTestTypeV2_WithConstraints(self, inputSeqBaseName):
        inputSeqBaseName = GTFoldPythonUnitTests.TESTDATADIR + "/" + inputSeqBaseName
        argFileExts = [ "fasta", "cons", "cons.mfestruct.dot", "cons.mfe" ]
        fileArgs = [ inputSeqBaseName + "." + fext for fext in argFileExts ]
        self.TestTypeV2_WithConstraints(*fileArgs);
    ##

    def TestTypeV3_NoConstraints(self, inputSeq, outputStruct, outputMFE):
        self.setUpMFERogersTypeTest()
        self.DescribeUnitTest("Basic MFE calculation without constraints (Rogers RNADB Historical Data)")
        (orgName, baseSeq) = GTFoldPythonUnitTests.LoadInputSequenceFromFile(inputSeq)
        self.NameOrganism(orgName)
        self.OrganismBaseSequence(baseSeq)
        self.DefineConstraints([])
        self.ComputeMFEData()
        (mfe, mfeStruct) = (GTFoldPythonUnitTests.LoadOutputMFEFromFile(outputMFE), 
                            GTFoldPythonUnitTests.LoadOutputStructFromFile(outputStruct))
        self.PrintTestInfo()
        self.AssertLastMFETupleEquals(mfe, mfeStruct)
    ##

    def RunTestTypeV3_NoConstraints(self, inputSeqBaseName):
        inputSeqBaseName = GTFoldPythonUnitTests.TESTDATADIR + "/" + inputSeqBaseName
        self.TestTypeV3_NoConstraints(inputSeqBaseName + ".fasta", 
                                      inputSeqBaseName + ".mfestruct.dot", 
                                      inputSeqBaseName + ".mfe");
    ##

    @unittest.skipIf(*UnitTestDecorArgs(MFE_BASE_TESTS))
    def test_MFE_test1_16S_K00421(self):
        GTFoldPythonUnitTests.RunTestTypeV1_NoConstraints(self, "16S/K00421")
    ##
     
    @unittest.skipIf(*UnitTestDecorArgs(MFE_BASE_TESTS))
    def test_MFE_test2_5S_EColiFa(self):
        GTFoldPythonUnitTests.RunTestTypeV1_NoConstraints(self, "5S/E.coli.fa")
    ##
     
    @unittest.skipIf(*UnitTestDecorArgs(MFE_BASE_TESTS))
    def test_MFE_test2_5S_EColiFa_withcons_RNAfold(self):
        GTFoldPythonUnitTests.RunTestTypeV2_WithConstraints(self, "5S/E.coli.fa")
    ##
    
    @unittest.skipIf(*UnitTestDecorArgs(MFE_BASE_TESTS))
    def test_MFE_test3_tRNA_yeastFa(self):
        GTFoldPythonUnitTests.RunTestTypeV1_NoConstraints(self, "tRNA/yeast.fa")
    ##
      
    @unittest.skipIf(*UnitTestDecorArgs(MFE_BASE_TESTS))
    def test_MFE_test3_tRNA_yeastFa_withcons_RNAfold(self):
        GTFoldPythonUnitTests.RunTestTypeV2_WithConstraints(self, "tRNA/yeast.fa")
    ##
      
    @unittest.skipIf(*UnitTestDecorArgs(MFE_BASE_TESTS))
    def test_MFE_test4_other_humanFa(self):
        GTFoldPythonUnitTests.RunTestTypeV1_NoConstraints(self, "other/human.fa")
    ##
       
    @unittest.skipIf(*UnitTestDecorArgs(MFE_BASE_TESTS))
    def test_MFE_test4_other_humanFa_withcons_RNAfold(self):
        GTFoldPythonUnitTests.RunTestTypeV2_WithConstraints(self, "other/human.fa")
    ##
    
    @unittest.skipIf(*UnitTestDecorArgs(MFE_BASE_TESTS))
    def test_MFE_test5_other_PSyringae(self):
        GTFoldPythonUnitTests.RunTestTypeV1_NoConstraints(self, "other/P.syringae")
    ##
  
    @unittest.skipIf(*UnitTestDecorArgs(MFE_BASE_TESTS))
    def test_MFE_test5_other_PSyringae_withcons_RNAfold(self):
        GTFoldPythonUnitTests.RunTestTypeV2_WithConstraints(self, "other/P.syringae")
    ##

    @unittest.skipIf(*UnitTestDecorArgs(MFE_RNADB_TESTS))
    def test_MFE_test6_RogersRNADB_verify_Aalbopictus6(self):
        GTFoldPythonUnitTests.RunTestTypeV3_NoConstraints(self, "rnadb_historical/A.albopictus.6")
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_RNADB_TESTS))
    def test_MFE_test7_RogersRNADB_verify_Linterrogans1(self):
        GTFoldPythonUnitTests.RunTestTypeV3_NoConstraints(self, "rnadb_historical/L.interrogans.1")
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_RNADB_TESTS))
    def test_MFE_test8_RogersRNADB_verify_Streptococcus_agalac1(self):
        GTFoldPythonUnitTests.RunTestTypeV3_NoConstraints(self, "rnadb_historical/Streptococcus_agalac.1")
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_RNADB_TESTS))
    def test_MFE_test9_RogersRNADB_verify_d23ePfalciparumA(self):
        GTFoldPythonUnitTests.RunTestTypeV3_NoConstraints(self, "rnadb_historical/d.23.e.P.falciparum.A")
    ##

    def RunMFECustomParametersTest(self, configParams, extraConfigParams, expectedResults):
        if 'unafold' in extraConfigParams and extraConfigParams['unafold'] != 0:
            self.setUpMFECustomParametersTypeTest(extraConfig=extraConfigParams, tpCode="UNAFold", tpParamsDir="UNAFold")
        else:
            self.setUpMFECustomParametersTypeTest(extraConfig=extraConfigParams)
        if 'dangle' in configParams:
            GTFoldPython.SetDangleParameter(configParams['dangle'])
        if 'tmismatch' in configParams:
            GTFoldPython.SetTerminalMismatch(configParams['tmismatch'])
        if 'limitcdist' in configParams:
            GTFoldPython.SetLimitContactDistance(configParams['limitcdist'])
        if 'prefilter' in configParams:
            GTFoldPython.SetPrefilterParameter(configParams['prefilter'])
        baseSeq = "GGUUAAGCGACUAAGCGUACACGGUGGAUGCCCUGGCAGUCAGAGGCGAUGAAGGACGUGCUAAUCUGCGAUAAGCGUCGGUAAGGUGAUAUGAA" + \
                  "CCGUUAUAACCGGCGAUUUCCGAAUGGGGAAACCCAGUGUGUUUCGACACACUAUCAUUAACUGAAUCCAUAGGUUAAUGAGGCGAACCGGGGGA" + \
                  "ACUGAAACAUCUAAGUACCCCGAGGAAAAGAAAUCAACCGAGAUUCCCCCAGUAGCGGCGAGCGAACGGGGAGCAGCCCAGAGCCUGAAUCAGUG" + \
                  "UGUGUGUUAGUGGAAGCGUCUGGAAAGGCGCGCGAUACAGGGUGACAGCCCCGUACACAAAAAUGCACAUGCUGUGAGCUCGAUGAGUAGGGCGG" + \
                  "GACACGUGGUAUCCUGUCUGAAUAUGGGGGGACCAUCCUCCAAGGCUAAAUACUCCUGACUGACCGAUAGUGAACCAGUACCGUGAGGGAAAGGC" + \
                  "GAAAAGAACCCCGGCGAGGGGAGUGAAAAAGAACCUGAAACCGUGUACGUACAAGCAGUGGGAGCACGCUUAGGCGUGUGACUGCGUACCUUUUG" + \
                  "UAUAAUGGGUCAGCGACUUAUAUUCUGUAGCAAGGUUAACCGAAUAGGGGAGCCGAAGGGAAACCGAGUCUUAACUGGGCGUUAAGUUGCAGGGU" + \
                  "AUAGACCCGAAACCCGGUGAUCUAGCCAUGGGCAGGUUGAAGGUUGGGUAACACUAACUGGAGGACCGAACCGACUAAUGUUGAAAAAUUAGCGG" + \
                  "AUGACUUGUGGCUGGGGGUGAAAGGCCAAUCAAACCGGGAGAUAGCUGGUUCUCCCCGAAAGCUAUUUAGGUAGCGCCUCGUGAAUUCAUCUCCG" + \
                  "GGGGUAGAGCACUGUUUCGGCAAGGGGGUCAUCCCGACUUACCAACCCGAUGCAAACUGCGAAUACCGGAGAAUGUUAUCACGGGAGACACACGG" + \
                  "CGGGUGCUAACGUCCGUCGUGAAGAGGGAAACAACCCAGACCGCCAGCUAAGGUCCCAAAGUCAUGGUUAAGUGGGAAACGAUGUGGGAAGGCCC" + \
                  "AGACAGCCAGGAUGUUGGCUUAGAAGCAGCCAUCAUUUAAAGAAAGCGUAAUAGCUCACUGGUCGAGUCGGCCUGCGCGGAAGAUGUAACGGGGC" + \
                  "UAAACCAUGCACCGAAGCUGCGGCAGCGACGCUUAUGCGUUGUUGGGUAGGGGAGCGUUCUGUAAGCCUGCGAAGGUGUGCUGUGAGGCAUGCUG" + \
                  "GAGGUAUCAGAAGUGCGAAUGCUGACAUAAGUAACGAUAAAGCGGGUGAAAAGCCCGCUCGCCGGAAGACCAAGGGUUCCUGUCCAACGUUAAUC" + \
                  "GGGGCAGGGUGAGUCGACCCCUAAGGCGAGGCCGAAAGGCGUAGUCGAUGGGAAACAGGUUAAUAUUCCUGUACUUGGUGUUACUGCGAAGGGGG" + \
                  "GACGGAGAAGGCUAUGUUGGCCGGGCGACGGUUGUCCCGGUUUAAGCGUGUAGGCUGGUUUUCCAGGCAAAUCCGGAAAAUCAAGGCUGAGGCGU" + \
                  "GAUGACGAGGCACUACGGUGCUGAAGCAACAAAUGCCCUGCUUCCAGGAAAAGCCUCUAAGCAUCAGGUAACAUCAAAUCGUACCCCAAACCGAC" + \
                  "ACAGGUGGUCAGGUAGAGAAUACCAAGGCGCUUGAGAGAACUCGGGUGAAGGAACUAGGCAAAAUGGUGCCGUAACUUCGGGAGAAGGCACGCUG" + \
                  "AUAUGUAGGUGAGGUCCCUCGCGGAUGGAGCUGAAAUCAGUCGAAGAUACCAGCUGGCUGCAACUGUUUAUUAAAAACACAGCACUGUGCAAACA" + \
                  "CGAAAGUGGACGUAUACGGUGUGACGCCUGCCCGGUGCCGGAAGGUUAAUUGAUGGGGUUAGCGCAAGCGAAGCUCUUGAUCGAAGCCCCGGUAA" + \
                  "ACGGCGGCCGUAACUAUAACGGUCCUAAGGUAGCGAAAUUCCUUGUCGGGUAAGUUCCGACCUGCACGAAUGGCGUAAUGAUGGCCAGGCUGUCU" + \
                  "CCACCCGAGACUCAGUGAAAUUGAACUCGCUGUGAAGAUGCAGUGUACCCGCGGCAAGACGGAAAGACCCCGUGAACCUUUACUAUAGCUUGACA" + \
                  "CUGAACAUUGAGCCUUGAUGUGUAGGAUAGGUGGGAGGCUUUGAAGUGUGGACGCCAGUCUGCAUGGAGCCGACCUUGAAAUACCACCCUUUAAU" + \
                  "GUUUGAUGUUCUAACGUUGACCCGUAAUCCGGGUUGCGGACAGUGUCUGGUGGGUAGUUUGACUGGGGCGGUCUCCUCCUAAAGAGUAACGGAGG" + \
                  "AGCACGAAGGUUGGCUAAUCCUGGUCGGACAUCAGGAGGUUAGUGCAAUGGCAUAAGCCAGCUUGACUGCGAGCGUGACGGCGCGAGCAGGUGCG" + \
                  "AAAGCAGGUCAUAGUGAUCCGGUGGUUCUGAAUGGAAGGGCCAUCGCUCAACGGAUAAAAGGUACUCCGGGGAUAACAGGCUGAUACCGCCCAAG" + \
                  "AGUUCAUAUCGACGGCGGUGUUUGGCACCUCGAUGUCGGCUCAUCACAUCCUGGGGCUGAAGUAGGUCCCAAGGGUAUGGCUGUUCGCCAUUUAA" + \
                  "AGUGGUACGCGAGCUGGGUUUAGAACGUCGUGAGACAGUUCGGUCCCUAUCUGCCGUGGGCGCUGGAGAACUGAGGGGGGCUGCUCCUAGUACGA" + \
                  "GAGGACCGGAGUGGACGCAUCACUGGUGUUCGGGUUGUCAUGCCAAUGGCACUGCCCGGUAGCUAAAUGCGGAAGAGAUAAGUGCUGAAAGCAUC" + \
                  "UAAGCACGAAACUUGCCCCGAGAUGAGUUCUCCCUGACCCUUUAAGGGUCCUGAAGGAACGUUGAAGACGACGACGUUGAUAGGCCGGGUGUGUA" + \
                  "AGCGCAGCGAUGCGUUGAGCUAACCGGUACUAAUGAACCGUGAGGCUUAACCUU"
        orgName = "Escherichia coli (J01695) -- 23S"
        self.DescribeUnitTest("MFE Custom Parameters Test -- Get the Python bindings output to match the GTFold utility")
        self.NameOrganism(orgName)
        self.OrganismBaseSequence(baseSeq)
        self.DefineConstraints([])
        self.PrintTestInfo(stackOffset=2)
        self.ComputeMFEData()
        (mfeExpected, mfeStructExpected) = (expectedResults['mfe'], expectedResults['mfe-struct'])
        self.AssertLastMFETupleEquals(mfeExpected, mfeStructExpected)
    ##

    @unittest.expectedFailure
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    @unittest.skipUnless(*UnitTestDecorArgs(NOT_PASSING, invertBoolean=True))
    def test__MFE_CustomParams_test01_rnafold(self):
        ### $ ./bin/gtmfe -v -d 0 -l 24 --prefilter 2 --rnafold d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 0, 
            'tmismatch'  : False,
            'limitcdist' : 24,
            'prefilter'  : 2,
        }
        extraConfigParamsDict = {
            'rnafold'    : 1, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -731.7000, 
            'mfe-struct' : ".((...((......))..))........(((((((.....))).))))......(((((((......)).....))))).(((((((.......))).))))...(((......)))..((((....))))((((((....))))))...((((((((.........)))))))).((....))..(((.(((..........))).)))...........((((......)))).((((.((.((.....))..))))))..(((........)))..(((.((.......)).)))..((((((....))))))....(((.((((....)))).)))((((.....((....)))))).((((...)))).((((((((.((...)).)))))))).....(((((((....)))))))........((((..((......))..))))..((....((....))....)).........((((.....)))).............(((......(((....)))..))).((..((((((....))))))..))..((((.....)))).(((((((...)))))))............((((..((.....))..))))...((....))..((((.....)))).....(((...((((....))))..))).....(((((.(((...))))))))...((((((......))))))...........(((.(((((........))))))))........(((((..........)))))......(.((((((........)))))).)...(((((....))))).(((((.((.......)))))))...............((.(((.(((....)))..))).)).......(((.....)))....(((((........)).))).......((((((((........)))))))).....(((......))).((((.........))))(((......)))....((.(....).)).((((....))))..........(((.(((((.......))))).)))....((..(((......)))..))(((((...))))).((((....).)))..(((.((........)).))).........(((((((((....))))))))).(((((...((.....))...)))))...((((((((....))))))))....((((.....))))...((((......)))).......(((((((.....)))))))....((((..(....).)))).((((..((.....)))))).((((......))))....(((.(.(((....))).).)))........(((((........)))))......((((.((.(....).))))))..............((((((((((...))).)))))))..........(.((((....)))).)...........((((..((....)).)))).....(((((....)))))...(((.....)))..(((((..(((.....)))..)))))...((((.(........)))))....(((......))).....((((.....))))....((((((((....))))))))..................(((((....(....).....)))))............(((((....))))).......((((..(((.......)))..)))).....((...(((((.....)))))..))...((((...(((....)))...))))..........((((..(((....))).))))........((((((.((....))..))))))...........(((.....))).((((((.......))))))..((((..........))))((((((.....))))))......(..((((.........))))..).(((((.....))))).((((((........))))))......(((.(((....))).)))..((((.......))))......................(((.((((..(...)..)))).)))....................(((..(((....)))..))).........................((((((((.(.....).)))))))).(((((((....)))))))......((..((.((....)).))..)).....(((((((...........))))))).((....)).......(((((((.....)))))))((((.((((....)))).)))).......((((..((((....))))..))))..((....)).((((.....)))).(((((((((.......)))))))))...(..((((..........))))..)................(((...((.......))...)))((((.....))))..((((......))))....(((((((((......)))))).))).......(((..(((((.....)))))..)))...........(((((((....))).)))).((.(((((.....))))).))...((..((....))..))(((((..((.(....).)).)))))((((((.......)))))).(((((((((....))))))..))).....((.....))...........(((((...........)))))............((((.....))))...(((((.....))))).......(((((((.......)))))))............((...((((((....))))))..))....((((.(....).)))).((((.....))))",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##

    @unittest.expectedFailure
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    @unittest.skipUnless(*UnitTestDecorArgs(NOT_PASSING, invertBoolean=True))
    def test__MFE_CustomParams_test02_rnafold(self):
        ### $ ./bin/gtmfe -v -d 1 -l 24 --prefilter 2 --rnafold d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 1, 
            'tmismatch'  : False,
            'limitcdist' : 24,
            'prefilter'  : 2,
        }
        extraConfigParamsDict = {
            'rnafold'    : 1, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -731.7000, 
            'mfe-struct' : ".((...((......))..))........(((((((.....))).))))......(((((((......)).....))))).(((((((.......))).))))...(((......)))..((((....))))((((((....))))))...((((((((.........)))))))).((....))..(((.(((..........))).)))...........((((......)))).((((.((.((.....))..))))))..(((........)))..(((.((.......)).)))..((((((....))))))....(((.((((....)))).)))((((.....((....)))))).((((...)))).((((((((.((...)).)))))))).....(((((((....)))))))........((((..((......))..))))..((....((....))....)).........((((.....)))).............(((......(((....)))..))).((..((((((....))))))..))..((((.....)))).(((((((...)))))))............((((..((.....))..))))...((....))..((((.....)))).....(((...((((....))))..))).....(((((.(((...))))))))...((((((......))))))...........(((.(((((........))))))))........(((((..........)))))......(.((((((........)))))).)...(((((....))))).(((((.((.......)))))))...............((.(((.(((....)))..))).)).......(((.....)))....(((((........)).))).......((((((((........)))))))).....(((......))).((((.........))))(((......)))....((.(....).)).((((....))))..........(((.(((((.......))))).)))....((..(((......)))..))(((((...))))).((((....).)))..(((.((........)).))).........(((((((((....))))))))).(((((...((.....))...)))))...((((((((....))))))))....((((.....))))...((((......)))).......(((((((.....)))))))....((((..(....).)))).((((..((.....)))))).((((......))))....(((.(.(((....))).).)))........(((((........)))))......((((.((.(....).))))))..............((((((((((...))).)))))))..........(.((((....)))).)...........((((..((....)).)))).....(((((....)))))...(((.....)))..(((((..(((.....)))..)))))...((((.(........)))))....(((......))).....((((.....))))....((((((((....))))))))..................(((((....(....).....)))))............(((((....))))).......((((..(((.......)))..)))).....((...(((((.....)))))..))...((((...(((....)))...))))..........((((..(((....))).))))........((((((.((....))..))))))...........(((.....))).((((((.......))))))..((((..........))))((((((.....))))))......(..((((.........))))..).(((((.....))))).((((((........))))))......(((.(((....))).)))..((((.......))))......................(((.((((..(...)..)))).)))....................(((..(((....)))..))).........................((((((((.(.....).)))))))).(((((((....)))))))......((..((.((....)).))..)).....(((((((...........))))))).((....)).......(((((((.....)))))))((((.((((....)))).)))).......((((..((((....))))..))))..((....)).((((.....)))).(((((((((.......)))))))))...(..((((..........))))..)................(((...((.......))...)))((((.....))))..((((......))))....(((((((((......)))))).))).......(((..(((((.....)))))..)))...........(((((((....))).)))).((.(((((.....))))).))...((..((....))..))(((((..((.(....).)).)))))((((((.......)))))).(((((((((....))))))..))).....((.....))...........(((((...........)))))............((((.....))))...(((((.....))))).......(((((((.......)))))))............((...((((((....))))))..))....((((.(....).)))).((((.....))))",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test03_rnafold(self):
        ### $ ./bin/gtmfe -v -d 1 -dS -l 24 --prefilter 2 --rnafold d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 1, 
            'tmismatch'  : False,
            'limitcdist' : 24,
            'prefilter'  : 2,
        }
        extraConfigParamsDict = {
            'rnafold'    : 1, 
            'unafold'    : 0,
            'dS'         : 1,
        }
        expectedResults = {
            'mfe'        : -731.7000, 
            'mfe-struct' : ".((...((......))..))........(((((((.....))).))))......(((((((......)).....))))).(((((((.......))).))))...(((......)))..((((....))))((((((....))))))...((((((((.........)))))))).((....))..(((.(((..........))).)))...........((((......)))).((((.((.((.....))..))))))..(((........)))..(((.((.......)).)))..((((((....))))))....(((.((((....)))).)))((((.....((....)))))).((((...)))).((((((((.((...)).)))))))).....(((((((....)))))))........((((..((......))..))))..((....((....))....)).........((((.....)))).............(((......(((....)))..))).((..((((((....))))))..))..((((.....)))).(((((((...)))))))............((((..((.....))..))))...((....))..((((.....)))).....(((...((((....))))..))).....(((((.(((...))))))))...((((((......))))))...........(((.(((((........))))))))........(((((..........)))))......(.((((((........)))))).)...(((((....))))).(((((.((.......)))))))...............((.(((.(((....)))..))).)).......(((.....)))....(((((........)).))).......((((((((........)))))))).....(((......))).((((.........))))(((......)))....((.(....).)).((((....))))..........(((.(((((.......))))).)))....((..(((......)))..))(((((...))))).((((....).)))..(((.((........)).))).........(((((((((....))))))))).(((((...((.....))...)))))...((((((((....))))))))....((((.....))))...((((......)))).......(((((((.....)))))))....((((..(....).)))).((((..((.....)))))).((((......))))....(((.(.(((....))).).)))........(((((........)))))......((((.((.(....).))))))..............((((((((((...))).)))))))..........(.((((....)))).)...........((((..((....)).)))).....(((((....)))))...(((.....)))..(((((..(((.....)))..)))))...((((.(........)))))....(((......))).....((((.....))))....((((((((....))))))))..................(((((....(....).....)))))............(((((....))))).......((((..(((.......)))..)))).....((...(((((.....)))))..))...((((...(((....)))...))))..........((((..(((....))).))))........((((((.((....))..))))))...........(((.....))).((((((.......))))))..((((..........))))((((((.....))))))......(..((((.........))))..).(((((.....))))).((((((........))))))......(((.(((....))).)))..((((.......))))......................(((.((((..(...)..)))).)))....................(((..(((....)))..))).........................((((((((.(.....).)))))))).(((((((....)))))))......((..((.((....)).))..)).....(((((((...........))))))).((....)).......(((((((.....)))))))((((.((((....)))).)))).......((((..((((....))))..))))..((....)).((((.....)))).(((((((((.......)))))))))...(..((((..........))))..)................(((...((.......))...)))((((.....))))..((((......))))....(((((((((......)))))).))).......(((..(((((.....)))))..)))...........(((((((....))).)))).((.(((((.....))))).))...((..((....))..))(((((..((.(....).)).)))))((((((.......)))))).(((((((((....))))))..))).....((.....))...........(((((...........)))))............((((.....))))...(((((.....))))).......(((((((.......)))))))............((...((((((....))))))..))....((((.(....).)))).((((.....))))",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test04_rnafold(self):
        ### $ ./bin/gtmfe -v -d 2 -l 24 --prefilter 2 --rnafold d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 2, 
            'tmismatch'  : False,
            'limitcdist' : 24,
            'prefilter'  : 2,
        }
        extraConfigParamsDict = {
            'rnafold'    : 1, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -731.7000, 
            'mfe-struct' : ".((...((......))..))........(((((((.....))).))))......(((((((......)).....))))).(((((((.......))).))))...(((......)))..((((....))))((((((....))))))...((((((((.........)))))))).((....))..(((.(((..........))).)))...........((((......)))).((((.((.((.....))..))))))..(((........)))..(((.((.......)).)))..((((((....))))))....(((.((((....)))).)))((((.....((....)))))).((((...)))).((((((((.((...)).)))))))).....(((((((....)))))))........((((..((......))..))))..((....((....))....)).........((((.....)))).............(((......(((....)))..))).((..((((((....))))))..))..((((.....)))).(((((((...)))))))............((((..((.....))..))))...((....))..((((.....)))).....(((...((((....))))..))).....(((((.(((...))))))))...((((((......))))))...........(((.(((((........))))))))........(((((..........)))))......(.((((((........)))))).)...(((((....))))).(((((.((.......)))))))...............((.(((.(((....)))..))).)).......(((.....)))....(((((........)).))).......((((((((........)))))))).....(((......))).((((.........))))(((......)))....((.(....).)).((((....))))..........(((.(((((.......))))).)))....((..(((......)))..))(((((...))))).((((....).)))..(((.((........)).))).........(((((((((....))))))))).(((((...((.....))...)))))...((((((((....))))))))....((((.....))))...((((......)))).......(((((((.....)))))))....((((..(....).)))).((((..((.....)))))).((((......))))....(((.(.(((....))).).)))........(((((........)))))......((((.((.(....).))))))..............((((((((((...))).)))))))..........(.((((....)))).)...........((((..((....)).)))).....(((((....)))))...(((.....)))..(((((..(((.....)))..)))))...((((.(........)))))....(((......))).....((((.....))))....((((((((....))))))))..................(((((....(....).....)))))............(((((....))))).......((((..(((.......)))..)))).....((...(((((.....)))))..))...((((...(((....)))...))))..........((((..(((....))).))))........((((((.((....))..))))))...........(((.....))).((((((.......))))))..((((..........))))((((((.....))))))......(..((((.........))))..).(((((.....))))).((((((........))))))......(((.(((....))).)))..((((.......))))......................(((.((((..(...)..)))).)))....................(((..(((....)))..))).........................((((((((.(.....).)))))))).(((((((....)))))))......((..((.((....)).))..)).....(((((((...........))))))).((....)).......(((((((.....)))))))((((.((((....)))).)))).......((((..((((....))))..))))..((....)).((((.....)))).(((((((((.......)))))))))...(..((((..........))))..)................(((...((.......))...)))((((.....))))..((((......))))....(((((((((......)))))).))).......(((..(((((.....)))))..)))...........(((((((....))).)))).((.(((((.....))))).))...((..((....))..))(((((..((.(....).)).)))))((((((.......)))))).(((((((((....))))))..))).....((.....))...........(((((...........)))))............((((.....))))...(((((.....))))).......(((((((.......)))))))............((...((((((....))))))..))....((((.(....).)))).((((.....))))",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test05_rnafold(self):
        ### $ ./bin/gtmfe -v -m -d 0 -l 24 --prefilter 2 --rnafold d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 0, 
            'tmismatch'  : True,
            'limitcdist' : 24,
            'prefilter'  : 2,
        }
        extraConfigParamsDict = {
            'rnafold'    : 1, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -731.7000, 
            'mfe-struct' : ".((...((......))..))........(((((((.....))).))))......(((((((......)).....))))).(((((((.......))).))))...(((......)))..((((....))))((((((....))))))...((((((((.........)))))))).((....))..(((.(((..........))).)))...........((((......)))).((((.((.((.....))..))))))..(((........)))..(((.((.......)).)))..((((((....))))))....(((.((((....)))).)))((((.....((....)))))).((((...)))).((((((((.((...)).)))))))).....(((((((....)))))))........((((..((......))..))))..((....((....))....)).........((((.....)))).............(((......(((....)))..))).((..((((((....))))))..))..((((.....)))).(((((((...)))))))............((((..((.....))..))))...((....))..((((.....)))).....(((...((((....))))..))).....(((((.(((...))))))))...((((((......))))))...........(((.(((((........))))))))........(((((..........)))))......(.((((((........)))))).)...(((((....))))).(((((.((.......)))))))...............((.(((.(((....)))..))).)).......(((.....)))....(((((........)).))).......((((((((........)))))))).....(((......))).((((.........))))(((......)))....((.(....).)).((((....))))..........(((.(((((.......))))).)))....((..(((......)))..))(((((...))))).((((....).)))..(((.((........)).))).........(((((((((....))))))))).(((((...((.....))...)))))...((((((((....))))))))....((((.....))))...((((......)))).......(((((((.....)))))))....((((..(....).)))).((((..((.....)))))).((((......))))....(((.(.(((....))).).)))........(((((........)))))......((((.((.(....).))))))..............((((((((((...))).)))))))..........(.((((....)))).)...........((((..((....)).)))).....(((((....)))))...(((.....)))..(((((..(((.....)))..)))))...((((.(........)))))....(((......))).....((((.....))))....((((((((....))))))))..................(((((....(....).....)))))............(((((....))))).......((((..(((.......)))..)))).....((...(((((.....)))))..))...((((...(((....)))...))))..........((((..(((....))).))))........((((((.((....))..))))))...........(((.....))).((((((.......))))))..((((..........))))((((((.....))))))......(..((((.........))))..).(((((.....))))).((((((........))))))......(((.(((....))).)))..((((.......))))......................(((.((((..(...)..)))).)))....................(((..(((....)))..))).........................((((((((.(.....).)))))))).(((((((....)))))))......((..((.((....)).))..)).....(((((((...........))))))).((....)).......(((((((.....)))))))((((.((((....)))).)))).......((((..((((....))))..))))..((....)).((((.....)))).(((((((((.......)))))))))...(..((((..........))))..)................(((...((.......))...)))((((.....))))..((((......))))....(((((((((......)))))).))).......(((..(((((.....)))))..)))...........(((((((....))).)))).((.(((((.....))))).))...((..((....))..))(((((..((.(....).)).)))))((((((.......)))))).(((((((((....))))))..))).....((.....))...........(((((...........)))))............((((.....))))...(((((.....))))).......(((((((.......)))))))............((...((((((....))))))..))....((((.(....).)))).((((.....))))",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test06_rnafold(self):
        ### $ ./bin/gtmfe -v -m -d 1 -l 24 --prefilter 2 --rnafold d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 1, 
            'tmismatch'  : True,
            'limitcdist' : 24,
            'prefilter'  : 2,
        }
        extraConfigParamsDict = {
            'rnafold'    : 1, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -731.7000, 
            'mfe-struct' : ".((...((......))..))........(((((((.....))).))))......(((((((......)).....))))).(((((((.......))).))))...(((......)))..((((....))))((((((....))))))...((((((((.........)))))))).((....))..(((.(((..........))).)))...........((((......)))).((((.((.((.....))..))))))..(((........)))..(((.((.......)).)))..((((((....))))))....(((.((((....)))).)))((((.....((....)))))).((((...)))).((((((((.((...)).)))))))).....(((((((....)))))))........((((..((......))..))))..((....((....))....)).........((((.....)))).............(((......(((....)))..))).((..((((((....))))))..))..((((.....)))).(((((((...)))))))............((((..((.....))..))))...((....))..((((.....)))).....(((...((((....))))..))).....(((((.(((...))))))))...((((((......))))))...........(((.(((((........))))))))........(((((..........)))))......(.((((((........)))))).)...(((((....))))).(((((.((.......)))))))...............((.(((.(((....)))..))).)).......(((.....)))....(((((........)).))).......((((((((........)))))))).....(((......))).((((.........))))(((......)))....((.(....).)).((((....))))..........(((.(((((.......))))).)))....((..(((......)))..))(((((...))))).((((....).)))..(((.((........)).))).........(((((((((....))))))))).(((((...((.....))...)))))...((((((((....))))))))....((((.....))))...((((......)))).......(((((((.....)))))))....((((..(....).)))).((((..((.....)))))).((((......))))....(((.(.(((....))).).)))........(((((........)))))......((((.((.(....).))))))..............((((((((((...))).)))))))..........(.((((....)))).)...........((((..((....)).)))).....(((((....)))))...(((.....)))..(((((..(((.....)))..)))))...((((.(........)))))....(((......))).....((((.....))))....((((((((....))))))))..................(((((....(....).....)))))............(((((....))))).......((((..(((.......)))..)))).....((...(((((.....)))))..))...((((...(((....)))...))))..........((((..(((....))).))))........((((((.((....))..))))))...........(((.....))).((((((.......))))))..((((..........))))((((((.....))))))......(..((((.........))))..).(((((.....))))).((((((........))))))......(((.(((....))).)))..((((.......))))......................(((.((((..(...)..)))).)))....................(((..(((....)))..))).........................((((((((.(.....).)))))))).(((((((....)))))))......((..((.((....)).))..)).....(((((((...........))))))).((....)).......(((((((.....)))))))((((.((((....)))).)))).......((((..((((....))))..))))..((....)).((((.....)))).(((((((((.......)))))))))...(..((((..........))))..)................(((...((.......))...)))((((.....))))..((((......))))....(((((((((......)))))).))).......(((..(((((.....)))))..)))...........(((((((....))).)))).((.(((((.....))))).))...((..((....))..))(((((..((.(....).)).)))))((((((.......)))))).(((((((((....))))))..))).....((.....))...........(((((...........)))))............((((.....))))...(((((.....))))).......(((((((.......)))))))............((...((((((....))))))..))....((((.(....).)))).((((.....))))",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test07_rnafold(self):
        ### $ ./bin/gtmfe -v -m -d 1 -dS -l 24 --prefilter 2 --rnafold d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 1, 
            'tmismatch'  : True,
            'limitcdist' : 24,
            'prefilter'  : 2,
        }
        extraConfigParamsDict = {
            'rnafold'    : 1, 
            'unafold'    : 0,
            'dS'         : 1,
        }
        expectedResults = {
            'mfe'        : -731.7000, 
            'mfe-struct' : ".((...((......))..))........(((((((.....))).))))......(((((((......)).....))))).(((((((.......))).))))...(((......)))..((((....))))((((((....))))))...((((((((.........)))))))).((....))..(((.(((..........))).)))...........((((......)))).((((.((.((.....))..))))))..(((........)))..(((.((.......)).)))..((((((....))))))....(((.((((....)))).)))((((.....((....)))))).((((...)))).((((((((.((...)).)))))))).....(((((((....)))))))........((((..((......))..))))..((....((....))....)).........((((.....)))).............(((......(((....)))..))).((..((((((....))))))..))..((((.....)))).(((((((...)))))))............((((..((.....))..))))...((....))..((((.....)))).....(((...((((....))))..))).....(((((.(((...))))))))...((((((......))))))...........(((.(((((........))))))))........(((((..........)))))......(.((((((........)))))).)...(((((....))))).(((((.((.......)))))))...............((.(((.(((....)))..))).)).......(((.....)))....(((((........)).))).......((((((((........)))))))).....(((......))).((((.........))))(((......)))....((.(....).)).((((....))))..........(((.(((((.......))))).)))....((..(((......)))..))(((((...))))).((((....).)))..(((.((........)).))).........(((((((((....))))))))).(((((...((.....))...)))))...((((((((....))))))))....((((.....))))...((((......)))).......(((((((.....)))))))....((((..(....).)))).((((..((.....)))))).((((......))))....(((.(.(((....))).).)))........(((((........)))))......((((.((.(....).))))))..............((((((((((...))).)))))))..........(.((((....)))).)...........((((..((....)).)))).....(((((....)))))...(((.....)))..(((((..(((.....)))..)))))...((((.(........)))))....(((......))).....((((.....))))....((((((((....))))))))..................(((((....(....).....)))))............(((((....))))).......((((..(((.......)))..)))).....((...(((((.....)))))..))...((((...(((....)))...))))..........((((..(((....))).))))........((((((.((....))..))))))...........(((.....))).((((((.......))))))..((((..........))))((((((.....))))))......(..((((.........))))..).(((((.....))))).((((((........))))))......(((.(((....))).)))..((((.......))))......................(((.((((..(...)..)))).)))....................(((..(((....)))..))).........................((((((((.(.....).)))))))).(((((((....)))))))......((..((.((....)).))..)).....(((((((...........))))))).((....)).......(((((((.....)))))))((((.((((....)))).)))).......((((..((((....))))..))))..((....)).((((.....)))).(((((((((.......)))))))))...(..((((..........))))..)................(((...((.......))...)))((((.....))))..((((......))))....(((((((((......)))))).))).......(((..(((((.....)))))..)))...........(((((((....))).)))).((.(((((.....))))).))...((..((....))..))(((((..((.(....).)).)))))((((((.......)))))).(((((((((....))))))..))).....((.....))...........(((((...........)))))............((((.....))))...(((((.....))))).......(((((((.......)))))))............((...((((((....))))))..))....((((.(....).)))).((((.....))))",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test08_rnafold(self):
        ### $ ./bin/gtmfe -v -m -d 2 -l 24 --prefilter 2 --rnafold d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 2, 
            'tmismatch'  : True,
            'limitcdist' : 24,
            'prefilter'  : 2,
        }
        extraConfigParamsDict = {
            'rnafold'    : 1, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -731.7000, 
            'mfe-struct' : ".((...((......))..))........(((((((.....))).))))......(((((((......)).....))))).(((((((.......))).))))...(((......)))..((((....))))((((((....))))))...((((((((.........)))))))).((....))..(((.(((..........))).)))...........((((......)))).((((.((.((.....))..))))))..(((........)))..(((.((.......)).)))..((((((....))))))....(((.((((....)))).)))((((.....((....)))))).((((...)))).((((((((.((...)).)))))))).....(((((((....)))))))........((((..((......))..))))..((....((....))....)).........((((.....)))).............(((......(((....)))..))).((..((((((....))))))..))..((((.....)))).(((((((...)))))))............((((..((.....))..))))...((....))..((((.....)))).....(((...((((....))))..))).....(((((.(((...))))))))...((((((......))))))...........(((.(((((........))))))))........(((((..........)))))......(.((((((........)))))).)...(((((....))))).(((((.((.......)))))))...............((.(((.(((....)))..))).)).......(((.....)))....(((((........)).))).......((((((((........)))))))).....(((......))).((((.........))))(((......)))....((.(....).)).((((....))))..........(((.(((((.......))))).)))....((..(((......)))..))(((((...))))).((((....).)))..(((.((........)).))).........(((((((((....))))))))).(((((...((.....))...)))))...((((((((....))))))))....((((.....))))...((((......)))).......(((((((.....)))))))....((((..(....).)))).((((..((.....)))))).((((......))))....(((.(.(((....))).).)))........(((((........)))))......((((.((.(....).))))))..............((((((((((...))).)))))))..........(.((((....)))).)...........((((..((....)).)))).....(((((....)))))...(((.....)))..(((((..(((.....)))..)))))...((((.(........)))))....(((......))).....((((.....))))....((((((((....))))))))..................(((((....(....).....)))))............(((((....))))).......((((..(((.......)))..)))).....((...(((((.....)))))..))...((((...(((....)))...))))..........((((..(((....))).))))........((((((.((....))..))))))...........(((.....))).((((((.......))))))..((((..........))))((((((.....))))))......(..((((.........))))..).(((((.....))))).((((((........))))))......(((.(((....))).)))..((((.......))))......................(((.((((..(...)..)))).)))....................(((..(((....)))..))).........................((((((((.(.....).)))))))).(((((((....)))))))......((..((.((....)).))..)).....(((((((...........))))))).((....)).......(((((((.....)))))))((((.((((....)))).)))).......((((..((((....))))..))))..((....)).((((.....)))).(((((((((.......)))))))))...(..((((..........))))..)................(((...((.......))...)))((((.....))))..((((......))))....(((((((((......)))))).))).......(((..(((((.....)))))..)))...........(((((((....))).)))).((.(((((.....))))).))...((..((....))..))(((((..((.(....).)).)))))((((((.......)))))).(((((((((....))))))..))).....((.....))...........(((((...........)))))............((((.....))))...(((((.....))))).......(((((((.......)))))))............((...((((((....))))))..))....((((.(....).)))).((((.....))))",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    def test__MFE_CustomParams_test09_rnafold(self):
        ### $ ./bin/gtmfe -v -d 0 -l 10 --prefilter 2 --rnafold d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 0, 
            'tmismatch'  : False,
            'limitcdist' : 10,
            'prefilter'  : 2,
        }
        extraConfigParamsDict = {
            'rnafold'    : 1, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -257.6000, 
            'mfe-struct' : "......((......))............(((....))).............................((.....))..............................((......))....(((....))).....................................................(((.....))).............((....)).............................((.....)).....(((.....)))..................................(((....)))............(((....)))...............(((.....))).((((...))))...(((.....)))...................((....))..............................................((....))................(((.....)))......................(((....)))..((.......)).(((....)))..........................((((...))))...............((....)).....((....))...((....))............(((.....))).............(((.....))).......(((...))).........................(((....)))....(((....))).............................(((.....)))....................((......))...........(((.....)))..........(((....)))........(((....)))..((((...))))...............(((.....)))......................(....)....(((....))).(((.....)))......(....)...........((......)).....................(....).....(((....))).................(((....)))..................((......))......((((...)))).....(....)........((......))..........((((...))))..(((....)))...........(((.....))).....(((....)))...(((....)))....................((....))......................(((.....))).......(....)......((.......))..((.....))......((....))...............(((....)))..........(....)...........((.......))..............(....).......(((.....))).......(((.....)))......((......)).((....)).....................((....))............(((....))).....(((.....))).(((....))).....((......))............................((......))............................(((....)))....................(((....)))...(((....)))...................(((....)))..........(((....)))............((.....))....................((.....))...(((....))).........((((...))))........(((....)))...............((....))...................(((.....)))...........................................(((.....))).......(((.....)))......(((...)))..(((.....))).................................(((....)))........((.......))..........................................................................(((....))).....((......)).........................................(((.....))).....((((...)))).................(((.....)))......................((....)).......(((.....)))....................(((....))).((......))..........((....))...(((....))).............(((.....)))..(((.....))).................((....))..........((......))........................(((.....))).(((....)))............................((....))...(((.....))).......(((...)))................(((....)))................(((...)))...............(((.....))).....(....)..((.....))........(((.....))).......((((...))))..........((.....))............(((.....))).............(((.....)))...............(((.....)))(((....)))..........((((...))))...........(((....)))......((.....)).................((....)).........",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test10_rnafold(self):
        ### $ ./bin/gtmfe -v -d 1 -l 10 --prefilter 2 --rnafold d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 1, 
            'tmismatch'  : False,
            'limitcdist' : 10,
            'prefilter'  : 2,
        }
        extraConfigParamsDict = {
            'rnafold'    : 1, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -257.6000, 
            'mfe-struct' : "......((......))............(((....))).............................((.....))..............................((......))....(((....))).....................................................(((.....))).............((....)).............................((.....)).....(((.....)))..................................(((....)))............(((....)))...............(((.....))).((((...))))...(((.....)))...................((....))..............................................((....))................(((.....)))......................(((....)))..((.......)).(((....)))..........................((((...))))...............((....)).....((....))...((....))............(((.....))).............(((.....))).......(((...))).........................(((....)))....(((....))).............................(((.....)))....................((......))...........(((.....)))..........(((....)))........(((....)))..((((...))))...............(((.....)))......................(....)....(((....))).(((.....)))......(....)...........((......)).....................(....).....(((....))).................(((....)))..................((......))......((((...)))).....(....)........((......))..........((((...))))..(((....)))...........(((.....))).....(((....)))...(((....)))....................((....))......................(((.....))).......(....)......((.......))..((.....))......((....))...............(((....)))..........(....)...........((.......))..............(....).......(((.....))).......(((.....)))......((......)).((....)).....................((....))............(((....))).....(((.....))).(((....))).....((......))............................((......))............................(((....)))....................(((....)))...(((....)))...................(((....)))..........(((....)))............((.....))....................((.....))...(((....))).........((((...))))........(((....)))...............((....))...................(((.....)))...........................................(((.....))).......(((.....)))......(((...)))..(((.....))).................................(((....)))........((.......))..........................................................................(((....))).....((......)).........................................(((.....))).....((((...)))).................(((.....)))......................((....)).......(((.....)))....................(((....))).((......))..........((....))...(((....))).............(((.....)))..(((.....))).................((....))..........((......))........................(((.....))).(((....)))............................((....))...(((.....))).......(((...)))................(((....)))................(((...)))...............(((.....))).....(....)..((.....))........(((.....))).......((((...))))..........((.....))............(((.....))).............(((.....)))...............(((.....)))(((....)))..........((((...))))...........(((....)))......((.....)).................((....)).........",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test11_rnafold(self):
        ### $ ./bin/gtmfe -v -d 1 -dS -l 10 --prefilter 2 --rnafold d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 1, 
            'tmismatch'  : False,
            'limitcdist' : 10,
            'prefilter'  : 2,
        }
        extraConfigParamsDict = {
            'rnafold'    : 1, 
            'unafold'    : 0,
            'dS'         : 1,
        }
        expectedResults = {
            'mfe'        : -257.6000, 
            'mfe-struct' : "......((......))............(((....))).............................((.....))..............................((......))....(((....))).....................................................(((.....))).............((....)).............................((.....)).....(((.....)))..................................(((....)))............(((....)))...............(((.....))).((((...))))...(((.....)))...................((....))..............................................((....))................(((.....)))......................(((....)))..((.......)).(((....)))..........................((((...))))...............((....)).....((....))...((....))............(((.....))).............(((.....))).......(((...))).........................(((....)))....(((....))).............................(((.....)))....................((......))...........(((.....)))..........(((....)))........(((....)))..((((...))))...............(((.....)))......................(....)....(((....))).(((.....)))......(....)...........((......)).....................(....).....(((....))).................(((....)))..................((......))......((((...)))).....(....)........((......))..........((((...))))..(((....)))...........(((.....))).....(((....)))...(((....)))....................((....))......................(((.....))).......(....)......((.......))..((.....))......((....))...............(((....)))..........(....)...........((.......))..............(....).......(((.....))).......(((.....)))......((......)).((....)).....................((....))............(((....))).....(((.....))).(((....))).....((......))............................((......))............................(((....)))....................(((....)))...(((....)))...................(((....)))..........(((....)))............((.....))....................((.....))...(((....))).........((((...))))........(((....)))...............((....))...................(((.....)))...........................................(((.....))).......(((.....)))......(((...)))..(((.....))).................................(((....)))........((.......))..........................................................................(((....))).....((......)).........................................(((.....))).....((((...)))).................(((.....)))......................((....)).......(((.....)))....................(((....))).((......))..........((....))...(((....))).............(((.....)))..(((.....))).................((....))..........((......))........................(((.....))).(((....)))............................((....))...(((.....))).......(((...)))................(((....)))................(((...)))...............(((.....))).....(....)..((.....))........(((.....))).......((((...))))..........((.....))............(((.....))).............(((.....)))...............(((.....)))(((....)))..........((((...))))...........(((....)))......((.....)).................((....)).........",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test12_rnafold(self):
        ### $ ./bin/gtmfe -v -d 2 -l 10 --prefilter 2 --rnafold d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 2, 
            'tmismatch'  : False,
            'limitcdist' : 10,
            'prefilter'  : 2,
        }
        extraConfigParamsDict = {
            'rnafold'    : 1, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -257.6000, 
            'mfe-struct' : "......((......))............(((....))).............................((.....))..............................((......))....(((....))).....................................................(((.....))).............((....)).............................((.....)).....(((.....)))..................................(((....)))............(((....)))...............(((.....))).((((...))))...(((.....)))...................((....))..............................................((....))................(((.....)))......................(((....)))..((.......)).(((....)))..........................((((...))))...............((....)).....((....))...((....))............(((.....))).............(((.....))).......(((...))).........................(((....)))....(((....))).............................(((.....)))....................((......))...........(((.....)))..........(((....)))........(((....)))..((((...))))...............(((.....)))......................(....)....(((....))).(((.....)))......(....)...........((......)).....................(....).....(((....))).................(((....)))..................((......))......((((...)))).....(....)........((......))..........((((...))))..(((....)))...........(((.....))).....(((....)))...(((....)))....................((....))......................(((.....))).......(....)......((.......))..((.....))......((....))...............(((....)))..........(....)...........((.......))..............(....).......(((.....))).......(((.....)))......((......)).((....)).....................((....))............(((....))).....(((.....))).(((....))).....((......))............................((......))............................(((....)))....................(((....)))...(((....)))...................(((....)))..........(((....)))............((.....))....................((.....))...(((....))).........((((...))))........(((....)))...............((....))...................(((.....)))...........................................(((.....))).......(((.....)))......(((...)))..(((.....))).................................(((....)))........((.......))..........................................................................(((....))).....((......)).........................................(((.....))).....((((...)))).................(((.....)))......................((....)).......(((.....)))....................(((....))).((......))..........((....))...(((....))).............(((.....)))..(((.....))).................((....))..........((......))........................(((.....))).(((....)))............................((....))...(((.....))).......(((...)))................(((....)))................(((...)))...............(((.....))).....(....)..((.....))........(((.....))).......((((...))))..........((.....))............(((.....))).............(((.....)))...............(((.....)))(((....)))..........((((...))))...........(((....)))......((.....)).................((....)).........",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test13_rnafold(self):
        ### $ ./bin/gtmfe -v -m -d 0 -l 10 --prefilter 2 --rnafold d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 0, 
            'tmismatch'  : True,
            'limitcdist' : 10,
            'prefilter'  : 2,
        }
        extraConfigParamsDict = {
            'rnafold'    : 1, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -257.6000, 
            'mfe-struct' : "......((......))............(((....))).............................((.....))..............................((......))....(((....))).....................................................(((.....))).............((....)).............................((.....)).....(((.....)))..................................(((....)))............(((....)))...............(((.....))).((((...))))...(((.....)))...................((....))..............................................((....))................(((.....)))......................(((....)))..((.......)).(((....)))..........................((((...))))...............((....)).....((....))...((....))............(((.....))).............(((.....))).......(((...))).........................(((....)))....(((....))).............................(((.....)))....................((......))...........(((.....)))..........(((....)))........(((....)))..((((...))))...............(((.....)))......................(....)....(((....))).(((.....)))......(....)...........((......)).....................(....).....(((....))).................(((....)))..................((......))......((((...)))).....(....)........((......))..........((((...))))..(((....)))...........(((.....))).....(((....)))...(((....)))....................((....))......................(((.....))).......(....)......((.......))..((.....))......((....))...............(((....)))..........(....)...........((.......))..............(....).......(((.....))).......(((.....)))......((......)).((....)).....................((....))............(((....))).....(((.....))).(((....))).....((......))............................((......))............................(((....)))....................(((....)))...(((....)))...................(((....)))..........(((....)))............((.....))....................((.....))...(((....))).........((((...))))........(((....)))...............((....))...................(((.....)))...........................................(((.....))).......(((.....)))......(((...)))..(((.....))).................................(((....)))........((.......))..........................................................................(((....))).....((......)).........................................(((.....))).....((((...)))).................(((.....)))......................((....)).......(((.....)))....................(((....))).((......))..........((....))...(((....))).............(((.....)))..(((.....))).................((....))..........((......))........................(((.....))).(((....)))............................((....))...(((.....))).......(((...)))................(((....)))................(((...)))...............(((.....))).....(....)..((.....))........(((.....))).......((((...))))..........((.....))............(((.....))).............(((.....)))...............(((.....)))(((....)))..........((((...))))...........(((....)))......((.....)).................((....)).........",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test14_rnafold(self):
        ### $ ./bin/gtmfe -v -m -d 1 -l 10 --prefilter 2 --rnafold d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 1, 
            'tmismatch'  : True,
            'limitcdist' : 10,
            'prefilter'  : 2,
        }
        extraConfigParamsDict = {
            'rnafold'    : 1, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -257.6000, 
            'mfe-struct' : "......((......))............(((....))).............................((.....))..............................((......))....(((....))).....................................................(((.....))).............((....)).............................((.....)).....(((.....)))..................................(((....)))............(((....)))...............(((.....))).((((...))))...(((.....)))...................((....))..............................................((....))................(((.....)))......................(((....)))..((.......)).(((....)))..........................((((...))))...............((....)).....((....))...((....))............(((.....))).............(((.....))).......(((...))).........................(((....)))....(((....))).............................(((.....)))....................((......))...........(((.....)))..........(((....)))........(((....)))..((((...))))...............(((.....)))......................(....)....(((....))).(((.....)))......(....)...........((......)).....................(....).....(((....))).................(((....)))..................((......))......((((...)))).....(....)........((......))..........((((...))))..(((....)))...........(((.....))).....(((....)))...(((....)))....................((....))......................(((.....))).......(....)......((.......))..((.....))......((....))...............(((....)))..........(....)...........((.......))..............(....).......(((.....))).......(((.....)))......((......)).((....)).....................((....))............(((....))).....(((.....))).(((....))).....((......))............................((......))............................(((....)))....................(((....)))...(((....)))...................(((....)))..........(((....)))............((.....))....................((.....))...(((....))).........((((...))))........(((....)))...............((....))...................(((.....)))...........................................(((.....))).......(((.....)))......(((...)))..(((.....))).................................(((....)))........((.......))..........................................................................(((....))).....((......)).........................................(((.....))).....((((...)))).................(((.....)))......................((....)).......(((.....)))....................(((....))).((......))..........((....))...(((....))).............(((.....)))..(((.....))).................((....))..........((......))........................(((.....))).(((....)))............................((....))...(((.....))).......(((...)))................(((....)))................(((...)))...............(((.....))).....(....)..((.....))........(((.....))).......((((...))))..........((.....))............(((.....))).............(((.....)))...............(((.....)))(((....)))..........((((...))))...........(((....)))......((.....)).................((....)).........",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test15_rnafold(self):
        ### $ ./bin/gtmfe -v -m -d 1 -dS -l 10 --prefilter 2 --rnafold d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 1, 
            'tmismatch'  : True,
            'limitcdist' : 10,
            'prefilter'  : 2,
        }
        extraConfigParamsDict = {
            'rnafold'    : 1, 
            'unafold'    : 0,
            'dS'         : 1,
        }
        expectedResults = {
            'mfe'        : -257.6000, 
            'mfe-struct' : "......((......))............(((....))).............................((.....))..............................((......))....(((....))).....................................................(((.....))).............((....)).............................((.....)).....(((.....)))..................................(((....)))............(((....)))...............(((.....))).((((...))))...(((.....)))...................((....))..............................................((....))................(((.....)))......................(((....)))..((.......)).(((....)))..........................((((...))))...............((....)).....((....))...((....))............(((.....))).............(((.....))).......(((...))).........................(((....)))....(((....))).............................(((.....)))....................((......))...........(((.....)))..........(((....)))........(((....)))..((((...))))...............(((.....)))......................(....)....(((....))).(((.....)))......(....)...........((......)).....................(....).....(((....))).................(((....)))..................((......))......((((...)))).....(....)........((......))..........((((...))))..(((....)))...........(((.....))).....(((....)))...(((....)))....................((....))......................(((.....))).......(....)......((.......))..((.....))......((....))...............(((....)))..........(....)...........((.......))..............(....).......(((.....))).......(((.....)))......((......)).((....)).....................((....))............(((....))).....(((.....))).(((....))).....((......))............................((......))............................(((....)))....................(((....)))...(((....)))...................(((....)))..........(((....)))............((.....))....................((.....))...(((....))).........((((...))))........(((....)))...............((....))...................(((.....)))...........................................(((.....))).......(((.....)))......(((...)))..(((.....))).................................(((....)))........((.......))..........................................................................(((....))).....((......)).........................................(((.....))).....((((...)))).................(((.....)))......................((....)).......(((.....)))....................(((....))).((......))..........((....))...(((....))).............(((.....)))..(((.....))).................((....))..........((......))........................(((.....))).(((....)))............................((....))...(((.....))).......(((...)))................(((....)))................(((...)))...............(((.....))).....(....)..((.....))........(((.....))).......((((...))))..........((.....))............(((.....))).............(((.....)))...............(((.....)))(((....)))..........((((...))))...........(((....)))......((.....)).................((....)).........",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test16_rnafold(self):
        ### $ ./bin/gtmfe -v -m -d 2 -l 10 --prefilter 2 --rnafold d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 2, 
            'tmismatch'  : True,
            'limitcdist' : 10,
            'prefilter'  : 2,
        }
        extraConfigParamsDict = {
            'rnafold'    : 1, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -257.6000, 
            'mfe-struct' : "......((......))............(((....))).............................((.....))..............................((......))....(((....))).....................................................(((.....))).............((....)).............................((.....)).....(((.....)))..................................(((....)))............(((....)))...............(((.....))).((((...))))...(((.....)))...................((....))..............................................((....))................(((.....)))......................(((....)))..((.......)).(((....)))..........................((((...))))...............((....)).....((....))...((....))............(((.....))).............(((.....))).......(((...))).........................(((....)))....(((....))).............................(((.....)))....................((......))...........(((.....)))..........(((....)))........(((....)))..((((...))))...............(((.....)))......................(....)....(((....))).(((.....)))......(....)...........((......)).....................(....).....(((....))).................(((....)))..................((......))......((((...)))).....(....)........((......))..........((((...))))..(((....)))...........(((.....))).....(((....)))...(((....)))....................((....))......................(((.....))).......(....)......((.......))..((.....))......((....))...............(((....)))..........(....)...........((.......))..............(....).......(((.....))).......(((.....)))......((......)).((....)).....................((....))............(((....))).....(((.....))).(((....))).....((......))............................((......))............................(((....)))....................(((....)))...(((....)))...................(((....)))..........(((....)))............((.....))....................((.....))...(((....))).........((((...))))........(((....)))...............((....))...................(((.....)))...........................................(((.....))).......(((.....)))......(((...)))..(((.....))).................................(((....)))........((.......))..........................................................................(((....))).....((......)).........................................(((.....))).....((((...)))).................(((.....)))......................((....)).......(((.....)))....................(((....))).((......))..........((....))...(((....))).............(((.....)))..(((.....))).................((....))..........((......))........................(((.....))).(((....)))............................((....))...(((.....))).......(((...)))................(((....)))................(((...)))...............(((.....))).....(....)..((.....))........(((.....))).......((((...))))..........((.....))............(((.....))).............(((.....)))...............(((.....)))(((....)))..........((((...))))...........(((....)))......((.....)).................((....)).........",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##

    @unittest.expectedFailure
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    @unittest.skipUnless(*UnitTestDecorArgs(NOT_PASSING, invertBoolean=True)) 
    def test__MFE_CustomParams_test01_unafold(self):
        ### $ export GTFOLDDATADIR=$(greadlink -f Testing/ExtraGTFoldThermoData/DefaultUNAFold)
        ### $ ./bin/gtmfe -v -d 0 -l 24 --prefilter 2 --unafold d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 0, 
            'tmismatch'  : False,
            'limitcdist' : 24,
            'prefilter'  : 2,
        }
        extraConfigParamsDict = {
            'rnafold'    : 0, 
            'unafold'    : 1,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -709.0000, 
            'mfe-struct' : ".((...((......))..))........(((((((.....))).))))......(((((((......)).....))))).(((((((.......))).))))...(((......)))..((((....))))((((((....))))))...((((((((.........)))))))).((....))..(((.(((..........))).)))...........((((......)))).((((.((.((.....))..)))))).......((..(((((...))).)).))...........((((((....))))))....(((.((((....)))).)))((((.....((....)))))).((((...)))).((((((((.((...)).)))))))).....(((((((....)))))))........((((..((......))..))))..((....((....))....)).........((((.....)))).............(((......(((....)))..))).((..((((((....))))))..))....((((..........))))..((.((.........)).))..((((..((.....))..))))...((....))..((((.....)))).....(((...((((....))))..))).....(((((.(((...))))))))...((((((......))))))((....))...(((.(((((........))))))))........(((((..........)))))........((((((........)))))).....(((((....))))).(((((.((.......)))))))...............((.(((.(((....)))..))).)).......(((.....)))....(((((........)).))).......((((((((........)))))))).....(((......))).((((.........)))).......(((.(((........))).)))((((....))))...((((((....))))))........((..((.......))..))......((.((..(((((...))))))).))...........(((.((........)).))).........(((((((((....))))))))).(((((...((.....))...)))))...((..((((....))))..))....((((.....))))...((((......)))).......(((((((.....))))))).(((((....))...))).(((((((..((.....))))))))).....(((.((.....))))).(((....)))..............(((((........))))).(((.((......)).))).......................(((((((((...))).))))))...(((......)))...(((((.((.....)))))))((((..((....)).)))).....(((((....)))))...(((.....)))..(((((..(((.....)))..)))))...((((.(........)))))....(((......))).....((((.....))))....(((..(((....)))..))).........((((......))))((..((((....))))..))............(((((....))))).......((((..(((.......)))..)))).....((...(((((.....)))))..))...((((...(((....)))...))))..........((((..(((....))).))))........((((((.((....))..))))))...........(((.....))).((((((.......))))))..((((..........))))((((((.....)))))).........((((.........))))....(((((.....))))).((((((........))))))......(((.(((....))).)))..((((.......))))......................((..((((..(...)..))))..))....................(((..(((....)))..))).........................((((((((.(.....).)))))))).(((((((....))))))).....(((..((..(....)..))..).))...(((((((...........))))))).((....)).......(((((((.....)))))))((((..(((....)))..)))).......((((..((((....))))..))))..((....)).((((.....)))).(((((..((.......))..)))))...(..((((..........))))..)................(((...((.......))...)))((((.....))))..((((......))))....(((((((((......)))))).))).......(((..(((((.....)))))..)))...........(((((((....))).)))).(..(((((.....)))))..)......(((.(((((.....))))))))................((((((.......)))))).(((((((((....))))))..))).....((.....))...........(((((...........)))))............((((.....))))...(((((.....))))).......(((((((.......)))))))............((...((((((....))))))..))....((((........)))).((((.....))))",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##

    @unittest.expectedFailure
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    @unittest.skipUnless(*UnitTestDecorArgs(NOT_PASSING, invertBoolean=True))
    def test__MFE_CustomParams_test02_unafold(self):
        ### $ export GTFOLDDATADIR=$(greadlink -f Testing/ExtraGTFoldThermoData/DefaultUNAFold)
        ### $ ./bin/gtmfe -v -d 0 -l 10 --prefilter 2 --unafold d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 0, 
            'tmismatch'  : False,
            'limitcdist' : 10,
            'prefilter'  : 2,
        }
        extraConfigParamsDict = {
            'rnafold'    : 0, 
            'unafold'    : 1,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -238.8000, 
            'mfe-struct' : "......((......))............(((....)))............................(((.....))).............................((......))....(((....))).....................................................(((.....)))..................................................((.....)).....(((.....)))..................................(((....)))............(((....)))...............(((.....))).((((...))))...(((.....)))...................((....))..............................................((....))................(((.....)))..................................((.......)).(((....)))..........................((((...))))...............((....)).....((....))...((....))....................................(((.....))).......(((...))).........................(((....)))....(((....))).............................(((.....)))....................((......))...........(((.....)))............................(((....)))..((((...))))...............(((.....))).............................(((.....)))...(((.....))).....((.......)).......((......))................................(((....))).................(((....)))..................((......))......((((...))))...................((......))..........((((...))))..(((....)))...........(((.....))).....(((....)))...(((....)))....................((....))................................(((.....)))..((((...))))........................((....))...............(((....)))...........................((.......))...........................(((.....))).......(((.....)))......((......)).((....)).....................((....))............(((....))).....(((.....))).(((....))).....((......))............................((......))............................(((....)))....................(((....)))...(((....)))...................(((....)))..........(((....)))..........(((....))).....................((.....))...(((....))).........((((...))))........(((....)))...............((....))...................(((.....)))...........................................(((.....))).......(((.....)))......(((...)))..(((.....))).................................(((....)))........((.......))..........................................................................(((....))).....((......)).........................................(((.....))).....((((...)))).................(((.....)))......................((....)).......(((.....)))....................(((....))).((......))..........((....))...(((....))).............(((.....)))..(((.....))).................((....))..........((......))........................(((.....))).(((....)))............................((....))...(((.....)))................................(((....)))................(((...)))...............(((.....)))..............................(((.....))).......((((...))))..........((.....))............(((.....))).............(((.....)))...............(((.....)))(((....))).((((...))))....................(((....)))......((.....)).................((....)).........",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##

    @unittest.expectedFailure
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    @unittest.skipUnless(*UnitTestDecorArgs(NOT_PASSING, invertBoolean=True))
    def test__MFE_CustomParams_test01(self):
        ### $ ./bin/gtmfe -v -d 0 -l 24 --prefilter 2 d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 0, 
            'tmismatch'  : False,
            'limitcdist' : 24,
            'prefilter'  : 2,
        }
        extraConfigParamsDict = {
            'rnafold'    : 0, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -731.7000, 
            'mfe-struct' : ".((...((......))..))........(((((((.....))).))))......(((((((......)).....))))).(((((((.......))).))))...(((......)))..((((....))))((((((....))))))...((((((((.........)))))))).((....))..(((.(((..........))).)))...........((((......)))).((((.((.((.....))..))))))..(((........)))..(((.((.......)).)))..((((((....))))))....(((.((((....)))).)))((((.....((....)))))).((((...)))).((((((((.((...)).)))))))).....(((((((....)))))))........((((..((......))..))))..((....((....))....)).........((((.....)))).............(((......(((....)))..))).((..((((((....))))))..))..((((.....)))).(((((((...)))))))............((((..((.....))..))))...((....))..((((.....)))).....(((...((((....))))..))).....(((((.(((...))))))))...((((((......))))))...........(((.(((((........))))))))........(((((..........)))))......(.((((((........)))))).)...(((((....))))).(((((.((.......)))))))...............((.(((.(((....)))..))).)).......(((.....)))....(((((........)).))).......((((((((........)))))))).....(((......))).((((.........))))(((......)))....((.(....).)).((((....))))..........(((.(((((.......))))).)))....((..(((......)))..))(((((...))))).((((....).)))..(((.((........)).))).........(((((((((....))))))))).(((((...((.....))...)))))...((((((((....))))))))....((((.....))))...((((......)))).......(((((((.....)))))))....((((..(....).)))).((((..((.....)))))).((((......))))....(((.(.(((....))).).)))........(((((........)))))......((((.((.(....).))))))..............((((((((((...))).)))))))..........(.((((....)))).)...........((((..((....)).)))).....(((((....)))))...(((.....)))..(((((..(((.....)))..)))))...((((.(........)))))....(((......))).....((((.....))))....((((((((....))))))))..................(((((....(....).....)))))............(((((....))))).......((((..(((.......)))..)))).....((...(((((.....)))))..))...((((...(((....)))...))))..........((((..(((....))).))))........((((((.((....))..))))))...........(((.....))).((((((.......))))))..((((..........))))((((((.....))))))......(..((((.........))))..).(((((.....))))).((((((........))))))......(((.(((....))).)))..((((.......))))......................(((.((((..(...)..)))).)))....................(((..(((....)))..))).........................((((((((.(.....).)))))))).(((((((....)))))))......((..((.((....)).))..)).....(((((((...........))))))).((....)).......(((((((.....)))))))((((.((((....)))).)))).......((((..((((....))))..))))..((....)).((((.....)))).(((((((((.......)))))))))...(..((((..........))))..)................(((...((.......))...)))((((.....))))..((((......))))....(((((((((......)))))).))).......(((..(((((.....)))))..)))...........(((((((....))).)))).((.(((((.....))))).))...((..((....))..))(((((..((.(....).)).)))))((((((.......)))))).(((((((((....))))))..))).....((.....))...........(((((...........)))))............((((.....))))...(((((.....))))).......(((((((.......)))))))............((...((((((....))))))..))....((((.(....).)))).((((.....))))",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.expectedFailure
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    @unittest.skipUnless(*UnitTestDecorArgs(NOT_PASSING, invertBoolean=True))
    def test__MFE_CustomParams_test02(self):
        ### $ ./bin/gtmfe -v -d 1 -l 24 --prefilter 2 d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 1, 
            'tmismatch'  : False,
            'limitcdist' : 24,
            'prefilter'  : 2,
        }
        extraConfigParamsDict = {
            'rnafold'    : 0, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -723.8000, 
            'mfe-struct' : ".((...((......))..))........(((((((.....))).))))......(((((((......)).....))))).(((((((.......))).))))...(((......)))..((((....))))((((((....))))))...((((((((.........)))))))).((....))..(((.(((..........))).)))...........((((......)))).((((.((.((.....))..))))))..(((........)))..(((.((.......)).)))..((((((....))))))....(((.((((....)))).)))((((.....((....)))))).((((...)))).((((((((.((...)).)))))))).....(((((((....)))))))........((((..((......))..))))..((....((....))....)).........((((.....)))).............(((......(((....)))..))).((..((((((....))))))..))..((((.....)))).(((((((...)))))))............((((..((.....))..))))...((....))..((((.....)))).....(((...((((....))))..))).....(((((.(((...))))))))...((((((......))))))...........(((.(((((........))))))))........(((((..........)))))........((((((........)))))).....(((((....))))).(((((.((.......)))))))...............((.(((.(((....)))..))).)).......(((.....)))....(((((........)).))).......((((((((........)))))))).....(((......))).((((.........)))).......(((.(((........))).)))((((....))))...((((((....))))))........((..((.......))..))......((.((..(((((...))))))).))...........(((.((........)).))).........(((((((((....))))))))).(((((...((.....))...)))))...((((((((....))))))))....((((.....))))...((((......)))).......(((((((.....))))))).(((((....))...))).(((((((..((.....))))))))).....(((.((.....))))).(((....)))..............(((((........))))).(((.((......)).)))....((((.((....)).)))).(((((((((...))).))))))...(((......)))...(((((.((.....)))))))((((..((....)).)))).....(((((....)))))...(((.....)))..(((((..(((.....)))..)))))...((((.(........)))))....(((......))).....((((.....))))....((((((((....)))))))).........((((......))))((..((((....))))..))............(((((....))))).......((((..(((.......)))..)))).....((...(((((.....)))))..))...((((...(((....)))...))))..........((((..(((....))).))))........((((((.((....))..))))))...........(((.....))).((((((.......))))))..((((..........))))((((((.....)))))).........((((.........))))....(((((.....))))).((((((........))))))......(((.(((....))).)))..((((.......))))......................(((.((((..(...)..)))).)))....................(((..(((....)))..))).........................((((((((.(.....).)))))))).(((((((....)))))))......((..((.((....)).))..)).....(((((((...........))))))).((....)).......(((((((.....)))))))((((.((((....)))).)))).......((((..((((....))))..))))..((....)).((((.....)))).(((((((((.......)))))))))...(..((((..........))))..)................(((...((.......))...)))((((.....))))..((((......))))....(((((((((......)))))).))).......(((..(((((.....)))))..)))...........(((((((....))).)))).((.(((((.....))))).))......(((.(((((.....))))))))................((((((.......)))))).(((((((((....))))))..))).....((.....))...........(((((...........)))))............((((.....))))...(((((.....))))).......(((((((.......)))))))............((...((((((....))))))..))....((((........)))).((((.....))))",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test03(self):
        ### $ ./bin/gtmfe -v -d 1 -dS -l 24 --prefilter 2 d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 1, 
            'tmismatch'  : False,
            'limitcdist' : 24,
            'prefilter'  : 2,
        }
        extraConfigParamsDict = {
            'rnafold'    : 0, 
            'unafold'    : 0,
            'dS'         : 1,
        }
        expectedResults = {
            'mfe'        : -723.8000, 
            'mfe-struct' : ".((...((......))..))........(((((((.....))).))))......(((((((......)).....))))).(((((((.......))).))))...(((......)))..((((....))))((((((....))))))...((((((((.........)))))))).((....))..(((.(((..........))).)))...........((((......)))).((((.((.((.....))..))))))..(((........)))..(((.((.......)).)))..((((((....))))))....(((.((((....)))).)))((((.....((....)))))).((((...)))).((((((((.((...)).)))))))).....(((((((....)))))))........((((..((......))..))))..((....((....))....)).........((((.....)))).............(((......(((....)))..))).((..((((((....))))))..))..((((.....)))).(((((((...)))))))............((((..((.....))..))))...((....))..((((.....)))).....(((...((((....))))..))).....(((((.(((...))))))))...((((((......))))))...........(((.(((((........))))))))........(((((..........)))))........((((((........)))))).....(((((....))))).(((((.((.......)))))))...............((.(((.(((....)))..))).)).......(((.....)))....(((((........)).))).......((((((((........)))))))).....(((......))).((((.........)))).......(((.(((........))).)))((((....))))...((((((....))))))........((..((.......))..))......((.((..(((((...))))))).))...........(((.((........)).))).........(((((((((....))))))))).(((((...((.....))...)))))...((((((((....))))))))....((((.....))))...((((......)))).......(((((((.....))))))).(((((....))...))).(((((((..((.....))))))))).....(((.((.....))))).(((....)))..............(((((........))))).(((.((......)).)))....((((.((....)).)))).(((((((((...))).))))))...(((......)))...(((((.((.....)))))))((((..((....)).)))).....(((((....)))))...(((.....)))..(((((..(((.....)))..)))))...((((.(........)))))....(((......))).....((((.....))))....((((((((....)))))))).........((((......))))((..((((....))))..))............(((((....))))).......((((..(((.......)))..)))).....((...(((((.....)))))..))...((((...(((....)))...))))..........((((..(((....))).))))........((((((.((....))..))))))...........(((.....))).((((((.......))))))..((((..........))))((((((.....)))))).........((((.........))))....(((((.....))))).((((((........))))))......(((.(((....))).)))..((((.......))))......................(((.((((..(...)..)))).)))....................(((..(((....)))..))).........................((((((((.(.....).)))))))).(((((((....)))))))......((..((.((....)).))..)).....(((((((...........))))))).((....)).......(((((((.....)))))))((((.((((....)))).)))).......((((..((((....))))..))))..((....)).((((.....)))).(((((((((.......)))))))))...(..((((..........))))..)................(((...((.......))...)))((((.....))))..((((......))))....(((((((((......)))))).))).......(((..(((((.....)))))..)))...........(((((((....))).)))).((.(((((.....))))).))......(((.(((((.....))))))))................((((((.......)))))).(((((((((....))))))..))).....((.....))...........(((((...........)))))............((((.....))))...(((((.....))))).......(((((((.......)))))))............((...((((((....))))))..))....((((........)))).((((.....))))",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test04(self):
        ### $ ./bin/gtmfe -v -d 2 -l 24 --prefilter 2 d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 2, 
            'tmismatch'  : False,
            'limitcdist' : 24,
            'prefilter'  : 2,
        }
        extraConfigParamsDict = {
            'rnafold'    : 0, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -746.2000, 
            'mfe-struct' : ".((...((......))..))........(((((((.....))).))))......(((((((......)).....))))).(((((((.......))).))))...(((......)))...(((....)))(((((((....)))))))..((((((((.........)))))))).((....))..(((.(((..........))).)))...........((((......)))).((((.((.((.....))..))))))..(((........)))..(((.((.......)).)))..((((((....))))))....(((.((((....)))).)))((((.....((....)))))).((((...)))).((((((((.((...)).)))))))).....(((((((....)))))))........((((..((......))..))))..((....((....))....)).........((((.....)))).............(((......(((....)))..))).((..((((((....))))))..))..((((.....)))).(((((((...)))))))............((((..((.....))..))))...((....))..((((.....)))).....(((...((((....))))..))).....(((((.(((...))))))))...((((((......))))))((....))...(((.(((((........))))))))........(((((..........)))))........((((((........)))))).....(((((....))))).(((((.((.......)))))))...............((.(((.(((....)))..))).)).......(((.....)))....(((((........)).))).......((((((((........)))))))).....(((......))).((((.........)))).......(((.(((........))).)))((((....))))..........(((.(((((.......))))).)))....((..(((......)))..))(((((...)))))................(((.((........)).))).........(((((((((....))))))))).(((((...((.....))...)))))...((((((((....))))))))....((((.....))))...((((......)))).......(((((((.....)))))))....(((..(((...))))))(((((..((.....)))))))((((......))))....(((...(((....)))...)))........(((((........))))).(((.((......)).))).............((((.....))))((((((...))))))(((((((......)))))))..(((((.((.....)))))))((((..((....)).)))).....(((((....)))))...(((.....)))..(((((..(((.....)))..)))))...((((.(........)))))((..(((......)))))...((((.....))))....((((((((....)))))))).........((((......))))((..((((....))))..))............(((((....))))).......((((..(((.......)))..)))).....((...(((((.....)))))..))...((((...(((....)))...)))).(((.((.......)))))..(((....)))........((((((.((....))..))))))...........(((.....))).((((((.......))))))..((((..........))))((((((.....)))))).........((((.........))))....(((((.....))))).((((((........))))))......(((.(((....))).)))..((((.......))))......................(((.((((..(...)..)))).)))....................(((..(((....)))..)))((......))...............((((((((.(.....).)))))))).(((((((....)))))))......((..((.((....)).))..)).....(((((((...........))))))).((....)).......(((((((.....)))))))((((.((((....)))).)))).......((((..((((....))))..)))).(((....)))((((.....)))).(((((((((.......)))))))))...(..((((..........))))..)......((......))(((...((.......))...)))((((.....))))..((((......))))....(((((((((......)))))).))).......(((..(((((.....)))))..)))...........(((((((....))).))))(((.(((((.....))))).))).....(((.(((((.....))))))))...............(((((((.......)))))))(((((((((....))))))..))).....((.....))...........(((((...........)))))............((((.....))))((((((((.....)))))....)))(((((((.......)))))))............((...((((((....))))))..))....((((........)))).((((.....))))",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test05(self):
        ### $ ./bin/gtmfe -v -m -d 0 -l 24 --prefilter 2 d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 0, 
            'tmismatch'  : True,
            'limitcdist' : 24,
            'prefilter'  : 2,
        }
        extraConfigParamsDict = {
            'rnafold'    : 0, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -600.4000, 
            'mfe-struct' : ".((...((......))..))........(((((((.....))).))))......(((((((......)).....))))).(((((((.......))).))))...(((......)))...(((....)))(((((((....)))))))..((((((((.........))))))))...........(((.(((..........))).)))...........((((......)))).((((.((.((.....))..)))))).......((..(((((...))).)).))...........((((((....))))))....(((.((((....)))).)))((((.....((....)))))).((((...)))).((((((((.((...)).)))))))).....(((((((....)))))))........((((..((......))..))))..((....((....))....)).........((((.....)))).............(((......(((....)))..))).((..((((((....))))))..))................(((((((...)))))))............((((..((.....))..))))...((....))....((((((.....))))))..((.((((...........)))).))(((((.(((...))))))))...((((((......))))))...........(((.(((((........))))))))........(((((..........)))))........((((((........))))))(((..(((((....)))))...)))...........(((..(...........)..)))...((((....))))...............(((.....)))....(((((........)).))).......((((((((........)))))))).....(((......))).((((.........)))).......(((.(((........))).)))((((....))))..........(((.(((((.......))))).))).................((.((..(((((...))))))).))...........(((.((........)).))).........(((((((((....))))))))).(((((...((.....))...)))))...((((((((....))))))))....................((((......)))).......(((((((.....))))))).(((((....))...))).(((((((..((.....)))))))))................(((...(((....)))...)))........(((((........))))).(((.((......)).)))....((((.((....)).))))((((((((((...))).)))))))..(((......)))...(((((.((.....)))))))((((..((....)).)))).....(((((....)))))...(((.....)))..(((((..(((.....)))..)))))...((((.(........)))))((..(((......)))))...((((.....))))....((((((((....)))))))).........((((......))))((..((((....))))..))........((..(((((....)))))..))...((((..(((.......)))..)))).....((...(((((.....)))))..))...((((...(((....)))...))))..........((((..(((....))).))))........((((((.((....))..))))))...........(((.....))).((((((.......))))))..((((..........))))((((((.....)))))).........((((.........))))....(((((.....))))).((((((........))))))......(((.(((....))).)))..((((.......))))......................(((.((((..(...)..)))).)))....................(((..(((....)))..))).........................((((((((.(.....).)))))))).(((((((....)))))))......((..((.((....)).))..)).....(((((((...........))))))).((....)).......(((((((.....)))))))((((.((((....)))).)))).......((((..((((....))))..)))).(((....)))((((.....)))).(((((((((.......)))))))))...(..((((..........))))..)................(((...((.......))...)))((((.....))))..((((......))))....(((((((((......)))))).)))..(((((.....)))))..........................(((((((....))).))))(((.(((((.....))))).))).....(((.(((((.....))))))))...............(((((((.......)))))))(((((((((....))))))..))).........................(((((...........)))))............((((.....))))((((((((.....)))))....)))(((((((.......)))))))............((...((((((....))))))..))....((((........)))).((((.....))))",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test06(self):
        ### $ ./bin/gtmfe -v -m -d 1 -l 24 --prefilter 2 d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 1, 
            'tmismatch'  : True,
            'limitcdist' : 24,
            'prefilter'  : 2,
        }
        extraConfigParamsDict = {
            'rnafold'    : 0, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -723.8000, 
            'mfe-struct' : ".((...((......))..))........(((((((.....))).))))......(((((((......)).....))))).(((((((.......))).))))...(((......)))..((((....))))((((((....))))))...((((((((.........)))))))).((....))..(((.(((..........))).)))...........((((......)))).((((.((.((.....))..))))))..(((........)))..(((.((.......)).)))..((((((....))))))....(((.((((....)))).)))((((.....((....)))))).((((...)))).((((((((.((...)).)))))))).....(((((((....)))))))........((((..((......))..))))..((....((....))....)).........((((.....)))).............(((......(((....)))..))).((..((((((....))))))..))..((((.....)))).(((((((...)))))))............((((..((.....))..))))...((....))..((((.....)))).....(((...((((....))))..))).....(((((.(((...))))))))...((((((......))))))...........(((.(((((........))))))))........(((((..........)))))........((((((........)))))).....(((((....))))).(((((.((.......)))))))...............((.(((.(((....)))..))).)).......(((.....)))....(((((........)).))).......((((((((........)))))))).....(((......))).((((.........)))).......(((.(((........))).)))((((....))))...((((((....))))))........((..((.......))..))......((.((..(((((...))))))).))...........(((.((........)).))).........(((((((((....))))))))).(((((...((.....))...)))))...((((((((....))))))))....((((.....))))...((((......)))).......(((((((.....))))))).(((((....))...))).(((((((..((.....))))))))).....(((.((.....))))).(((....)))..............(((((........))))).(((.((......)).)))....((((.((....)).)))).(((((((((...))).))))))...(((......)))...(((((.((.....)))))))((((..((....)).)))).....(((((....)))))...(((.....)))..(((((..(((.....)))..)))))...((((.(........)))))....(((......))).....((((.....))))....((((((((....)))))))).........((((......))))((..((((....))))..))............(((((....))))).......((((..(((.......)))..)))).....((...(((((.....)))))..))...((((...(((....)))...))))..........((((..(((....))).))))........((((((.((....))..))))))...........(((.....))).((((((.......))))))..((((..........))))((((((.....)))))).........((((.........))))....(((((.....))))).((((((........))))))......(((.(((....))).)))..((((.......))))......................(((.((((..(...)..)))).)))....................(((..(((....)))..))).........................((((((((.(.....).)))))))).(((((((....)))))))......((..((.((....)).))..)).....(((((((...........))))))).((....)).......(((((((.....)))))))((((.((((....)))).)))).......((((..((((....))))..))))..((....)).((((.....)))).(((((((((.......)))))))))...(..((((..........))))..)................(((...((.......))...)))((((.....))))..((((......))))....(((((((((......)))))).))).......(((..(((((.....)))))..)))...........(((((((....))).)))).((.(((((.....))))).))......(((.(((((.....))))))))................((((((.......)))))).(((((((((....))))))..))).....((.....))...........(((((...........)))))............((((.....))))...(((((.....))))).......(((((((.......)))))))............((...((((((....))))))..))....((((........)))).((((.....))))",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test07(self):
        ### $ ./bin/gtmfe -v -m -d 1 -dS -l 24 --prefilter 2 d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 1, 
            'tmismatch'  : True,
            'limitcdist' : 24,
            'prefilter'  : 2,
        }
        extraConfigParamsDict = {
            'rnafold'    : 0, 
            'unafold'    : 0,
            'dS'         : 1,
        }
        expectedResults = {
            'mfe'        : -723.8000, 
            'mfe-struct' : ".((...((......))..))........(((((((.....))).))))......(((((((......)).....))))).(((((((.......))).))))...(((......)))..((((....))))((((((....))))))...((((((((.........)))))))).((....))..(((.(((..........))).)))...........((((......)))).((((.((.((.....))..))))))..(((........)))..(((.((.......)).)))..((((((....))))))....(((.((((....)))).)))((((.....((....)))))).((((...)))).((((((((.((...)).)))))))).....(((((((....)))))))........((((..((......))..))))..((....((....))....)).........((((.....)))).............(((......(((....)))..))).((..((((((....))))))..))..((((.....)))).(((((((...)))))))............((((..((.....))..))))...((....))..((((.....)))).....(((...((((....))))..))).....(((((.(((...))))))))...((((((......))))))...........(((.(((((........))))))))........(((((..........)))))........((((((........)))))).....(((((....))))).(((((.((.......)))))))...............((.(((.(((....)))..))).)).......(((.....)))....(((((........)).))).......((((((((........)))))))).....(((......))).((((.........)))).......(((.(((........))).)))((((....))))...((((((....))))))........((..((.......))..))......((.((..(((((...))))))).))...........(((.((........)).))).........(((((((((....))))))))).(((((...((.....))...)))))...((((((((....))))))))....((((.....))))...((((......)))).......(((((((.....))))))).(((((....))...))).(((((((..((.....))))))))).....(((.((.....))))).(((....)))..............(((((........))))).(((.((......)).)))....((((.((....)).)))).(((((((((...))).))))))...(((......)))...(((((.((.....)))))))((((..((....)).)))).....(((((....)))))...(((.....)))..(((((..(((.....)))..)))))...((((.(........)))))....(((......))).....((((.....))))....((((((((....)))))))).........((((......))))((..((((....))))..))............(((((....))))).......((((..(((.......)))..)))).....((...(((((.....)))))..))...((((...(((....)))...))))..........((((..(((....))).))))........((((((.((....))..))))))...........(((.....))).((((((.......))))))..((((..........))))((((((.....)))))).........((((.........))))....(((((.....))))).((((((........))))))......(((.(((....))).)))..((((.......))))......................(((.((((..(...)..)))).)))....................(((..(((....)))..))).........................((((((((.(.....).)))))))).(((((((....)))))))......((..((.((....)).))..)).....(((((((...........))))))).((....)).......(((((((.....)))))))((((.((((....)))).)))).......((((..((((....))))..))))..((....)).((((.....)))).(((((((((.......)))))))))...(..((((..........))))..)................(((...((.......))...)))((((.....))))..((((......))))....(((((((((......)))))).))).......(((..(((((.....)))))..)))...........(((((((....))).)))).((.(((((.....))))).))......(((.(((((.....))))))))................((((((.......)))))).(((((((((....))))))..))).....((.....))...........(((((...........)))))............((((.....))))...(((((.....))))).......(((((((.......)))))))............((...((((((....))))))..))....((((........)))).((((.....))))",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test08(self):
        ### $ ./bin/gtmfe -v -m -d 2 -l 24 --prefilter 2 d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 2, 
            'tmismatch'  : True,
            'limitcdist' : 24,
            'prefilter'  : 2,
        }
        extraConfigParamsDict = {
            'rnafold'    : 0, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -746.2000, 
            'mfe-struct' : ".((...((......))..))........(((((((.....))).))))......(((((((......)).....))))).(((((((.......))).))))...(((......)))...(((....)))(((((((....)))))))..((((((((.........)))))))).((....))..(((.(((..........))).)))...........((((......)))).((((.((.((.....))..))))))..(((........)))..(((.((.......)).)))..((((((....))))))....(((.((((....)))).)))((((.....((....)))))).((((...)))).((((((((.((...)).)))))))).....(((((((....)))))))........((((..((......))..))))..((....((....))....)).........((((.....)))).............(((......(((....)))..))).((..((((((....))))))..))..((((.....)))).(((((((...)))))))............((((..((.....))..))))...((....))..((((.....)))).....(((...((((....))))..))).....(((((.(((...))))))))...((((((......))))))((....))...(((.(((((........))))))))........(((((..........)))))........((((((........)))))).....(((((....))))).(((((.((.......)))))))...............((.(((.(((....)))..))).)).......(((.....)))....(((((........)).))).......((((((((........)))))))).....(((......))).((((.........)))).......(((.(((........))).)))((((....))))..........(((.(((((.......))))).)))....((..(((......)))..))(((((...)))))................(((.((........)).))).........(((((((((....))))))))).(((((...((.....))...)))))...((((((((....))))))))....((((.....))))...((((......)))).......(((((((.....)))))))....(((..(((...))))))(((((..((.....)))))))((((......))))....(((...(((....)))...)))........(((((........))))).(((.((......)).))).............((((.....))))((((((...))))))(((((((......)))))))..(((((.((.....)))))))((((..((....)).)))).....(((((....)))))...(((.....)))..(((((..(((.....)))..)))))...((((.(........)))))((..(((......)))))...((((.....))))....((((((((....)))))))).........((((......))))((..((((....))))..))............(((((....))))).......((((..(((.......)))..)))).....((...(((((.....)))))..))...((((...(((....)))...)))).(((.((.......)))))..(((....)))........((((((.((....))..))))))...........(((.....))).((((((.......))))))..((((..........))))((((((.....)))))).........((((.........))))....(((((.....))))).((((((........))))))......(((.(((....))).)))..((((.......))))......................(((.((((..(...)..)))).)))....................(((..(((....)))..)))((......))...............((((((((.(.....).)))))))).(((((((....)))))))......((..((.((....)).))..)).....(((((((...........))))))).((....)).......(((((((.....)))))))((((.((((....)))).)))).......((((..((((....))))..)))).(((....)))((((.....)))).(((((((((.......)))))))))...(..((((..........))))..)......((......))(((...((.......))...)))((((.....))))..((((......))))....(((((((((......)))))).))).......(((..(((((.....)))))..)))...........(((((((....))).))))(((.(((((.....))))).))).....(((.(((((.....))))))))...............(((((((.......)))))))(((((((((....))))))..))).....((.....))...........(((((...........)))))............((((.....))))((((((((.....)))))....)))(((((((.......)))))))............((...((((((....))))))..))....((((........)))).((((.....))))",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
  
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test09(self):
        ### $ ./bin/gtmfe -v -d 0 -l 10 --prefilter 2 d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 0, 
            'tmismatch'  : False,
            'limitcdist' : 10,
            'prefilter'  : 2,
        }
        extraConfigParamsDict = {
            'rnafold'    : 0, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -129.0000, 
            'mfe-struct' : "......((......))............(((....)))............................(((.....)))...........................................(((....))).....................................................(((.....)))..................................................((.....)).....(((.....)))..................................(((....)))............(((....)))...............(((.....))).((((...))))...(((.....)))...................((....))..............................................((....))................(((.....)))..............................................(((....)))..........................((((...))))............................((....))...((....))....................................(((.....))).......(((...)))..............................................................................(((.....))).........................................(((.....)))........................................((((...))))...............(((.....)))................................(((....))).(((.....))).................................................................(((....))).................(((....)))..................((......))......((((...))))...................((......))..........((((...))))..(((....)))...........(((.....))).....(((....)))...(((....)))..................................................(((.....)))............((((...))))...............................................(((....)))...........................................................................(((.....)))........................(((....)))........................................(((....))).....(((.....))).........(((.....)))..................................((......))............................(((....))).................................(((....)))...................(((....)))..........(((....)))..........(((....))).................................(((....))).........((((...))))........(((....)))...............((....))...................(((.....)))...........................................(((.....)))......................................................................................................................................................................................(((....)))........................................................(((.....))).....((((...)))).................(((.....)))......................((....)).......(((.....)))....................(((....))).((......))..........((....))...(((....)))..........................(((.....))).....................................................................(((.....))).......................................((....))...(((.....)))................................(((....)))...............((((...))))..............(((.....)))................................................((((...))))...............................(((.....))).......................................(((.....)))(((....)))........................................(((....)))........................((....)).........",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test10(self):
        ### $ ./bin/gtmfe -v -d 1 -l 10 --prefilter 2 d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 1, 
            'tmismatch'  : False,
            'limitcdist' : 10,
            'prefilter'  : 2,
        }
        extraConfigParamsDict = {
            'rnafold'    : 0, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -249.5000, 
            'mfe-struct' : "......((......))............(((....))).............................((.....))..............................((......))....(((....))).....................................................(((.....))).............((....)).............................((.....)).....(((.....)))..................................(((....)))............(((....)))...............(((.....))).((((...))))...(((.....)))...................((....))..............................................((....))................(((.....)))......................(((....)))..((.......)).(((....)))..........................((((...))))...............((....)).....((....))...((....))............(((.....))).............(((.....))).......(((...))).........................(((....)))....(((....))).............................(((.....)))....................((......))...........(((.....)))..........(((....)))........(((....)))..((((...))))...............(((.....))).............................(((.....)))...(((.....))).....((.......)).......((......))................................(((....))).................(((....)))..................((......))......((((...))))...................((......))..........((((...))))..(((....)))...........(((.....))).....(((....)))...(((....)))....................((....))............((......))..........(((.....)))..((((...)))).........((.....))......((....))...............(((....)))...........................((.......))...........................(((.....))).......(((.....)))......((......)).((....)).....................((....))............(((....))).....(((.....))).(((....))).....((......))............................((......))............................(((....)))....................(((....)))...(((....)))...................(((....)))..........(((....)))............((.....))....................((.....))...(((....))).........((((...))))........(((....)))...............((....))...................(((.....)))...........................................(((.....))).......(((.....)))......(((...)))..(((.....))).................................(((....)))........((.......))..........................................................................(((....))).....((......)).........................................(((.....))).....((((...)))).................(((.....)))......................((....)).......(((.....)))....................(((....))).((......))..........((....))...(((....))).............(((.....)))..(((.....))).................((....))..........((......))........................(((.....))).(((....)))............................((....))...(((.....))).......(((...)))................(((....)))................(((...)))...............(((.....))).............((.....))........(((.....))).......((((...))))..........((.....))............(((.....))).............(((.....)))...............(((.....)))(((....)))..........((((...))))...........(((....)))......((.....)).................((....)).........",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test11(self):
        ### $ ./bin/gtmfe -v -d 1 -dS -l 10 --prefilter 2 d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 1, 
            'tmismatch'  : False,
            'limitcdist' : 10,
            'prefilter'  : 2,
        }
        extraConfigParamsDict = {
            'rnafold'    : 0, 
            'unafold'    : 0,
            'dS'         : 1,
        }
        expectedResults = {
            'mfe'        : -249.5000, 
            'mfe-struct' : "......((......))............(((....))).............................((.....))..............................((......))....(((....))).....................................................(((.....))).............((....)).............................((.....)).....(((.....)))..................................(((....)))............(((....)))...............(((.....))).((((...))))...(((.....)))...................((....))..............................................((....))................(((.....)))......................(((....)))..((.......)).(((....)))..........................((((...))))...............((....)).....((....))...((....))............(((.....))).............(((.....))).......(((...))).........................(((....)))....(((....))).............................(((.....)))....................((......))...........(((.....)))..........(((....)))........(((....)))..((((...))))...............(((.....))).............................(((.....)))...(((.....))).....((.......)).......((......))................................(((....))).................(((....)))..................((......))......((((...))))...................((......))..........((((...))))..(((....)))...........(((.....))).....(((....)))...(((....)))....................((....))............((......))..........(((.....)))..((((...)))).........((.....))......((....))...............(((....)))...........................((.......))...........................(((.....))).......(((.....)))......((......)).((....)).....................((....))............(((....))).....(((.....))).(((....))).....((......))............................((......))............................(((....)))....................(((....)))...(((....)))...................(((....)))..........(((....)))............((.....))....................((.....))...(((....))).........((((...))))........(((....)))...............((....))...................(((.....)))...........................................(((.....))).......(((.....)))......(((...)))..(((.....))).................................(((....)))........((.......))..........................................................................(((....))).....((......)).........................................(((.....))).....((((...)))).................(((.....)))......................((....)).......(((.....)))....................(((....))).((......))..........((....))...(((....))).............(((.....)))..(((.....))).................((....))..........((......))........................(((.....))).(((....)))............................((....))...(((.....))).......(((...)))................(((....)))................(((...)))...............(((.....))).............((.....))........(((.....))).......((((...))))..........((.....))............(((.....))).............(((.....)))...............(((.....)))(((....)))..........((((...))))...........(((....)))......((.....)).................((....)).........",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test12(self):
        ### $ ./bin/gtmfe -v -d 2 -l 10 --prefilter 2 d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 2, 
            'tmismatch'  : False,
            'limitcdist' : 10,
            'prefilter'  : 2,
        }
        extraConfigParamsDict = {
            'rnafold'    : 0, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -255.9000, 
            'mfe-struct' : "......((......))............(((....)))((.....))............((......))(((....)))...........................((......))....(((....))).....................................................(((.....))).............((....)).............................((.....)).....(((.....)))..................................(((....)))............(((....)))...............(((.....))).((((...))))...(((.....)))...................((....))..............................................((....))................(((.....)))......................(((....))).....(((....)))((....))...........................((((...))))...............((....)).....((....))...((....))............(((.....))).............(((.....))).......(((...))).............................((......))(((....))).............................(((.....)))....................((......))...........(((.....)))..........(((....)))........(((....)))..((((...))))...............(((.....)))................................(((....))).(((.....))).....((.......)).......((......))................................(((....))).................(((....)))..................((......))......((((...))))...................((......))..........((((...))))..(((....)))...........(((.....))).....(((....)))...(((....))).(((.....)))........((....))............((......))(((.....)))........((....))...((.......))..((.....))......((....))...............(((....)))...........................((.......))...........................(((.....))).......(((.....)))......((......))(((....)))((.....))...........((....))............(((....))).....(((.....))).(((....))).....((......))............................((......))............................(((....)))....................(((....)))...(((....)))...................(((....)))..........(((....)))............((.....))....................((.....))...(((....))).........((((...))))........(((....)))...............((....))...................(((.....)))...........................................(((.....))).......(((.....)))......(((...)))..(((.....))).................................(((....)))........((.......))..........................................................................(((....))).....((......)).........................................(((.....))).....((((...)))).................(((.....)))......................((....)).......(((.....)))....................(((....))).((......))..........((....))...(((....))).(((.....))).(((.....)))..(((.....)))(((.....)))......((....))..........((......))........................(((.....))).(((....)))............................((....))...(((.....))).......(((...)))................(((....)))................(((...)))...............(((.....))).............((.....))........(((.....))).......((((...))))..........((.....))............(((.....))).............(((.....)))...............(((.....)))(((....))).((((...))))....................(((....)))......((.....)).................((....)).........",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test13(self):
        ### $ ./bin/gtmfe -v -m -d 1 -dS -l 10 --prefilter 2 d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 0, 
            'tmismatch'  : True,
            'limitcdist' : 10,
            'prefilter'  : 2,
        }
        extraConfigParamsDict = {
            'rnafold'    : 0, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -129.0000, 
            'mfe-struct' : "......((......))............(((....)))............................(((.....)))...........................................(((....))).....................................................(((.....)))..................................................((.....)).....(((.....)))..................................(((....)))............(((....)))...............(((.....))).((((...))))...(((.....)))...................((....))..............................................((....))................(((.....)))..............................................(((....)))..........................((((...))))............................((....))...((....))....................................(((.....))).......(((...)))..............................................................................(((.....))).........................................(((.....)))........................................((((...))))...............(((.....)))................................(((....))).(((.....))).................................................................(((....))).................(((....)))..................((......))......((((...))))...................((......))..........((((...))))..(((....)))...........(((.....))).....(((....)))...(((....)))..................................................(((.....)))............((((...))))...............................................(((....)))...........................................................................(((.....)))........................(((....)))........................................(((....))).....(((.....))).........(((.....)))..................................((......))............................(((....))).................................(((....)))...................(((....)))..........(((....)))..........(((....))).................................(((....))).........((((...))))........(((....)))...............((....))...................(((.....)))...........................................(((.....)))......................................................................................................................................................................................(((....)))........................................................(((.....))).....((((...)))).................(((.....)))......................((....)).......(((.....)))....................(((....))).((......))..........((....))...(((....)))..........................(((.....))).....................................................................(((.....))).......................................((....))...(((.....)))................................(((....)))...............((((...))))..............(((.....)))................................................((((...))))...............................(((.....))).......................................(((.....)))(((....)))........................................(((....)))........................((....)).........",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test14(self):
        ### $ ./bin/gtmfe -v -m -d 1 -l 10 --prefilter 2 d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 1, 
            'tmismatch'  : True,
            'limitcdist' : 10,
            'prefilter'  : 2,
        }
        extraConfigParamsDict = {
            'rnafold'    : 0, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -249.5000, 
            'mfe-struct' : "......((......))............(((....))).............................((.....))..............................((......))....(((....))).....................................................(((.....))).............((....)).............................((.....)).....(((.....)))..................................(((....)))............(((....)))...............(((.....))).((((...))))...(((.....)))...................((....))..............................................((....))................(((.....)))......................(((....)))..((.......)).(((....)))..........................((((...))))...............((....)).....((....))...((....))............(((.....))).............(((.....))).......(((...))).........................(((....)))....(((....))).............................(((.....)))....................((......))...........(((.....)))..........(((....)))........(((....)))..((((...))))...............(((.....))).............................(((.....)))...(((.....))).....((.......)).......((......))................................(((....))).................(((....)))..................((......))......((((...))))...................((......))..........((((...))))..(((....)))...........(((.....))).....(((....)))...(((....)))....................((....))............((......))..........(((.....)))..((((...)))).........((.....))......((....))...............(((....)))...........................((.......))...........................(((.....))).......(((.....)))......((......)).((....)).....................((....))............(((....))).....(((.....))).(((....))).....((......))............................((......))............................(((....)))....................(((....)))...(((....)))...................(((....)))..........(((....)))............((.....))....................((.....))...(((....))).........((((...))))........(((....)))...............((....))...................(((.....)))...........................................(((.....))).......(((.....)))......(((...)))..(((.....))).................................(((....)))........((.......))..........................................................................(((....))).....((......)).........................................(((.....))).....((((...)))).................(((.....)))......................((....)).......(((.....)))....................(((....))).((......))..........((....))...(((....))).............(((.....)))..(((.....))).................((....))..........((......))........................(((.....))).(((....)))............................((....))...(((.....))).......(((...)))................(((....)))................(((...)))...............(((.....))).............((.....))........(((.....))).......((((...))))..........((.....))............(((.....))).............(((.....)))...............(((.....)))(((....)))..........((((...))))...........(((....)))......((.....)).................((....)).........",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test15(self):
        ### $ ./bin/gtmfe -v -m -d 1 -dS -l 10 --prefilter 2 d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 1, 
            'tmismatch'  : True,
            'limitcdist' : 10,
            'prefilter'  : 2,
        }
        extraConfigParamsDict = {
            'rnafold'    : 0, 
            'unafold'    : 0,
            'dS'         : 1,
        }
        expectedResults = {
            'mfe'        : -249.5000, 
            'mfe-struct' : "......((......))............(((....))).............................((.....))..............................((......))....(((....))).....................................................(((.....))).............((....)).............................((.....)).....(((.....)))..................................(((....)))............(((....)))...............(((.....))).((((...))))...(((.....)))...................((....))..............................................((....))................(((.....)))......................(((....)))..((.......)).(((....)))..........................((((...))))...............((....)).....((....))...((....))............(((.....))).............(((.....))).......(((...))).........................(((....)))....(((....))).............................(((.....)))....................((......))...........(((.....)))..........(((....)))........(((....)))..((((...))))...............(((.....))).............................(((.....)))...(((.....))).....((.......)).......((......))................................(((....))).................(((....)))..................((......))......((((...))))...................((......))..........((((...))))..(((....)))...........(((.....))).....(((....)))...(((....)))....................((....))............((......))..........(((.....)))..((((...)))).........((.....))......((....))...............(((....)))...........................((.......))...........................(((.....))).......(((.....)))......((......)).((....)).....................((....))............(((....))).....(((.....))).(((....))).....((......))............................((......))............................(((....)))....................(((....)))...(((....)))...................(((....)))..........(((....)))............((.....))....................((.....))...(((....))).........((((...))))........(((....)))...............((....))...................(((.....)))...........................................(((.....))).......(((.....)))......(((...)))..(((.....))).................................(((....)))........((.......))..........................................................................(((....))).....((......)).........................................(((.....))).....((((...)))).................(((.....)))......................((....)).......(((.....)))....................(((....))).((......))..........((....))...(((....))).............(((.....)))..(((.....))).................((....))..........((......))........................(((.....))).(((....)))............................((....))...(((.....))).......(((...)))................(((....)))................(((...)))...............(((.....))).............((.....))........(((.....))).......((((...))))..........((.....))............(((.....))).............(((.....)))...............(((.....)))(((....)))..........((((...))))...........(((....)))......((.....)).................((....)).........",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test16(self):
        ### $ ./bin/gtmfe -v -m -d 2 -l 10 --prefilter 2 d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 2, 
            'tmismatch'  : True,
            'limitcdist' : 10,
            'prefilter'  : 2,
        }
        extraConfigParamsDict = {
            'rnafold'    : 0, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -255.9000, 
            'mfe-struct' : "......((......))............(((....)))((.....))............((......))(((....)))...........................((......))....(((....))).....................................................(((.....))).............((....)).............................((.....)).....(((.....)))..................................(((....)))............(((....)))...............(((.....))).((((...))))...(((.....)))...................((....))..............................................((....))................(((.....)))......................(((....))).....(((....)))((....))...........................((((...))))...............((....)).....((....))...((....))............(((.....))).............(((.....))).......(((...))).............................((......))(((....))).............................(((.....)))....................((......))...........(((.....)))..........(((....)))........(((....)))..((((...))))...............(((.....)))................................(((....))).(((.....))).....((.......)).......((......))................................(((....))).................(((....)))..................((......))......((((...))))...................((......))..........((((...))))..(((....)))...........(((.....))).....(((....)))...(((....))).(((.....)))........((....))............((......))(((.....)))........((....))...((.......))..((.....))......((....))...............(((....)))...........................((.......))...........................(((.....))).......(((.....)))......((......))(((....)))((.....))...........((....))............(((....))).....(((.....))).(((....))).....((......))............................((......))............................(((....)))....................(((....)))...(((....)))...................(((....)))..........(((....)))............((.....))....................((.....))...(((....))).........((((...))))........(((....)))...............((....))...................(((.....)))...........................................(((.....))).......(((.....)))......(((...)))..(((.....))).................................(((....)))........((.......))..........................................................................(((....))).....((......)).........................................(((.....))).....((((...)))).................(((.....)))......................((....)).......(((.....)))....................(((....))).((......))..........((....))...(((....))).(((.....))).(((.....)))..(((.....)))(((.....)))......((....))..........((......))........................(((.....))).(((....)))............................((....))...(((.....))).......(((...)))................(((....)))................(((...)))...............(((.....))).............((.....))........(((.....))).......((((...))))..........((.....))............(((.....))).............(((.....)))...............(((.....)))(((....))).((((...))))....................(((....)))......((.....)).................((....)).........",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test17(self):
        ### $ ./bin/gtmfe -v -d 0 -l 24 --prefilter 6 d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 0, 
            'tmismatch'  : False,
            'limitcdist' : 24,
            'prefilter'  : 6,
        }
        extraConfigParamsDict = {
            'rnafold'    : 0, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -303.9000, 
            'mfe-struct' : "..................................................................................................................................(((((((....)))))))..((((((((.........)))))))).............................................................(((..................)))........................................((((((....))))))..........................................................((((((((.........)))))))).....(((((((....)))))))....................................................................................................................((((((....))))))....................(((((((...)))))))................................................((((((.....))))))..................................................((((((......))))))...................((((((....)))))).....................................((((((........))))))....................................(((..(...........)..))).......................................................................((((((((........))))))))...............................................................................((((((....))))))..................................................................................................(((((((((....)))))))))..(((((.....)))))............((((((((....)))))))).........................................(((((((.....)))))))...................(((((((...........))))))).......................................(((((((...........))))))).........................................((((((((((...))).)))))))...............(((((((..........)))))))....................................((((((..........))))))...............................................................................((((((((....))))))))....................................................................................((((((...........))))))...................................................(((..(............)..)))..............((((((...........)))))).......................((((((.......))))))....................((((((.....))))))..................((((((...))))))............................((((((......))))))..........................................(((..(.........)..)))................................(((..(((....)))..))).........................((((((((.........)))))))).(((((((....)))))))......((..((..........))..)).....(((((((...........)))))))................(((((((.....)))))))..............................................................................(((((((((.......))))))))).......................................................((((((....))))))((((((......))))))............(((((((......)))))))...............(((((.....)))))............................................................................(((((...............)))))((((((.......)))))).(((((((((....))))))..)))................................................(((((..........)))))......(((((.....))))).......(((((((.......))))))).................((((((....))))))......................................",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test18(self):
        ### $ ./bin/gtmfe -v -d 1 -l 24 --prefilter 6 d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 1, 
            'tmismatch'  : False,
            'limitcdist' : 24,
            'prefilter'  : 6,
        }
        extraConfigParamsDict = {
            'rnafold'    : 0, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -356.2000, 
            'mfe-struct' : "..................................................................................................................................(((((((....)))))))..((((((((.........)))))))).............................................................(((..................)))........................................((((((....))))))..........................................................((((((((.........)))))))).....(((((((....)))))))....................................................................................................................((((((....))))))....................(((((((...)))))))..(((((...............))))).....................((((((.....))))))...........................(((((..........)))))...((((((......))))))...................((((((....)))))).....................................((((((........))))))....................................(((..(...........)..))).......................................................................((((((((........))))))))...............................................................................((((((....))))))..................................................................................................(((((((((....)))))))))..(((((.....)))))............((((((((....)))))))).........................................(((((((.....)))))))...................(((((((...........))))))).......................................(((((((...........))))))).........................................(((((.....)))))...((((((((......))))))))((((((..........)))))).....................................((((((..........))))))...............................................................................((((((((....))))))))....................................................................................((((((...........))))))...................................................(((..(............)..)))....(((((((.....))))))).....................................((((((.......))))))....................((((((.....))))))..................((((((...))))))............................((((((......))))))..........................................(((..(.........)..)))................................(((..(((....)))..))).........................((((((((.........)))))))).(((((((....)))))))......((..((..........))..)).....(((((((...........)))))))................(((((((.....)))))))..............................................................................(((((((((.......)))))))))..........................................((((.................))))....((((((......))))))............(((((((......)))))))...............(((((.....))))).......(((...................)))..((((.................)))).................(((((...............)))))((((((.......)))))).(((((((((....))))))..)))................................................(((((..........)))))......(((((.....))))).......(((((((.......))))))).................((((((....))))))......................................",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test19(self):
        ### $ ./bin/gtmfe -v -d 1 -dS -l 24 --prefilter 6 d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 1, 
            'tmismatch'  : False,
            'limitcdist' : 24,
            'prefilter'  : 6,
        }
        extraConfigParamsDict = {
            'rnafold'    : 0, 
            'unafold'    : 0,
            'dS'         : 1,
        }
        expectedResults = {
            'mfe'        : -356.2000, 
            'mfe-struct' : "..................................................................................................................................(((((((....)))))))..((((((((.........)))))))).............................................................(((..................)))........................................((((((....))))))..........................................................((((((((.........)))))))).....(((((((....)))))))....................................................................................................................((((((....))))))....................(((((((...)))))))..(((((...............))))).....................((((((.....))))))...........................(((((..........)))))...((((((......))))))...................((((((....)))))).....................................((((((........))))))....................................(((..(...........)..))).......................................................................((((((((........))))))))...............................................................................((((((....))))))..................................................................................................(((((((((....)))))))))..(((((.....)))))............((((((((....)))))))).........................................(((((((.....)))))))...................(((((((...........))))))).......................................(((((((...........))))))).........................................(((((.....)))))...((((((((......))))))))((((((..........)))))).....................................((((((..........))))))...............................................................................((((((((....))))))))....................................................................................((((((...........))))))...................................................(((..(............)..)))....(((((((.....))))))).....................................((((((.......))))))....................((((((.....))))))..................((((((...))))))............................((((((......))))))..........................................(((..(.........)..)))................................(((..(((....)))..))).........................((((((((.........)))))))).(((((((....)))))))......((..((..........))..)).....(((((((...........)))))))................(((((((.....)))))))..............................................................................(((((((((.......)))))))))..........................................((((.................))))....((((((......))))))............(((((((......)))))))...............(((((.....))))).......(((...................)))..((((.................)))).................(((((...............)))))((((((.......)))))).(((((((((....))))))..)))................................................(((((..........)))))......(((((.....))))).......(((((((.......))))))).................((((((....))))))......................................",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test20(self):
        ### $ ./bin/gtmfe -v -d 2 -l 24 --prefilter 6 d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 2, 
            'tmismatch'  : False,
            'limitcdist' : 24,
            'prefilter'  : 6,
        }
        extraConfigParamsDict = {
            'rnafold'    : 0, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -358.0000, 
            'mfe-struct' : "..................................................................................................................................(((((((....)))))))..((((((((.........)))))))).............................................................(((..................)))........................................((((((....))))))..........................................................((((((((.........)))))))).....(((((((....)))))))....................................................................................................................((((((....))))))....................(((((((...)))))))..(((((...............))))).....................((((((.....))))))...........................(((((..........)))))...((((((......))))))...................((((((....)))))).....................................((((((........))))))....................................(((..(...........)..))).......................................................................((((((((........))))))))...............................................................................((((((....))))))..................................................................................................(((((((((....)))))))))..(((((.....)))))............((((((((....)))))))).........................................(((((((.....)))))))...................(((((((...........))))))).......................................(((((((...........))))))).........................................(((((.....)))))...((((((((......))))))))((((((..........)))))).....................................((((((..........))))))...............................................................................((((((((....))))))))....................................................................................((((((...........))))))...................................................(((..(............)..)))....(((((((.....))))))).....................................((((((.......))))))....................((((((.....))))))..................((((((...))))))............................((((((......))))))..........................................(((..(.........)..)))................................(((..(((....)))..))).........................((((((((.........)))))))).(((((((....)))))))......((..((..........))..)).....(((((((...........)))))))................(((((((.....)))))))..............................................................................(((((((((.......)))))))))..........................................((((.................))))....((((((......))))))............(((((((......)))))))...............(((((.....))))).......(((...................)))..((((.................)))).................(((((...............)))))((((((.......)))))).(((((((((....))))))..)))................................................(((((..........)))))......(((((.....))))).......(((((((.......))))))).................((((((....))))))......................................",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test21(self):
        ### $ ./bin/gtmfe -v -m -d 0 -l 24 --prefilter 6 d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 0, 
            'tmismatch'  : True,
            'limitcdist' : 24,
            'prefilter'  : 6,
        }
        extraConfigParamsDict = {
            'rnafold'    : 0, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -303.9000, 
            'mfe-struct' : "..................................................................................................................................(((((((....)))))))..((((((((.........)))))))).............................................................(((..................)))........................................((((((....))))))..........................................................((((((((.........)))))))).....(((((((....)))))))....................................................................................................................((((((....))))))....................(((((((...)))))))................................................((((((.....))))))..................................................((((((......))))))...................((((((....)))))).....................................((((((........))))))....................................(((..(...........)..))).......................................................................((((((((........))))))))...............................................................................((((((....))))))..................................................................................................(((((((((....)))))))))..(((((.....)))))............((((((((....)))))))).........................................(((((((.....)))))))...................(((((((...........))))))).......................................(((((((...........))))))).........................................((((((((((...))).)))))))...............(((((((..........)))))))....................................((((((..........))))))...............................................................................((((((((....))))))))....................................................................................((((((...........))))))...................................................(((..(............)..)))..............((((((...........)))))).......................((((((.......))))))....................((((((.....))))))..................((((((...))))))............................((((((......))))))..........................................(((..(.........)..)))................................(((..(((....)))..))).........................((((((((.........)))))))).(((((((....)))))))......((..((..........))..)).....(((((((...........)))))))................(((((((.....)))))))..............................................................................(((((((((.......))))))))).......................................................((((((....))))))((((((......))))))............(((((((......)))))))...............(((((.....)))))............................................................................(((((...............)))))((((((.......)))))).(((((((((....))))))..)))................................................(((((..........)))))......(((((.....))))).......(((((((.......))))))).................((((((....))))))......................................",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test22(self):
        ### $ ./bin/gtmfe -v -m -d 1 -l 24 --prefilter 6 d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 1, 
            'tmismatch'  : True,
            'limitcdist' : 24,
            'prefilter'  : 6,
        }
        extraConfigParamsDict = {
            'rnafold'    : 0, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -356.2000, 
            'mfe-struct' : "..................................................................................................................................(((((((....)))))))..((((((((.........)))))))).............................................................(((..................)))........................................((((((....))))))..........................................................((((((((.........)))))))).....(((((((....)))))))....................................................................................................................((((((....))))))....................(((((((...)))))))..(((((...............))))).....................((((((.....))))))...........................(((((..........)))))...((((((......))))))...................((((((....)))))).....................................((((((........))))))....................................(((..(...........)..))).......................................................................((((((((........))))))))...............................................................................((((((....))))))..................................................................................................(((((((((....)))))))))..(((((.....)))))............((((((((....)))))))).........................................(((((((.....)))))))...................(((((((...........))))))).......................................(((((((...........))))))).........................................(((((.....)))))...((((((((......))))))))((((((..........)))))).....................................((((((..........))))))...............................................................................((((((((....))))))))....................................................................................((((((...........))))))...................................................(((..(............)..)))....(((((((.....))))))).....................................((((((.......))))))....................((((((.....))))))..................((((((...))))))............................((((((......))))))..........................................(((..(.........)..)))................................(((..(((....)))..))).........................((((((((.........)))))))).(((((((....)))))))......((..((..........))..)).....(((((((...........)))))))................(((((((.....)))))))..............................................................................(((((((((.......)))))))))..........................................((((.................))))....((((((......))))))............(((((((......)))))))...............(((((.....))))).......(((...................)))..((((.................)))).................(((((...............)))))((((((.......)))))).(((((((((....))))))..)))................................................(((((..........)))))......(((((.....))))).......(((((((.......))))))).................((((((....))))))......................................",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test23(self):
        ### $ ./bin/gtmfe -v -m -d 1 -dS -l 24 --prefilter 6 d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 1, 
            'tmismatch'  : True,
            'limitcdist' : 24,
            'prefilter'  : 6,
        }
        extraConfigParamsDict = {
            'rnafold'    : 0, 
            'unafold'    : 0,
            'dS'         : 1,
        }
        expectedResults = {
            'mfe'        : -356.2000, 
            'mfe-struct' : "..................................................................................................................................(((((((....)))))))..((((((((.........)))))))).............................................................(((..................)))........................................((((((....))))))..........................................................((((((((.........)))))))).....(((((((....)))))))....................................................................................................................((((((....))))))....................(((((((...)))))))..(((((...............))))).....................((((((.....))))))...........................(((((..........)))))...((((((......))))))...................((((((....)))))).....................................((((((........))))))....................................(((..(...........)..))).......................................................................((((((((........))))))))...............................................................................((((((....))))))..................................................................................................(((((((((....)))))))))..(((((.....)))))............((((((((....)))))))).........................................(((((((.....)))))))...................(((((((...........))))))).......................................(((((((...........))))))).........................................(((((.....)))))...((((((((......))))))))((((((..........)))))).....................................((((((..........))))))...............................................................................((((((((....))))))))....................................................................................((((((...........))))))...................................................(((..(............)..)))....(((((((.....))))))).....................................((((((.......))))))....................((((((.....))))))..................((((((...))))))............................((((((......))))))..........................................(((..(.........)..)))................................(((..(((....)))..))).........................((((((((.........)))))))).(((((((....)))))))......((..((..........))..)).....(((((((...........)))))))................(((((((.....)))))))..............................................................................(((((((((.......)))))))))..........................................((((.................))))....((((((......))))))............(((((((......)))))))...............(((((.....))))).......(((...................)))..((((.................)))).................(((((...............)))))((((((.......)))))).(((((((((....))))))..)))................................................(((((..........)))))......(((((.....))))).......(((((((.......))))))).................((((((....))))))......................................",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test24(self):
        ### $ ./bin/gtmfe -v -m -d 2 -l 24 --prefilter 6 d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 2, 
            'tmismatch'  : True,
            'limitcdist' : 24,
            'prefilter'  : 6,
        }
        extraConfigParamsDict = {
            'rnafold'    : 0, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -358.0000, 
            'mfe-struct' : "..................................................................................................................................(((((((....)))))))..((((((((.........)))))))).............................................................(((..................)))........................................((((((....))))))..........................................................((((((((.........)))))))).....(((((((....)))))))....................................................................................................................((((((....))))))....................(((((((...)))))))..(((((...............))))).....................((((((.....))))))...........................(((((..........)))))...((((((......))))))...................((((((....)))))).....................................((((((........))))))....................................(((..(...........)..))).......................................................................((((((((........))))))))...............................................................................((((((....))))))..................................................................................................(((((((((....)))))))))..(((((.....)))))............((((((((....)))))))).........................................(((((((.....)))))))...................(((((((...........))))))).......................................(((((((...........))))))).........................................(((((.....)))))...((((((((......))))))))((((((..........)))))).....................................((((((..........))))))...............................................................................((((((((....))))))))....................................................................................((((((...........))))))...................................................(((..(............)..)))....(((((((.....))))))).....................................((((((.......))))))....................((((((.....))))))..................((((((...))))))............................((((((......))))))..........................................(((..(.........)..)))................................(((..(((....)))..))).........................((((((((.........)))))))).(((((((....)))))))......((..((..........))..)).....(((((((...........)))))))................(((((((.....)))))))..............................................................................(((((((((.......)))))))))..........................................((((.................))))....((((((......))))))............(((((((......)))))))...............(((((.....))))).......(((...................)))..((((.................)))).................(((((...............)))))((((((.......)))))).(((((((((....))))))..)))................................................(((((..........)))))......(((((.....))))).......(((((((.......))))))).................((((((....))))))......................................",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
  
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test25(self):
        ### $ ./bin/gtmfe -v -d 0 -l 10 --prefilter 6 d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 0, 
            'tmismatch'  : False,
            'limitcdist' : 10,
            'prefilter'  : 6,
        }
        extraConfigParamsDict = {
            'rnafold'    : 0, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -19.2000, 
            'mfe-struct' : "...............................................................................................................................................................................................................................................................................................................(((....)))...............................................................................................(((.....)))..........................................................................................................................(((....)))..........................((((...)))).....................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................(((....)))........................................(((....)))..................................................(((.....)))...........................................................................................................................................................(((.....)))................................................................................................................................................................................................(((....))).................................................................................................................................................................................................................................................................................................(((.....)))......................................................................................................................................................................................(((....)))........................................................(((.....)))...............................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................(((.....)))..................................................(((....))).........................................",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test26(self):
        ### $ ./bin/gtmfe -v -d 1 -l 10 --prefilter 6 d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 1, 
            'tmismatch'  : False,
            'limitcdist' : 10,
            'prefilter'  : 6,
        }
        extraConfigParamsDict = {
            'rnafold'    : 0, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -37.5000, 
            'mfe-struct' : "...............................................................................................................................................................................................................................................................................................................(((....)))...............................................................................................(((....)))...........................................................................................................................(((....)))..........................((((...)))).....................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................(((....)))..........(((.....)))...................(((....)))..................................................(((.....)))...........................................................................................................................................................(((.....)))................................................................................................................................................................................................(((....))).................................................................................................................................................................................................................................................................................................(((.....)))........................(((...))).....................................................................................................................................................(((....)))........................................................(((.....))).....................................................................................................................................................................................................................................................................(((....)))......................................................................(((.....))).................................................................................................................................(((....)))....................................................................................(((.....)))..................................................(((....))).........................................",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test27(self):
        ### $ ./bin/gtmfe -v -d 1 -dS -l 10 --prefilter 6 d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 1, 
            'tmismatch'  : False,
            'limitcdist' : 10,
            'prefilter'  : 6,
        }
        extraConfigParamsDict = {
            'rnafold'    : 0, 
            'unafold'    : 0,
            'dS'         : 1,
        }
        expectedResults = {
            'mfe'        : -37.5000, 
            'mfe-struct' : "...............................................................................................................................................................................................................................................................................................................(((....)))...............................................................................................(((....)))...........................................................................................................................(((....)))..........................((((...)))).....................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................(((....)))..........(((.....)))...................(((....)))..................................................(((.....)))...........................................................................................................................................................(((.....)))................................................................................................................................................................................................(((....))).................................................................................................................................................................................................................................................................................................(((.....)))........................(((...))).....................................................................................................................................................(((....)))........................................................(((.....))).....................................................................................................................................................................................................................................................................(((....)))......................................................................(((.....))).................................................................................................................................(((....)))....................................................................................(((.....)))..................................................(((....))).........................................",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test28(self):
        ### $ ./bin/gtmfe -v -d 2 -l 10 --prefilter 6 d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 2, 
            'tmismatch'  : False,
            'limitcdist' : 10,
            'prefilter'  : 6,
        }
        extraConfigParamsDict = {
            'rnafold'    : 0, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -37.5000, 
            'mfe-struct' : "...............................................................................................................................................................................................................................................................................................................(((....)))...............................................................................................(((....)))...........................................................................................................................(((....)))..........................((((...)))).....................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................(((....)))..........(((.....)))...................(((....)))..................................................(((.....)))...........................................................................................................................................................(((.....)))................................................................................................................................................................................................(((....))).................................................................................................................................................................................................................................................................................................(((.....)))........................(((...))).....................................................................................................................................................(((....)))........................................................(((.....))).....................................................................................................................................................................................................................................................................(((....)))......................................................................(((.....))).................................................................................................................................(((....)))....................................................................................(((.....)))..................................................(((....))).........................................",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test29(self):
        ### $ ./bin/gtmfe -v -m -d 0 -l 10 --prefilter 6 d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 0, 
            'tmismatch'  : True,
            'limitcdist' : 10,
            'prefilter'  : 6,
        }
        extraConfigParamsDict = {
            'rnafold'    : 0, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -19.2000, 
            'mfe-struct' : "...............................................................................................................................................................................................................................................................................................................(((....)))...............................................................................................(((.....)))..........................................................................................................................(((....)))..........................((((...)))).....................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................(((....)))........................................(((....)))..................................................(((.....)))...........................................................................................................................................................(((.....)))................................................................................................................................................................................................(((....))).................................................................................................................................................................................................................................................................................................(((.....)))......................................................................................................................................................................................(((....)))........................................................(((.....)))...............................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................(((.....)))..................................................(((....))).........................................",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test30(self):
        ### $ ./bin/gtmfe -v -m -d 1 -l 10 --prefilter 6 d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 1, 
            'tmismatch'  : True,
            'limitcdist' : 10,
            'prefilter'  : 6,
        }
        extraConfigParamsDict = {
            'rnafold'    : 0, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -37.5000, 
            'mfe-struct' : "...............................................................................................................................................................................................................................................................................................................(((....)))...............................................................................................(((....)))...........................................................................................................................(((....)))..........................((((...)))).....................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................(((....)))..........(((.....)))...................(((....)))..................................................(((.....)))...........................................................................................................................................................(((.....)))................................................................................................................................................................................................(((....))).................................................................................................................................................................................................................................................................................................(((.....)))........................(((...))).....................................................................................................................................................(((....)))........................................................(((.....))).....................................................................................................................................................................................................................................................................(((....)))......................................................................(((.....))).................................................................................................................................(((....)))....................................................................................(((.....)))..................................................(((....))).........................................",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test31(self):
        ### $ ./bin/gtmfe -v -m -d 1 -dS -l 10 --prefilter 6 d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 1, 
            'tmismatch'  : True,
            'limitcdist' : 10,
            'prefilter'  : 6,
        }
        extraConfigParamsDict = {
            'rnafold'    : 0, 
            'unafold'    : 0,
            'dS'         : 1,
        }
        expectedResults = {
            'mfe'        : -37.5000, 
            'mfe-struct' : "...............................................................................................................................................................................................................................................................................................................(((....)))...............................................................................................(((....)))...........................................................................................................................(((....)))..........................((((...)))).....................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................(((....)))..........(((.....)))...................(((....)))..................................................(((.....)))...........................................................................................................................................................(((.....)))................................................................................................................................................................................................(((....))).................................................................................................................................................................................................................................................................................................(((.....)))........................(((...))).....................................................................................................................................................(((....)))........................................................(((.....))).....................................................................................................................................................................................................................................................................(((....)))......................................................................(((.....))).................................................................................................................................(((....)))....................................................................................(((.....)))..................................................(((....))).........................................",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(MFE_CUSTOM_TESTS))
    def test__MFE_CustomParams_test32(self):
        ### $ ./bin/gtmfe -v -m -d 2 -l 10 --prefilter 6 d.23.b.E.coli.fasta ###
        configParamsDict = {
            'dangle'     : 2, 
            'tmismatch'  : True,
            'limitcdist' : 10,
            'prefilter'  : 6,
        }
        extraConfigParamsDict = {
            'rnafold'    : 0, 
            'unafold'    : 0,
            'dS'         : 0,
        }
        expectedResults = {
            'mfe'        : -37.5000, 
            'mfe-struct' : "...............................................................................................................................................................................................................................................................................................................(((....)))...............................................................................................(((....)))...........................................................................................................................(((....)))..........................((((...)))).....................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................(((....)))..........(((.....)))...................(((....)))..................................................(((.....)))...........................................................................................................................................................(((.....)))................................................................................................................................................................................................(((....))).................................................................................................................................................................................................................................................................................................(((.....)))........................(((...))).....................................................................................................................................................(((....)))........................................................(((.....))).....................................................................................................................................................................................................................................................................(((....)))......................................................................(((.....))).................................................................................................................................(((....)))....................................................................................(((.....)))..................................................(((....))).........................................",
        }
        self.RunMFECustomParametersTest(configParamsDict, extraConfigParamsDict, expectedResults)
    ##

    def RunGTSuboptTest(self, configParams, extraConfigParams, expectedResults):
        self.setUpGTSuboptCustomParametersTypeTest()
        GTFoldPython.ConfigExtraSettings(extraConfigParams)
        baseSeq = "GAAACUAUAAUUCAAUUGGUUAGAAUAGUAUUUUGAUAAGGUACAAAUAUAGGUUCAAUCCCUGUUAGUUUCA"
        orgName = "S.cerevisiae.45 (V00695.1) -- Bases: 3453-3525 -- Primary Key: 386"
        self.DescribeUnitTest("GTSubopt Custom Parameters Test -- Get the Python bindings output to match the GTFold utility")
        self.NameOrganism(orgName)
        self.OrganismBaseSequence(baseSeq)
        self.DefineConstraints([])
        self.PrintTestInfo(stackOffset=2)
        #self.ComputeMFEData()
        #(mfeExpected, mfeStructExpected) = (expectedResults['mfe'], expectedResults['mfe-struct'])
        #self.AssertLastMFETupleEquals(mfeExpected, mfeStructExpected)    
        
        ## TODO:
        ## take a short tRNA sequence ... 
        ## delta = 0.5 (very small)
        ## dS = True or dangle = 2
        ## uniquemultiloop T/F
        ## TODO: Pass in a dictionary of (dotStruct, energy) pairs to check results [will need to sort them] ... 
        pass
    ##

    @unittest.expectedFailure
    def test_GTSubopt(self):
        self.assertTrue(False)
    ##
 
    @unittest.skipIf(*UnitTestDecorArgs(PFUNC_TESTS))
    def test___PFunc_test_accurate_structure_count(self):
        ### $ ./bin/gtboltzmann -v -d 0 -l 3 --pfcount --useSHAPE K00421.shape K00421.seq 
        #    GTfold: A Scalable Multicore Code for RNA Secondary Structure Prediction
        #    (c) 2007-2011  D.A. Bader, C.E. Heitsch, S.C. Harvey
        #    Georgia Institute of Technology
        #
        #
        #    Validating Options:
        #
        #
        #    Run Configuration:
        #    + running with --pfcount option
        #    + running with customized param dir: /Users/mschmidt34/GTDMMBSoftware/gtfold/gtfold-mfe/data/Turner99
        #    - maximum contact distance: 3
        #    - using SHAPE data file: K00421.shape
        #    - thermodynamic parameters: /Users/mschmidt34/GTDMMBSoftware/gtfold/gtfold-mfe/data/Turner99/
        #    - input sequence file: K00421.seq
        #    - sequence length: 1474
        #    - scale factor: 1.070000
        #    - Partition Function and Sampling calculation to use: native double
        #
        #
        #    Limiting contact distance to 3
        #    mfe 0
        #
        #    Computing partition function...
        #    Actual Scaling Factor exp((scaleFactor*mfe*100)/(RT*part_len))=1
        #    Thread count:   4
        #    Possible structure count: 1
        #    partition function computation running time: 46.548535 seconds
        ###
        self.DescribeUnitTest("Testing the partition function used with GTBoltzmann to count total possible structures")
        GTFoldPython.SetDangleParameter(0)
        GTFoldPython.SetLimitContactDistance(3)
        baseSeq = "AUUCCGGUUGAUCCUGCCGGAGGUCAUUGCUAUUGGGGUCCGAUUUAGCCAUGCUAGUUGCACGAGUUCAUACUCGUGGC" + \
                  "GAAAAGCUCAGUAACACGUGGCCAAACUACCCUACAGAGAACGAUAACCUCGGGAAACUGAGGCUAAUAGUUCAUACGGG" + \
                  "AGUCAUGCUGGAAUGCCGACUCCCCGAAACGCUCAGGCGCUGUAGGAUGUGGCUGCGGCCGAUUAGGUAGACGGUGGGGU" + \
                  "AACGGCCCACCGUGCCGAUAAUCGGUACGGGUUGUGAGAGCAAGAGCCCGGAGACGGAAUCUGAGACAAGAUUCCGGGCC" + \
                  "CUACGGGGCGCAGCAGGCGCGAAACCUUUACACUGCACGCAAGUGCGAUAAGGGGACCCCAAGUGCGAGGGCAUAUAGUC" + \
                  "CUCGCUUUUCUCGACCGUAAGGCGGUCGAGGAAUAAGAGCUGGGCAAGACCGGUGCCAGCCGCCGCGGUAAUACCGGCAG" + \
                  "CUCAAGUGAUGACCGAUAUUAUUGGGCCUAAAGCGUCCGUAGCCGGCCACGAAGGUUCAUCGGGAAAUCCGCCAGCUCAA" + \
                  "CUGGCGGGCGUCCGGUGAAAACCACGUGGCUUGGGACCGGAAGGCUCGAGGGGUACGUCCGGGGUAGGAGUGAAAUCCCG" + \
                  "UAAUCCUGGACGGACCACCGAUGGCGAAAGCACCUCGAGAAGACGGAUCCGACGGUGAGGGACGAAAGCUAGGGUCUCGA" + \
                  "ACCGGAUUAGAUACCCGGGUAGUCCUAGCUGUAAACGAUGCUCGCUAGGUGUGACACAGGCUACGAGCCUGUGUUGUGCC" + \
                  "GUAGGGAAGCCGAGAAGCGAGCCGCCUGGGAAGUACGUCCGCAAGGAUGAAACUUAAAGGAAUUGGCGGGGGAGCACUAC" + \
                  "AACCGGAGGAGCCUGCGGUUUAAUUGGACUCAACGCCGGACAUCUCACCAGCUCCGACUACAGUGAUGACGAUCAGGUUG" + \
                  "AUGACCUUAUCACGACGCUGUAGAGAGGAGGUGCAUGGCCGCCGUCAGCUCGUACCGUGAGGCGUCCUGUUAAGUCAGGC" + \
                  "AACGAGCGAGACCCGCACUUCUAAUUGCCAGCAGCAGUUUCGACUGGCUGGGUACAUUAGAAGGACUGCCGCUGCUAAAG" + \
                  "CGGAGGAAGGAACGGGCAACGGUAGGUCAGUAUGCCCCGAAUGAGCUGGGCUACACGCGGGCUACAAUGGUCGAGACAAU" + \
                  "GGGUUGCUAUCUCGAAAGAGAACGCUAAUCUCCUAAACUCGAUCGUAGUUCGGAUUGAGGGCUGAAACUCGCCCUCAUGA" + \
                  "AGCUGGAUUCGGUAGUAAUCGCAUUUCAAUAGAGUGCGGUGAAUACGUCCCUGCUCCUUGCACACACCGCCCGUCAAAGC" + \
                  "ACCCGAGUGAGGUCCGGAUGAGGCCACCACACGGUGGUCGAAUCUGGGCUUCGCAAGGGGGCUUAAGUCGUAACAAGGUA" + \
                  "GCCGUAGGGGAAUCUGCGGCUGGAUCACCUCCUG"
        consSHAPE = GTFoldPythonUnitTests.LoadConstraintsFromFile("../Testing/SampleFiles/K00421.shape")
        totalStructsExpected = 1
        self.NameOrganism("H. volcanii", "K00421")
        self.OrganismBaseSequence(baseSeq)
        self.DefineConstraints(consSHAPE)
        self.PrintTestInfo(stackOffset=1)
        pfCount = GTFoldPython.GetPFuncCountSHAPE(baseSeq, consSHAPE)
        testPassedCond = totalStructsExpected == int(round(float(pfCount), 0))
        if testPassedCond:
            print(" ... TEST PASSED! [OK]")
        else:
            print(" ... TEST FAILED! [XX]")
        self.assertTrue(testPassedCond)
    ##

##

if __name__ == '__main__':
    logging.basicConfig( stream=sys.stderr )
    logging.getLogger( "GTFOLDPYTHON-TEST-LOG" ).setLevel( logging.DEBUG )
    unittest.main(verbosity=0)
