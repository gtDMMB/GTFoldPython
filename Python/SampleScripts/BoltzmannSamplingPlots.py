#### BoltzmannSamplingPlots.py 
#### Author: Maxie D. Schmidt (github/maxieds)
#### Created: 2021.07.09

import sys, os
import math
import matplotlib.pyplot as plt
import numpy as np 
from GTFoldPythonImportAll import *

DEBUG = True

def ReInitGTFPLibrary():
    GTFP.Config(quiet=0, verbose=0, debugging=0)
    GTFP.ConfigExtraSettings( { 
        'workdir'             : os.path.expanduser("~/TestGTFoldPython"), 
        'calcpartition'       : 0, 
        'numthreads'          : 2,
        'printarrays'         : 0,
        'writeauxfiles'       : 0,
        'duplicatecheck'      : 1,
        'uniquemultiloop'     : 0,
        'countsparallel'      : 1,
    })
    GTFP.SetThermodynamicParametersFromDefaults(TURNER04)
    GTFP.SetDangleParameter(2)
    GTFP.SetTerminalMismatch(True)
    GTFP.SetLimitContactDistance(-1) # same as if not set
    GTFP.SetPrefilterParameter(-1)   # same as if not set

def IsCanonicalBasePair(baseSeq, bpIndexTuple):
    (i, j) = bpIndexTuple
    if i < 0 or j < 0 or i >= len(baseSeq) or j >= len(baseSeq):
        #raise ValueError("Base pair (%d, %d) is out of range!" % (i, j))
        return False
    watsonCrickBasePairs = [ ('A', 'U'), ('U', 'A'), ('G', 'C'), ('C', 'G') ]
    wobbleBasePairs = [ ('G', 'U'), ('U', 'G') ]
    bpBaseTuple = (baseSeq[i].upper(), baseSeq[j].upper())
    if bpBaseTuple in watsonCrickBasePairs or bpBaseTuple in wobbleBasePairs:
        return True
    return False

def GetBasePairsByContainment(dbStruct):
    pairwiseContainers = []
    unpairedBases = []
    curContainer = []
    basePairs = []
    for (seIdx, dbStructEntry) in enumerate(dbStruct):
        if dbStructEntry == '.':
            pass 
        elif dbStructEntry in [ '(', '<', '{' ]:
            unpairedBases.append(seIdx)
        elif dbStructEntry in [ ')', '>', '}' ] and len(unpairedBases) > 0:
            openPairIndex = unpairedBases.pop()
            curContainer.append( (openPairIndex, seIdx) )
            basePairs.append( (openPairIndex, seIdx) )
            if len(unpairedBases) == 0:
                pairwiseContainers.append(curContainer)
                curContainer = []
        else:
            raise ValueError("Invalid DOT structure character %s at index %d!" % (dbStructEntry, seIdx))
    if len(unpairedBases) > 0:
        raise ValueError("Invalid DOT structure (extra unpaired bases found)!")
    return basePairs

# For an excellent introduction to helices and helix classes, see the following article:
# https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4267672/pdf/gku959.pdf
def GetHelices(dbStruct):
    basePairsContainerList = [ GetBasePairsByContainment(dbStruct) ]
    helixContainerList = []
    for bpContainer in basePairsContainerList:
        helixContainer = []
        for basePair in bpContainer:
            (i, j) = basePair
            if abs(i - j) < 2:
                continue
            maxK = min(abs(i - j), len(bpContainer))
            for k in range(2, maxK + 1):
                proposedBasePairRun = [ (i + delta, j - delta) in bpContainer for delta in range(0, k) ] 
                if False not in proposedBasePairRun:
                    helixContainer.append( (i, j, k) )
        helixContainerList.append(helixContainer)
    return helixContainerList[0]

def GetMaximalHelices(baseSeq, helixContainerList):
    helixList = helixContainerList
    maximalHelices = []
    for helix in helixList:
        (i, j, k) = helix
        if j - i - 2 * k < 5:
            maximalHelices.append(helix)
        elif not IsCanonicalBasePair(baseSeq, (i - 1, j + 1)) and not IsCanonicalBasePair(baseSeq, (i + k, j - k)):
            maximalHelices.append(helix)
    return maximalHelices

