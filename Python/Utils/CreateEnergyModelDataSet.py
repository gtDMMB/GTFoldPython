#### CreateEnergyModelDataSet.py : Create the energy model data set *.DAT files from a text-based 
####                               one-float-value-per-line parameters file in the format of 
####                               ../Testing/ExtraGTFoldThermoData/BuildingCustomDataSets/turner_partypes_fm363.txt
#### Usage: python3 CreateEnergyModelDataSet.py <FM363-TURNER-PARAMTYPES-PARAMS-FILE> <RELATIVE-OUTPUT-DIR>
#### Author: Maxie D. Schmidt (maxieds@gmail.com)
#### Created: 2020.02.23

import sys, os
import numpy as np

def InitStackFile(stackValuesList, outputFile):
     fourBaseIndex = lambda a, b, c, d: (a << 6) + (b << 4) + (c << 2) + d
     _stack = [ "inf" for idx in range(0, 256) ]
     fourDimSpecIndices = [
         (0, 3, 0, 3), 
         (0, 3, 1, 2), 
         (0, 3, 2, 1), 
         (0, 3, 2, 3), 
         (0, 3, 3, 0), 
         (0, 3, 3, 2),
         (1, 2, 0, 3), 
         (1, 2, 1, 2), 
         (1, 2, 2, 3), 
         (1, 2, 3, 2),
         (2, 1, 0, 3), 
         (2, 1, 1, 2), 
         (2, 1, 2, 3), 
         (2, 1, 3, 2), 
         (2, 3, 0, 3), 
         (2, 3, 2, 3), 
         (2, 3, 3, 2),
         (3, 0, 0, 3), 
         (3, 0, 2, 3), 
         (3, 2, 2, 3),
     ]
     for (idx, indexSpec) in enumerate(fourDimSpecIndices):
          _stack[ fourBaseIndex(*list(indexSpec)) ] = stackValuesList[idx]
     with open(outputFile, "w+", encoding = 'utf-8') as stackFD:
          for count in range(0, 16):
              for cols in range(0, 16):
                  valueStr = "{0}".format(_stack[16 * count + cols]).ljust(8)
                  stackFD.write(valueStr)
              stackFD.write('\n')
          ##
     ##
     return True
##

