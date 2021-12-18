#### GTFoldPythonUnitTests.py : Run unit tests to verify basic functionality of GTFoldPython;
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

class GTFoldPythonUnitTests(unittest.TestCase):

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
        consList = []
        with open(consFilePath, encoding = 'utf-8') as fd:
             consStr = fd.readline().rstrip()
             consList = GTFPUtils.GetFPConstraintsFromString(consStr)
        return consList
    ##

    def AssertLastMFETupleEquals(self, mfe, mfeDOTStruct):
        self.assertEqual(mfe, self._lastMFE)
        self.assertEqual(mfeDOTStruct, self._lastMFEStruct)
        return True
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

    def PrintTestInfo(self):
        testMethod = inspect.stack()[3].function
        orgPrintName = self._orgName
        if self._orgAccNo != "":
            orgPrintName += "(" + self._orgAccNo + ")"
        basePrintSeq = self._orgBaseSeq if len(self._orgBaseSeq) <= 16 else \
                self._orgBaseSeq[0:8] + " ... " + self._orgBaseSeq[-15:]
        numConstF = [ cons[0] for cons in self._testConstraints].count(GTFoldPython.F)
        numConstP = [ cons[0] for cons in self._testConstraints].count(GTFoldPython.P)
        constPrintStatus = "None enabled" if len(self._testConstraints) == 0 else \
                "%d Total, %d Forced, %d Prohibited" % (numConstF + numConstP, numConstF, numConstP)
        print("\n\n|| GTFOLD-PYTHON UNIT TEST INFO: (" + str(testMethod) + ")")
        print("    ## %d" % GTFoldPythonUnitTests._testNumber)
        print("    >> Test Purpose:    %s" % self._testPurpose)
        print("    >> Organism:        %s" % orgPrintName)
        print("    >> Base Sequence:   [#%d] %s" % (len(self._orgBaseSeq), basePrintSeq))
        print("    >> Constraints:     %s" % constPrintStatus)
        print("////")
    ##

    def setUp(self):
        GTFoldPython._ConstructLibGTFold()
        GTFoldPython.Config(debugging = False)
        GTFoldPython.SetThermodynamicParametersFromDefaults("RNAStructure")
        #GTFoldPython.SetPrefilterParameter(1)
        #GTFoldPython.SetDangleParameter(0)
        GTFoldPython.EnableTerminalMismatch()
        self._testPurpose = ""
        self._testConstraints = []
        self._orgName = ""
        self._orgAccNo = ""
        self._orgBaseSeq = ""
        self._testResultExpectedMFE = None
        self._testResultExpectedMFEStruct = None
    ##

    def tearDown(self):
        pass
    ##

    def TestTypeV1_NoConstraints(self, inputSeq, outputStruct, outputMFE):
        self.DescribeUnitTest("Basic MFE calculation without constraints")
        (orgName, baseSeq) = GTFoldPythonUnitTests.LoadInputSequenceFromFile(inputSeq)
        self.NameOrganism(orgName)
        self.OrganismBaseSequence(baseSeq)
        self.DefineConstraints([])
        self.ComputeMFEData()
        (mfe, mfeStruct) = (GTFoldPythonUnitTests.LoadOutputMFEFromFile(outputMFE), 
                            GTFoldPythonUnitTests.LoadOutputStructFromFile(outputStruct))
        self.PrintTestInfo()
        if self.AssertLastMFETupleEquals(mfe, mfeStruct):
            print(" ... TEST PASSED! [OK]")
        ##
    ##

    def RunTestTypeV1_NoConstraints(self, inputSeqBaseName):
        inputSeqBaseName = GTFoldPythonUnitTests.TESTDATADIR + "/" + inputSeqBaseName
        self.TestTypeV1_NoConstraints(inputSeqBaseName + ".seq", 
                                      inputSeqBaseName + ".mfestruct.dot", 
                                      inputSeqBaseName + ".mfe");
    ##

    def TestTypeV2_WithConstraints(self, inputSeq, consFile, outputStruct, outputMFE):
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
        argFileExts = [ "seq", "cons", "cons.mfestruct.dot", "cons.mfe" ]
        fileArgs = [ inputSeqBaseName + "." + fext for fext in argFileExts ]
        self.TestTypeV2_WithConstraints(*fileArgs);
    ##

    def test1_16S_K00421(self):
        GTFoldPythonUnitTests.RunTestTypeV1_NoConstraints(self, "16S/K00421")
    ##
 
    def test2_5S_EColiFa(self):
        GTFoldPythonUnitTests.RunTestTypeV1_NoConstraints(self, "5S/E.coli.fa")
    ##
 
    def test2_5S_EColiFa_withcons_RNAfold(self):
        GTFoldPythonUnitTests.RunTestTypeV2_WithConstraints(self, "5S/E.coli.fa")
    ##
 
    def test3_tRNA_yeastFa(self):
        GTFoldPythonUnitTests.RunTestTypeV1_NoConstraints(self, "tRNA/yeast.fa")
    ##
  
    def test3_tRNA_yeastFa_withcons_RNAfold(self):
        GTFoldPythonUnitTests.RunTestTypeV2_WithConstraints(self, "tRNA/yeast.fa")
    ##
  
    def test4_other_humanFa(self):
        GTFoldPythonUnitTests.RunTestTypeV1_NoConstraints(self, "other/human.fa")
    ##
   
    def test4_other_humanFa_withcons_RNAfold(self):
        GTFoldPythonUnitTests.RunTestTypeV2_WithConstraints(self, "other/human.fa")
    ##
  
    def test5_other_PSyringae(self):
        GTFoldPythonUnitTests.RunTestTypeV1_NoConstraints(self, "other/P.syringae")
    ##
  
    def test5_other_PSyringae_withcons_RNAfold(self):
        GTFoldPythonUnitTests.RunTestTypeV2_WithConstraints(self, "other/P.syringae")
    ##

##

if __name__ == '__main__':
    logging.basicConfig( stream=sys.stderr )
    logging.getLogger( "GTFOLDPYTHON-TEST-LOG" ).setLevel( logging.INFO )
    unittest.main()