def GetHelixClassCounts(baseSeq, dbStruct):
    helixList = GetHelices(dbStruct)
    if DEBUG: print("HELICES: ", helixList)
    #maximalHelices = GetMaximalHelices(baseSeq, helixList)
    #if DEBUG: print("MAXIMAL HELICES: ", maximalHelices)
    helixClassCountDict = dict([])
    for helix in helixList:
        helixClassCountDict[helix] = helixList.count(helix)
    return helixClassCountDict
    #for (maximalHelixIdx, maximalHelix) in enumerate(maximalHelices):
    #    (i, j, k) = maximalHelix
    #    helixClassPossiblePairs = [ (i + delta, j - delta) for delta in range(0, k) ]
    #    inClassCondFunc = lambda sijTuple: 1 if (sijTuple[0], sijTuple[1]) in helixClassPossiblePairs else 0
    #    classCount = sum(map(inClassCondFunc, helixList))
    #    helixClassCountDict[maximalHelix] = classCount
    #return helixClassCountDict

# Get the points as shown in Figure 1 of the following article: 
# https://www.cell.com/biophysj/fulltext/S0006-3495(17)30565-9
def GetFrequencyDistributionLocal(N, baseSeq, constraintsList=[]):
    boltzmannSamples = GTFP.SampleBoltzmannStructures(baseSeq, N, constraintsList)
    #if DEBUG: print("LENGTH: ", len(boltzmannSamples))
    helixClassFreqDict, maxHelixClassFreqDict = dict([]), dict([])
    freqToStdDevPoints = []
    for boltzmannSample in boltzmannSamples:
        (estBoltzProb, actBoltzProb, energy, sampleStruct) = boltzmannSample
        if DEBUG: print(boltzmannSample)
        helixClassCountsDict = GetHelixClassCounts(baseSeq, sampleStruct)
        for hcCountHelixIdx in helixClassCountsDict.keys():
            hcCount = helixClassCountsDict[hcCountHelixIdx]
            if hcCountHelixIdx in helixClassFreqDict:
                (hcFreq, hcFreqsList) = helixClassFreqDict[hcCountHelixIdx] 
                hcFreq += estBoltzProb * N 
                hcFreqsList.append(estBoltzProb * N)
                helixClassFreqDict[hcCountHelixIdx] = (hcFreq, hcFreqsList)
            else:
                sampleStructNumTimes = estBoltzProb * N
                helixClassFreqDict[hcCountHelixIdx] = (sampleStructNumTimes, [ sampleStructNumTimes ]) 
    #if DEBUG: print("HC FREQS LOCAL: ", helixClassFreqDict)
    helixList = helixClassFreqDict.keys()
    maximalHelices = GetMaximalHelices(baseSeq, helixList)
    #if DEBUG: print("MAXIMAL HELICES: ", maximalHelices)
    countSatisfiedFunc = lambda hi, hj, hk, mi, mj, mk: 1 if hi >= mi and hj <= mj and hk <= mk else 0
    countHelicesInMaximalFunc = lambda hlxList, hlx, maxHlx: sum([ countSatisfiedFunc(hi, hj, hk, maxHlx[0], maxHlx[1], maxHlx[2]) for (hi, hj, hk) in hlxList ])
    for (maximalHelixIdx, maximalHelix) in enumerate(maximalHelices):
        (i, j, k) = maximalHelix
        helixClassPossiblePairs = [ (i + delta, j - delta) for delta in range(0, k) ]
        #inClassCondFunc = lambda hi, hj, hk: countHelicesInMaximalFunc( helixList, (hi, hj, hk), (i, j, k) ) if (hi, hj) in helixClassPossiblePairs else 0
        inClassCondFunc = lambda hi, hj, hk: 1 if (hi, hj) in helixClassPossiblePairs else 0
        classCount = sum(map(lambda helix: inClassCondFunc(helix[0], helix[1], helix[2]), helixList))
        maxHelixClassFreqDict[maximalHelix] = classCount
    #if DEBUG: print("HC FREQS LOCAL BY MAX HLX: ", maxHelixClassFreqDict)
    return maxHelixClassFreqDict