def InitTStackHFile(stackValuesList, outputFile):
    fourBaseIndex = lambda a, b, c, d: (a << 6) + (b << 4) + (c << 2) + d
    _tstackh = [ "inf" for idx in range(0, 256) ]
    tstackhIndices = [
        (0, 3, 0, 0), 
        (0, 3, 0, 1), 
        (0, 3, 0, 2), 
        (0, 3, 0, 3), 
        (0, 3, 1, 0),
        (0, 3, 1, 1), 
        (0, 3, 1, 2), 
        (0, 3, 1, 3), 
        (0, 3, 2, 0), 
        (0, 3, 2, 1), 
        (0, 3, 2, 2), 
        (0, 3, 2, 3), 
        (0, 3, 3, 0),
        (0, 3, 3, 1), 
        (0, 3, 3, 2), 
        (0, 3, 3, 3), 
        (1, 2, 0, 0), 
        (1, 2, 0, 1), 
        (1, 2, 0, 2), 
        (1, 2, 0, 3), 
        (1, 2, 1, 0), 
        (1, 2, 1, 1), 
        (1, 2, 1, 2),
        (1, 2, 1, 3), 
        (1, 2, 2, 0), 
        (1, 2, 2, 1),
        (1, 2, 2, 2),
        (1, 2, 2, 3),
        (1, 2, 3, 0), 
        (1, 2, 3, 1), 
        (1, 2, 3, 2), 
        (1, 2, 3, 3), 
        (2, 1, 0, 0),
        (2, 1, 0, 1),
        (2, 1, 0, 2),
        (2, 1, 0, 3),
        (2, 1, 1, 0),
        (2, 1, 1, 1),
        (2, 1, 1, 2),
        (2, 1, 1, 3),
        (2, 1, 2, 0),
        (2, 1, 2, 1),
        (2, 1, 2, 2),
        (2, 1, 2, 3),
        (2, 1, 3, 0),
        (2, 1, 3, 1),
        (2, 1, 3, 2),
        (2, 1, 3, 3),
        (2, 3, 0, 0),
        (2, 3, 0, 1),
        (2, 3, 0, 2),
        (2, 3, 0, 3),
        (2, 3, 1, 0),
        (2, 3, 1, 1),
        (2, 3, 1, 2),
        (2, 3, 1, 3),
        (2, 3, 2, 0),
        (2, 3, 2, 1),
        (2, 3, 2, 2),
        (2, 3, 2, 3),
        (2, 3, 3, 0),
        (2, 3, 3, 1),
        (2, 3, 3, 2),
        (2, 3, 3, 3),
        (3, 0, 0, 0),
        (3, 0, 0, 1),
        (3, 0, 0, 2),
        (3, 0, 0, 3),
        (3, 0, 1, 0),
        (3, 0, 1, 1),
        (3, 0, 1, 2),
        (3, 0, 1, 3),
        (3, 0, 2, 0),
        (3, 0, 2, 1),
        (3, 0, 2, 2),
        (3, 0, 2, 3),
        (3, 0, 3, 0),
        (3, 0, 3, 1),
        (3, 0, 3, 2),
        (3, 0, 3, 3),
        (3, 2, 0, 0),
        (3, 2, 0, 1),
        (3, 2, 0, 2),
        (3, 2, 0, 3),
        (3, 2, 1, 0),
        (3, 2, 1, 1),
        (3, 2, 1, 2),
        (3, 2, 1, 3),
        (3, 2, 2, 0),
        (3, 2, 2, 1),
        (3, 2, 2, 2),
        (3, 2, 2, 3),
        (3, 2, 3, 0),
        (3, 2, 3, 1),
        (3, 2, 3, 2),
        (3, 2, 3, 3),
    ]
    for (idx, indexSpec) in enumerate(tstackhIndices):
          _tstackh[ fourBaseIndex(*list(indexSpec)) ] = stackValuesList[idx]
    with open(outputFile, "w+", encoding = 'utf-8') as tstackFD:
          for idx in range(0, 256): 
              if idx > 0 and idx % 16 == 0:
                  tstackFD.write('\n')
              valueStr = "{0}".format(_tstackh[idx]).ljust(8)
              tstackFD.write(valueStr)
          ##
    ##
    return True
##

def InitInt11File(int11ValuesList, outputFile):
    _int11 = np.array([ "inf" for idx in range(0, 5**6) ])
    _int11 = np.reshape(_int11, (5, 5, 5, 5, 5, 5), order = 'C')
    int11Indices = [
        (0, 3, 3, 3, 0, 3),
        (0, 3, 3, 3, 1, 2),
        (0, 3, 3, 3, 2, 1),
        (0, 3, 3, 3, 3, 0),
        (1, 2, 0, 0, 1, 2),
        (1, 2, 0, 0, 2, 1),
        (1, 2, 0, 1, 1, 2),
        (1, 2, 0, 1, 2, 1),
        (1, 2, 0, 2, 1, 2),
        (1, 2, 0, 2, 2, 1),
        (1, 2, 1, 0, 1, 2),
        (1, 2, 1, 1, 1, 2),
        (1, 2, 1, 1, 2, 1),
        (1, 2, 1, 3, 1, 2),
        (1, 2, 1, 3, 2, 1),
        (1, 2, 2, 0, 1, 2),
        (1, 2, 2, 2, 1, 2),
        (1, 2, 2, 2, 2, 1),
        (1, 2, 3, 1, 1, 2),
        (1, 2, 3, 3, 0, 3),
        (1, 2, 3, 3, 1, 2),
        (1, 2, 3, 3, 2, 1),
        (2, 1, 0, 0, 1, 2),
        (2, 1, 0, 1, 1, 2),
        (2, 1, 0, 2, 1, 2),
        (2, 1, 1, 1, 1, 2),
        (2, 1, 1, 3, 1, 2),
        (2, 1, 2, 2, 1, 2),
        (2, 1, 3, 3, 0, 3),
        (2, 1, 3, 3, 1, 2),
        (3, 0, 3, 3, 0, 3),
    ]
    for (idx, (b1, b2, b3, b4, b5, b6))  in enumerate(int11Indices):
         _int11[b1, b2, b3, b4, b5, b6] = int11ValuesList[idx]
    _int11 = np.reshape(_int11, (5**6), order = 'C')
    _int11 = list(_int11)[:-1]
    with open(outputFile, "w+", encoding = 'utf-8') as fd:
        for (idx, int11Value) in enumerate(_int11):
            if idx > 0 and idx % 24 == 0:
                fd.write('\n')
            columnStr = "{0}".format(_int11[idx]).ljust(8)
            fd.write(columnStr)
        ##
    return True
##

def InitInt21File(int21ValuesList, outputFile):
    _int21 = np.array([ "inf" for idx in range(0, 5**7) ])
    _int21 = np.reshape(_int21, (5, 5, 5, 5, 5, 5, 5), order = 'C')
    int21Indices = [
        (1, 2, 0, 0, 1, 2, 0),
        (1, 2, 0, 0, 1, 2, 1),
        (1, 2, 0, 0, 1, 2, 2),
        (1, 2, 0, 1, 1, 2, 0),
        (1, 2, 0, 1, 1, 2, 1),
        (1, 2, 0, 1, 1, 2, 2),
        (1, 2, 0, 2, 1, 2, 0),
        (1, 2, 0, 2, 1, 2, 1),
        (1, 2, 0, 2, 1, 2, 2),
        (1, 2, 1, 0, 1, 2, 0),
        (1, 2, 1, 0, 1, 2, 1),
        (1, 2, 1, 0, 1, 2, 3),
        (1, 2, 1, 1, 1, 2, 0),
        (1, 2, 1, 1, 1, 2, 1),
        (1, 2, 1, 1, 1, 2, 3),
        (1, 2, 1, 3, 1, 2, 0),
        (1, 2, 1, 3, 1, 2, 1),
        (1, 2, 1, 3, 1, 2, 3),
        (1, 2, 2, 0, 1, 2, 0),
        (1, 2, 2, 0, 1, 2, 2),
        (1, 2, 2, 2, 1, 2, 0),
        (1, 2, 2, 2, 1, 2, 2),
        (1, 2, 3, 1, 1, 2, 1),
        (1, 2, 3, 1, 1, 2, 3),
        (1, 2, 3, 3, 1, 2, 1),
        (1, 2, 3, 3, 1, 2, 3),
        (2, 1, 0, 0, 2, 1, 0),
        (2, 1, 0, 0, 2, 1, 1),
        (2, 1, 0, 0, 2, 1, 2),
        (2, 1, 0, 1, 2, 1, 0),
        (2, 1, 0, 1, 2, 1, 1),
        (2, 1, 0, 1, 2, 1, 2),
        (2, 1, 0, 2, 2, 1, 0),
        (2, 1, 0, 2, 2, 1, 1),
        (2, 1, 0, 2, 2, 1, 2),
        (2, 1, 1, 0, 2, 1, 0),
        (2, 1, 1, 0, 2, 1, 1),
        (2, 1, 1, 0, 2, 1, 3),
        (2, 1, 1, 1, 2, 1, 0),
        (2, 1, 1, 1, 2, 1, 1),
        (2, 1, 1, 1, 2, 1, 3),
        (2, 1, 1, 3, 2, 1, 0),
        (2, 1, 1, 3, 2, 1, 1),
        (2, 1, 1, 3, 2, 1, 3),
        (2, 1, 2, 0, 2, 1, 0),
        (2, 1, 2, 0, 2, 1, 2),
        (2, 1, 2, 2, 2, 1, 0),
        (2, 1, 2, 2, 2, 1, 2),
        (2, 1, 3, 1, 2, 1, 1),
        (2, 1, 3, 1, 2, 1, 3),
        (2, 1, 3, 3, 2, 1, 1),
        (2, 1, 3, 3, 2, 1, 3),
    ]
    for (idx, (b1, b2, b3, b4, b5, b6, b7))  in enumerate(int21Indices):
         _int21[b1, b2, b3, b4, b5, b6, b7] = int21ValuesList[idx]
    _int21 = np.reshape(_int21, (5**7), order = 'C')
    _int21 = list(_int21)[:-5]
    with open(outputFile, "w+", encoding = 'utf-8') as fd:
        for (idx, int21Value) in enumerate(_int21):
            if idx > 0 and idx % 24 == 0:
                fd.write('\n')
            columnStr = "{0}".format(_int21[idx]).ljust(8)
            fd.write(columnStr)
        ##
    return True