def GetFrequencyDistribution(N, repeatM, baseSeq, constraintsList=[]):
    helixClassFreqDict = dict([])
    freqToStdDevPoints = []
    for M in range(0, repeatM):
        localHelixClassFreqDict = GetFrequencyDistributionLocal(N, baseSeq, constraintsList=constraintsList)
        for helixClass in localHelixClassFreqDict.keys():
            hcLocalFreq = localHelixClassFreqDict[helixClass]
            if helixClass in helixClassFreqDict:
                (hcFreq, hcFreqsList) = helixClassFreqDict[helixClass]
                hcFreq += hcLocalFreq
                hcFreqsList.append(hcLocalFreq)
                helixClassFreqDict[helixClass] = (hcFreq, hcFreqsList)
            else:
                hcFreq = hcLocalFreq
                hcFreqsList = [ hcFreq ]
                helixClassFreqDict[helixClass] = (hcFreq, hcFreqsList)
    #if DEBUG: print("HELIX CLASS COUNT #: ", helixClassFreqDict)
    for helixClass in helixClassFreqDict.keys():
        hcFreqsList = helixClassFreqDict[helixClass][1]
        hcFreqMean = sum(hcFreqsList) / repeatM
        stdDevTerms = list(map(lambda term: float((term - hcFreqMean)**2), hcFreqsList))
        stdDevTerms.extend( [ float(hcFreqMean**2) for zeroValuedFreqs in range(0, repeatM - len(stdDevTerms)) ] )
        stdDevOfFreqs = math.sqrt(sum(stdDevTerms) / repeatM)
        hcFreq = helixClassFreqDict[helixClass][0] / repeatM
        freqToStdDevPoints.append( (hcFreq, stdDevOfFreqs) )
        #if DEBUG: print("STD DEV TERMS: ", (hcFreq, stdDevOfFreqs))
    return freqToStdDevPoints

def GetFrequencyPlots(seqData, sampleSizeN, samplesM, repeatNumPlots, constraintsList=[], showPlot=True):
    (seqName, baseSeq) = seqData
    mpFig = plt.figure()
    gridSpec = mpFig.add_gridspec(repeatNumPlots)
    mpAxs = gridSpec.subplots(sharex=True, sharey=True)
    stdDevFunc = lambda n, p: math.sqrt(n * p * (1 - p))
    mpFig.suptitle("%s Helix Class Frequencies" % seqName)
    for trialM in range(0, repeatNumPlots):
        xFreqs = list(np.arange(1, sampleSizeN, 1))
        stdDevPoints = GetFrequencyDistribution(sampleSizeN, samplesM, baseSeq, constraintsList)
        stdDevX = [ sdPointFreq for (sdPointFreq, sd) in stdDevPoints ]
        stdDevY = [ sd for (freq, sd) in stdDevPoints ]
        theoreticalStdDevPoints = [ stdDevFunc(sampleSizeN, float(x / sampleSizeN)) for x in xFreqs ]
        ax = mpAxs if repeatNumPlots <= 1 else mpAxs[trialM]
        ax.set(xlabel='observed frequency', ylabel='sample stddev')
        ax.label_outer()
        ax.plot(xFreqs, theoreticalStdDevPoints, 'b-')
        ax.scatter(stdDevX, stdDevY, alpha=0.5)
        ax.set_title("Trial #%d -- M=%d Samples with N=%d Structures Per Sample" % (trialM + 1, samplesM, sampleSizeN))
    if showPlot:
        plt.show()