##

def InitInt22File(int22ValuesList, outputFile):
    _int22 = np.array([ "inf" for idx in range(0, 5**8) ])
    _int22 = np.reshape(_int22, (5, 5, 5, 5, 5, 5, 5, 5), order = 'C')
    int22Indices = [
        (0, 3, 0, 0, 3, 0, 0, 0),
        (0, 3, 0, 1, 3, 0, 1, 0),
        (0, 3, 0, 2, 3, 0, 2, 0),
        (0, 3, 1, 0, 3, 0, 0, 1),
        (0, 3, 1, 1, 3, 0, 1, 1),
        (0, 3, 1, 3, 3, 0, 3, 1),
        (0, 3, 2, 0, 3, 0, 0, 2),
        (0, 3, 2, 2, 3, 0, 2, 2),
        (0, 3, 2, 3, 3, 0, 3, 2),
        (0, 3, 3, 1, 3, 0, 1, 3),
        (0, 3, 3, 2, 3, 0, 2, 3),
        (0, 3, 3, 3, 3, 0, 3, 3),
        (1, 2, 0, 0, 2, 1, 0, 0),
        (1, 2, 0, 1, 2, 1, 1, 0),
        (1, 2, 0, 2, 2, 1, 2, 0),
        (1, 2, 1, 0, 2, 1, 0, 1),
        (1, 2, 1, 1, 2, 1, 1, 1),
        (1, 2, 1, 3, 2, 1, 3, 1),
        (1, 2, 2, 0, 2, 1, 0, 2),
        (1, 2, 2, 2, 2, 1, 2, 2),
        (1, 2, 2, 3, 2, 1, 3, 2),
        (1, 2, 3, 1, 2, 1, 1, 3),
        (1, 2, 3, 2, 2, 1, 2, 3),
        (1, 2, 3, 3, 2, 1, 3, 3),
        (2, 1, 0, 0, 1, 2, 0, 0),
        (2, 1, 0, 1, 1, 2, 1, 0),
        (2, 1, 0, 2, 1, 2, 2, 0),
        (2, 1, 1, 0, 1, 2, 0, 1),
        (2, 1, 1, 1, 1, 2, 1, 1),
        (2, 1, 1, 3, 1, 2, 3, 1),
        (2, 1, 2, 0, 1, 2, 0, 2),
        (2, 1, 2, 2, 1, 2, 2, 2),
        (2, 1, 2, 3, 1, 2, 3, 2),
        (2, 1, 3, 1, 1, 2, 1, 3),
        (2, 1, 3, 2, 1, 2, 2, 3),
        (2, 1, 3, 3, 1, 2, 3, 3),
        (3, 0, 0, 0, 0, 3, 0, 0),
        (3, 0, 0, 1, 0, 3, 1, 0),
        (3, 0, 0, 2, 0, 3, 2, 0),
        (3, 0, 1, 0, 0, 3, 0, 1),
        (3, 0, 1, 1, 0, 3, 1, 1),
        (3, 0, 1, 3, 0, 3, 3, 1),
        (3, 0, 2, 0, 0, 3, 0, 2),
        (3, 0, 2, 2, 0, 3, 2, 2),
        (3, 0, 2, 3, 0, 3, 3, 2),
        (3, 0, 3, 1, 0, 3, 1, 3),
        (3, 0, 3, 2, 0, 3, 2, 3),
        (3, 0, 3, 3, 0, 3, 3, 3),
    ]
    for (idx, (b1, b2, b3, b4, b5, b6, b7, b8))  in enumerate(int22Indices):
         _int22[b1, b2, b3, b4, b5, b6, b7, b8] = int22ValuesList[idx]
    _int22 = np.reshape(_int22, (5**8), order = 'C')
    _int22 = list(_int22)[:-1]
    with open(outputFile, "w+", encoding = 'utf-8') as fd:
        for (idx, int22Value) in enumerate(_int22):
            if idx > 0 and idx % 16 == 0:
                fd.write('\n')
            columnStr = "{0}".format(_int22[idx]).ljust(8)
            fd.write(columnStr)
        ##
    return True
##

def InitDangleFile(dangleTuplesList, outputFile):
    _dangle = np.array([ "inf" for idx in range(0, 2 * (4**3)) ])
    _dangle = np.reshape(_dangle, (4, 4, 4, 2), order = 'C')
    dangleTupleIndices = [
        (0, 3, 0),
        (0, 3, 1),
        (0, 3, 2),
        (0, 3, 3),
        (1, 2, 0),
        (1, 2, 1),
        (1, 2, 2),
        (1, 2, 3),
        (2, 1, 0),
        (2, 1, 1),
        (2, 1, 2),
        (2, 1, 3),
        (2, 3, 0),
        (2, 3, 1),
        (2, 3, 2),
        (2, 3, 3),
        (3, 0, 0),
        (3, 0, 1),
        (3, 0, 2),
        (3, 0, 3),
        (3, 2, 0),
        (3, 2, 1),
        (3, 2, 2),
    ]
    for (idx, (d1, d2, d3)) in enumerate(dangleTupleIndices):
        (dtop, dbot) = dangleTuplesList[idx]
        _dangle[d1, d2, d3, 0] = dbot
        _dangle[d1, d2, d3, 1] = dtop
    _dangle = np.reshape(_dangle, (128), order = 'C')
    _dangle = list(_dangle)
    with open(outputFile, "w+", encoding = 'utf-8') as fd:
        for idx in range(0, 128):
            if idx > 0 and idx % 16 == 0:
                fd.write('\n')
            dangleValueStr = "{0}".format(_dangle[idx]).ljust(8)
            fd.write(dangleValueStr)
        ##
    return True
##

def InitLoopFile(loopValuesList, outputFile):
    [ _internal_penalty_by_size, _buldge_penalty_by_size, _hairpin_penalty_by_size ] = loopValuesList
    with open(outputFile, "w+", encoding = 'utf-8') as fd:
        for idx in range(1, 31):
             idxStr = "{0}".format(idx).ljust(8)
             interStr = "{0}".format(_internal_penalty_by_size[idx - 1]).ljust(8)
             bulgeStr = "{0}".format(_buldge_penalty_by_size[idx - 1]).ljust(8)
             hairpinStr = "{0}".format(_hairpin_penalty_by_size[idx - 1]).ljust(8)
             fd.write(idxStr + interStr + bulgeStr + hairpinStr + '\n')
    return True
##