if __name__=="__main__":

    ReInitGTFPLibrary()

    N, M = 1000, 3
    numRepeatTrials = 1
    baseSeqDict = dict([
        #("yeast (native structure)", 
        # "GCCGUGAUAGUUUAAUGGUCAGAAUGGGCGCUUGUCGCGUGCCAGAUCGGGGUUCAAUUCCCCGUCGCGGCGCCA"),
        #("Phalaenopsis aphrodite subsp. formosana (AY916449)", 
        # "GUCGGGAUAGCUCAGUUGGUAGAGCAGAGGACUGAAAAUCCUCGUGUCACCAGUUCAAAUCUGGUUCCUGACA"),
        # https://rfam.xfam.org/accession/CP001956.1?seq_start=1598192&seq_end=1599664
        ("Haloferax volcanii",       
         "ATTCCGGTTGATCCTGCCGGAGGTCATTGCTATTGGGGTCCGATTTAGCCATGCTAGTTG" + 
         "CACGAGTTCATACTCGTGGCGAAAAGCTCAGTAACACGTGGCCAAACTACCCTACAGAGA" +
         "ACGATAACCTCGGGAAACTGAGGCTAATAGTTCATACGGGAGTCATGCTGGAATGCCGAC" + 
         "TCCCCGAAACGCTCAGGCGCTGTAGGATGTGGCTGCGGCCGATTAGGTAGACGGTGGGGT" +
         "AACGGCCCACCGTGCCGATAATCGGTACGGGTTGTGAGAGCAAGAGCCCGGAGACGGAAT" +
         "CTGAGACAAGATTCCGGGCCCTACGGGGCGCAGCAGGCGCGAAACCTTTACACTGCACGC" +
         "AAGTGCGATAAGGGGACCCCAAGTGCGAGGGCATATAGTCCTCGCTTTTCTCGACCGTAA" +
         "GGCGGTCGAGGAATAAGAGCTGGGCAAGACCGGTGCCAGCCGCCGCGGTAATACCGGCAG" + 
         "CTCAAGTGATGACCGATATTATTGGGCCTAAAGCGTCCGTAGCCGGCCACGAAGGTTCAT" +
         "CGGGAAATCCGCCAGCTCAACTGGCGGGCGTCCGGTGAAAACCACGTGGCTTGGGACCGG" +
         "AAGGCTCGAGGGGTACGTCCGGGGTAGGAGTGAAATCCCGTAATCCTGGACGGACCACCG" +
         "ATGGCGAAAGCACCTCGAGAAGACGGATCCGACGGTGAGGGACGAAAGCTAGGGTCTCGA" +
         "ACCGGATTAGATACCCGGGTAGTCCTAGCTGTAAACGATGCTCGCTAGGTGTGACACAGG" +
         "CTACGAGCCTGTGTTGTGCCGTAGGGAAGCCGAGAAGCGAGCCGCCTGGGAAGTACGTCC" +
         "GCAAGGATGAAACTTAAAGGAATTGGCGGGGGAGCACTACAACCGGAGGAGCCTGCGGTT" +
         "TAATTGGACTCAACGCCGGACATCTCACCAGCTCCGACTACAGTGATGACGATCAGGTTG" +
         "ATGACCTTATCACGACGCTGTAGAGAGGAGGTGCATGGCCGCCGTCAGCTCGTACCGTGA" +
         "GGCGTCCTGTTAAGTCAGGCAACGAGCGAGACCCGCACTTCTAATTGCCAGCAGCAGTTT" +
         "CGACTGGCTGGGTACATTAGAAGGACTGCCGCTGCTAAAGCGGAGGAAGGAACGGGCAAC" + 
         "GGTAGGTCAGTATGCCCCGAATGAGCTGGGCTACACGCGGGCTACAATGGTCGAGACAAT" +
         "GGGTTGCTATCTCGAAAGAGAACGCTAATCTCCTAAACTCGATCGTAGTTCGGATTGAGG" + 
         "GCTGAAACTCGCCCTCATGAAGCTGGATTCGGTAGTAATCGCATTTCAATAGAGTGCGGT" +
         "GAATACGTCCCTGCTCCTTGCACACACCGCCCGTCAAAGCACCCGAGTGAGGTCCGGATG" +
         "AGGCCACCACACGGTGGTCGAATCTGGGCTTCGCAAGGGGGCTTAAGTCGTAACAAGGTA"
         "GCCGTAGGGGAATCTGCGGCTGGATCACCTCCT"), 
    ])
 
    numLeadingBasesToPrint = 16
    for sequenceID in baseSeqDict.keys():
        baseSeq = baseSeqDict[sequenceID]
        GTFP.PrintRunConfiguration()
        print(">> Computing M=%d Frequency StdDev Plots for the Sequence" % numRepeatTrials)
        (startSeq, endSeq) = (baseSeq[0:min(numLeadingBasesToPrint, len(baseSeq))], \
                              baseSeq[-min(numLeadingBasesToPrint, max(len(baseSeq) - numLeadingBasesToPrint, 0)):])
        print("   %s [ %s ... %s ]" % (sequenceID, startSeq, endSeq))
        GetFrequencyPlots( (sequenceID, baseSeq), N, M, numRepeatTrials, showPlot=True)
        print("")
    
    sys.exit(0)