def InitTLoopFile(tloopValuesList, outputFile):
     prefixBases = [
          "CUACGG", 
          "CUCCGG", 
          "CUUCGG", 
          "CUUUGG", 
          "CCAAGG", 
          "CCCAGG",
          "CCGAGG",
          "CCUAGG",
          "CCACGG",
          "CCGCGG",
          "CCUCGG",
          "CUAAGG",
          "CUCAGG",
          "CUUAGG",
          "CUGCGG",
          "CAACGG", 
     ]
     with open(outputFile, "w+", encoding = 'utf-8') as fd:
         for (idx, tloopEnergy) in enumerate(tloopValuesList):
             if idx >= len(prefixBases):
                 break
             fd.write(prefixBases[idx] + "   " + "{0}\n".format(tloopEnergy))
     return True
##

def InitMiscLoopFile(miscLoopDict, outputFile):
    miscLoopFileValues = [
         ('UseExactValue', [1.079]), 
         ('UseExactValue', [3.0]), 
         ('UseExactValue', [0.6, 0.6, 0.6, 0.6]), 
         ('UseDictValue',  ['multi_offset', 'multi_free_base_penalty', 'multi_helix_penalty']), 
         ('UseExactValue', [9.3, 0.0, -0.6]), 
         ('UseExactValue', [0.9]), 
         ('UseExactValue', [3.1]), 
         ('UseDictValue',  ['terminal_AU_penalty']), 
         ('UseDictValue',  ['hairpin_GGG']), 
         ('UseDictValue',  ['hairpin_c1']), 
         ('UseDictValue',  ['hairpin_c2']), 
         ('UseDictValue',  ['hairpin_c3']), 
         ('UseDictValue',  ['intermolecular_initiation']), 
    ]
    with open(outputFile, "w+", encoding = 'utf-8') as fd:
        for (parseKey, valueLst) in miscLoopFileValues:
            for lvalue in valueLst:
                columnStrValue = "".ljust(8)
                if parseKey == 'UseExactValue':
                    columnStrValue = "{0}".format(lvalue).ljust(8)
                elif parseKey == 'UseDictValue':
                    columnStrValue = "{0}".format(miscLoopDict[lvalue]).ljust(8)
                fd.write(columnStrValue)
            fd.write('\n')
        ##
    ##
    return True
##

def MainRunner(paramsFile, outputDir):
    with open(paramsFile, encoding = 'utf-8') as fd:
        # Populate "stack.DAT":
        _stackPresetValuesLst = []
        for lineIdx in range(0, 21):
            floatValueLine = fd.readline().rstrip()
            _stackPresetValuesLst.append(floatValueLine)
        # Populate "tstackh.DAT":
        _tstackhPresetValuesLst = []
        for lineIdx in range(0, 96):
            floatValueLine = fd.readline().rstrip()
            _tstackhPresetValuesLst.append(floatValueLine)
        # Start accounting of misc.* values:
        _misc = dict()
        _misc['internal_AU_closure']  = fd.readline().rstrip()
        _misc['internal_AG_mismatch'] = fd.readline().rstrip()
        _misc['internal_UU_mismatch'] = fd.readline().rstrip()
        # Populate "int11.DAT":
        _int11PresetValuesLst = []
        for lineIdx in range(0, 31):
            floatValueLine = fd.readline().rstrip()
            _int11PresetValuesLst.append(floatValueLine)
        # More misc.* values:
        _misc['internal11_basic_mismatch'] = fd.readline().rstrip()
        _misc['internal11_GG_mismatch']    = fd.readline().rstrip()
        # Populate "int21.DAT":
        _int21PresetValuesLst = []
        for lineIdx in range(0, 52):
             _int21PresetValuesLst.append( fd.readline().rstrip() )
        # More misc.* values:
        _misc['internal21_match']      = fd.readline().rstrip()
        _misc['internal21_AU_closure'] = fd.readline().rstrip()
        # Populate "int22.DAT":
        _int22PresetValuesLst = []
        for lineIdx in range(0, 48):
             _int22PresetValuesLst.append( fd.readline().rstrip() )
        # More misc.* values:
        _misc['internal22_delta_same_size']         = fd.readline().rstrip()
        _misc['internal22_delta_different_size']    = fd.readline().rstrip()
        _misc['internal22_delta_1stable_1unstable'] = fd.readline().rstrip()
        _misc['internal22_delta_AC']                = fd.readline().rstrip()
        _misc['internal22_match']                   = fd.readline().rstrip()
        # Populate "dangle.DAT":
        _dangleTopPresetValuesLst, _dangleBottomPresetValuesLst = [], []
        for lineIdx in range(0, 24):
            _dangleTopPresetValuesLst.append( fd.readline().rstrip() )
        for lineIdx in range(0, 24):
            _dangleBottomPresetValuesLst.append( fd.readline().rstrip() )
        _danglePresetTuplesLst = list(zip(_dangleTopPresetValuesLst, _dangleBottomPresetValuesLst))
        # Define some more arrays:
        _internal_penalty_by_size = [ "inf" for idx in range(0, 31) ]
        for lineIdx in range(4, 7):
            _internal_penalty_by_size[lineIdx] = fd.readline().rstrip()
        _bulge_penalty_by_size = [ "inf" for idx in range(0, 31) ]
        for lineIdx in range(1, 7):
            _bulge_penalty_by_size[lineIdx] = fd.readline().rstrip()
        _hairpin_penalty_by_size = [ "inf" for idx in range(0, 31) ]
        for lineIdx in range(3, 10):
            _hairpin_penalty_by_size[lineIdx] = fd.readline().rstrip()
        # More misc.* values:
        _misc['terminal_AU_penalty']       = fd.readline().rstrip()#
        _misc['hairpin_GGG']               = fd.readline().rstrip()#
        _misc['hairpin_c1']                = fd.readline().rstrip()#
        _misc['hairpin_c2']                = fd.readline().rstrip()#
        _misc['hairpin_c3']                = fd.readline().rstrip()#
        _misc['multi_offset']              = fd.readline().rstrip() # multibranched loops
        _misc['multi_helix_penalty']       = fd.readline().rstrip() # multibranched loops
        _misc['multi_free_base_penalty']   = fd.readline().rstrip() # multibranched loops
        _misc['intermolecular_initiation'] = fd.readline().rstrip() #
        # Populate "tloop.DAT":
        _tloopPresetValuesLst = []
        for lineIdx in range(0, 30):
            readLine = fd.readline()
            if readLine == "":
                break
            _tloopPresetValuesLst.append(readLine.rstrip())
        fd.close()
        ## NOW ... Write all of the files:
        InitStackFile(_stackPresetValuesLst, outputDir + "/stack.DAT")
        InitTStackHFile(_tstackhPresetValuesLst, outputDir + "/tstackh.DAT")
        InitInt11File(_int11PresetValuesLst, outputDir + "/int11.DAT")
        InitInt21File(_int21PresetValuesLst, outputDir + "/int21.DAT")
        InitInt22File(_int22PresetValuesLst, outputDir + "/int22.DAT")
        InitDangleFile(_danglePresetTuplesLst, outputDir + "/dangle.DAT")
        InitLoopFile([ _internal_penalty_by_size, _bulge_penalty_by_size, _hairpin_penalty_by_size ], outputDir + "/loop.DAT")
        InitTLoopFile(_tloopPresetValuesLst, outputDir + "/tloop.DAT")
        InitMiscLoopFile(_misc, outputDir + "/miscloop.DAT")
    ##
    return 0
##

def GetAbsolutePathRelativeToScript(relPath):
    return os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), relPath))
##

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise ValueError("Usage: python3 CreateEnergyModelDataSet.py <FM363-TURNER-PARAMTYPES-PARAMS-FILE> <RELATIVE-OUTPUT-DIR>")
    paramsFile = GetAbsolutePathRelativeToScript(sys.argv[1])
    outputDir  = GetAbsolutePathRelativeToScript(sys.argv[2])
    sys.exit(MainRunner(paramsFile, outputDir))
##
