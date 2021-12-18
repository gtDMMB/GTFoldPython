#### GTFoldPythonUtils.py : Utility and helper functions 
#### Author: Maxie D. Schmidt (maxieds@gmail.com)
#### Created: 2020.02.06

import os
from GTFoldPython import GTFoldPython

class GTFoldPythonUtils(object):

    @staticmethod
    def Constraint(consType, i, j, k):
        """Constructs a constraint list
        :param consType: Constraint type, either F or P
        :param i: Constraint spec (int)
        :param j: Constraint spec (int)
        :param k: Constraint spec (int)
        :return: A list [consType, i, j, k]
        :rtype: List
        """
        return [consType, i, j, k]
    ##

    @staticmethod
    def ForcedConstraint(i, j, k):
        """Constructs a forced constraint from component parameters"""
        return GTFoldPythonUtils.Constraint(GTFoldPython.F, i, j, k)
    ##

    @staticmethod
    def ProhibitedConstraint(i, j, k):
        """Constructs a prohibited constraint from component parameters"""
        return GTFoldPythonUtils.Constraint(GTFoldPython.P, i, j, k)
    ##

    @staticmethod
    def SHAPEConstraint(basePair, shape):
        """Constructs a SHAPE constraint from component parameters"""
        return [ basePair, shape ]
    ##

    @staticmethod
    def GetFPConstraintsFromString(consStr):
        consList = []
        unpairedStack = []
        for (idx, consCh) in enumerate(consStr):
             if consCh == ".":
                 pass
             elif consCh == 'x':
                 consList.append( GTFoldPythonUtils.ProhibitedConstraint(idx + 1, 0, 1) )
             elif consCh == "(":
                 unpairedStack.append(idx + 1)
             elif consCh == ")":
                 if len(unpairedStack) == 0:
                     raise ValueError("Unmatched () values in constraints string at position {0}".format(idx + 1))
                 pairIdxI = unpairedStack[-1]
                 unpairedStack = unpairedStack[:-1]
                 #consList.append( GTFoldPythonUtils.ForcedConstraint(pairIdxI, idx + 1, 1) )
                 consList.append( GTFoldPythonUtils.ForcedConstraint(pairIdxI, idx + 1, idx + 2 - pairIdxI) )
             elif consCh == ">":
                 consList.append( GTFoldPythonUtils.ProhibitedConstraint(1, 0, idx + 1) )
                 consList.append( GTFoldPythonUtils.ForcedConstraint(idx + 1, 0, 1) )
             elif consCh == "<":
                 consList.append( GTFoldPythonUtils.ProhibitedConstraint(idx + 1, 0, len(consStr) + 1) )
                 consList.append( GTFoldPythonUtils.ForcedConstraint(idx + 1, 0, 1) )
             elif consCh == "|":
                 consList.append( GTFoldPythonUtils.ForcedConstraint(idx + 1, 0, 1) )
             else:
                 raise SyntaxError("Unknown constraint spec character \"{0}\" at position {1}".format(consCh, idx + 1))
        ##
        if len(unpairedStack) > 0:
            raise ValueError("Unmatched values () in constraints string")
        return consList
    ##

    @staticmethod
    def ReadFPConstraintsFromFile(fileNamePath):
        """Reads F(orced)/P(rohibited) type constraints in from a formatted file 
           Constraint syntax
           The constraints given in constraint file should be formated as follows:
           P i j k      Prohibits the formation of base pairs (i,j) (i+1,j-1) ... (i+k-1, j-k+1).
           F i j k      Forces the formation of base pairs (i,j) (i+1,j-1) ... (i+k-1, j-k+1).
           P i 0 k      Makes the bases from i to i+k-1 single stranded bases.
           F i 0 k      Forces the bases from i to i+k-1 to be paired 
                        (without specifying their pairing parterns). (Beta option)
           Note that k must be positive, and j-i must be at least 4.
        """
        absFilePath = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), fileNamePath))
        if not os.path.exists(absFilePath) or os.path.isdir(absFilePath):
             raise FileNotFoundError(absFilePath)
        consList = [ ]
        try:
            consFP = open(absFilePath, 'r')
            for (lineNo, lineText) in enumerate(consFP):
                if len(lineText) > 0 and lineText[0] == '>':
                    continue
                lineText = lineText.rstrip()
                if len(lineText) == 0:
                    continue
                consParams = lineText.split(' ')
                if len(consParams) not in [3, 4] or consParams[0] not in ["F", "P"]:
                    raise SyntaxError("Invalid constraint syntax on line #{0}: \"{1}\" ... ".format(lineNo, lineText))
                curCons = GTFoldPython.F if consParams[0] == "F" else GTFoldPython.P
                (i, j, k) = consParams[1:] if len(consParams) == 4 else (consParams[1], 0, consParams[2])
                (i, j, k) = (int(i), int(j), int(k))
                #print([curCons, i, j, k])
                #if k <= 0 or abs(j - i) < 4:
                #    raise SyntaxError("Invalid constraint values on line #{0}: \"{1}\" ... ".format(lineNo, lineText))
                #curCons.extend([i, j, k])
                consList.append([ curCons, i, j, k ])
            ##
        #except Exception:
        #    consFP.close()
        #    raise Exception
        finally:
            consFP.close()
        return consList
    ##

    @staticmethod
    def ReadSHAPEConstraintsFromFile(fileNamePath):
        """Reads SHAPE style constraints from a formatted file 
           For file format specs, see: 
           http://rna.urmc.rochester.edu/Releases/5.8/manual/Text/File_Formats.html#SHAPE

           SHAPE values should be given in a file with two single-space-delimited columns, 
           for example:
           --------
           1 0.1
           2 0.001
           3 1.67
           etc.,
           --------
           where the first column is the nucleotide position (INT) and the second column is the 
           SHAPE reactivity[1] (DOUBLE) for that position. The file should have no header. Not all 
           positions need to be included in the file, and the values do not need to be in order of 
           increasing position. Negative SHAPE reactivities are ignored.
        """
        absFilePath = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), fileNamePath))
        if not os.path.exists(absFilePath) or os.path.isdir(absFilePath):
             raise FileNotFoundError(absFilePath)
        consList = [ ]
        try:
            consFP = open(absFilePath, 'r')
            for (lineNo, lineText) in enumerate(consFP):
                if len(lineText) > 0 and lineText[0] == '>':
                    continue
                lineText = lineText.rstrip()
                if len(lineText) == 0:
                    continue
                consParams = lineText.split(' ')
                if len(consParams) != 2:
                    raise SyntaxError("Invalid SHAPE constraint on line #{0} in \"{1}\" ... ".format(lineNo, fileNamePath))
                curCons = [ typeFunc(param) for (param, typeFunc) in \
                            zip(consParams, [ lambda x: int(x), lambda x: float(x) ]) ]
                consList.append(curCons)
            ##
        #except exObj:
        #    consFP.close()
        #    raise exObj
        finally:
            consFP.close()
        return consList
    ##

    @staticmethod
    def ReadConstraintsFromFile(fileNamePath, isFPConstraints = False, isSHAPEConstraints = False):
         """Read constraints from file (tries to auto-detect type of constraints file)"""
         if isFPConstraints:
             return GTFoldPythonUtils.ReadFPConstraintsFromFile(fileNamePath)
         elif isSHAPEConstraints:
             return GTFoldPythonUtils.ReadSHAPEConstraintsFromFile(fileNamePath)
         elif not os.path.exists(fileNamePath) and not os.path.isdir(fileNamePath):
             raise FileNotFoundError
         (fileBaseName, fileExt) = os.path.splitext(fileNamePath)
         if fileExt.lower().find('shape'):
             return GTFoldPythonUtils.ReadSHAPEConstraintsFromFile(fileNamePath)
         else:
             return GTFoldPythonUtils.ReadFPConstraintsFromFile(fileNamePath)
    ##

    @staticmethod
    def DOTStructToPairsList(dotStruct, includeNonPaired = False, nonPairedMarker = -1, includeSymmetricPairs = True):
        """Generate a list of pair tuples from a DOT(Bracket) structure string
           - includeNonPaired:      [BOOL] Whether to include bases with no pairs in the returned list
           - nonPairedMarker:       [INT]  What to call the pairs for non-paired (default: -1)
           - includeSymmetricPairs: [BOOL] Whether to include symmetric pairs in the returned list, e.g., only 
                                           (1, 2) versus both (1, 2) and (2, 1)
        """
        retPairsList = [ ]
        unpairedStack = [ ]
        for (pidx, pairCh) in enumerate(str(dotStruct)):
            if pairCh == "." and includeNonPaired:
                retPairsList.extend( (pidx + 1, nonPairedMarker) )
            elif pairCh == "(":
                unpairedStack.extend(pidx + 1)
            elif pairCh == ")" and len(unpairedStack) > 0:
                pairIdx = unpairedStack[-1]
                unpairedStack = unpairedStack[:-1]
                if not includeSymmetricPairs:
                    retPairsList.extend([ (pidx + 1, pairIdx) ])
                else:
                    retPairsList.extend([ (pidx + 1, pairIdx), (pairIdx, pidx + 1) ])
            else:
                raise SyntaxError("Parsing DOT structure \"... {0} ... \" at position index #{1}".format(
                    dotStruct[min(0, pidx - 8):max(len(dotStruct - 1), pidx + 8)], pidx))
        ##
        if len(unpairedStack) > 0:
            raise SyntaxError("DOT structure has more open pair characters than closed pair characters ... ")
        sortCompareFunc = lambda i, j: i
        return list(retPairsList).sort(key = sortCompareFunc)
    ## 

    @staticmethod
    def ParseFASTAFile(fastaFilePath, baseSeqToUpper = False):
        """Parse a FASTA file, and return the base sequence it contains:

           FASTA (Sequence File) Format
           For FASTA files, the first line, a title line, needs to start with ">". 
           Subsequent lines should only contain sequence and whitespace, which is ignored. 
           Lowercase nucleotides will be forced single stranded in structure prediction.
           
           Example / Sample FASTA file:
           --------
           >Title of Sequence
           AAA GCGG UUTGTT UTCUTaaTCTXXXXUCAGG
           UUA GCCG UUTGTT UTCUTaaTCTGGG
           --------
        """
        if not os.path.exists(fastaNamePath) or os.path.isdir(fastaNamePath):
             raise FileNotFoundError(fileNamePath)
        baseSeqList = [ ]
        try:
            fastaFP = open(fastaFilePath, 'r')
            for (lineNo, lineText) in enumerate(fastaFP):
                lineText = lineText.rstrip().replace(" ", "")
                if len(lineText) == 0:
                    continue
                elif lineText[0] == ">":
                    continue
                if baseSeqToUpper:
                    lineText = str(lineText).upper()
                if any(ch not in 'ACGTUXNacgtuxn' for ch in lineText):
                    raise SyntaxError("Invalid nucleotide char specified on line #{0}: {1}".format(lineNo, lineText))
                baseSeqList.append(lineText)
        except exObj:
            fastaFP.close()
            raise exObj
        finally:
            fastaFP.close()
        return baseSeqList
    ##

    @staticmethod
    def ParseCTFile(cfFilePath):
        """Parse the base sequence and dot pairing structure in from (NOP)CT file

           CT File Format
           A CT (Connectivity Table) file contains secondary structure information 
           for a sequence. These files are saved with a CT extension. When entering 
           a structure to calculate the free energy, the following format must be followed.
           1. Start of first line: number of bases in the sequence
           2. End of first line: title of the structure
           3. Each of the following lines provides information about a given base in the 
              sequence. Each base has its own line, with these elements in order:
              * Base number: index n
              * Base (A, C, G, T, U, X)
              * Index n-1
              * Index n+1
              * Number of the base to which n is paired. No pairing is indicated by 0 (zero).
              * Natural numbering. RNAstructure ignores the actual value given in natural 
                numbering, so it is easiest to repeat n here.
           The CT file may hold multiple structures for a single sequence. This is done by repeating the 
           format for each structure without any blank lines between structures.
        """
        raise NotImplementedError
    ##

    @staticmethod
    def ParseDOTBracketFile(dotFilePath):
        """Parse the base sequence and dot pairing structure in from DOT(Bracket) file

           Dot bracket files are plain text. They encode a sequence and secondary structure. 
           The first line starts with a ">" character and a file title follows. 
           The next line contains the sequence. The final line contains "." (unpaired nucleotide), 
           "(" (nucleotide that is 5' in a pair), and ")" (nucleotide that is 3' in a pair.

           SAMPLE DOT BRACKET FILE EXAMPLE:
           --------
           >  A stem-loop structure
           GGGCGAAUUGGGUACCGGGCCC
           ((((...((((...))))))))
           --------
        """
        raise NotImplementedError
    ## 

##
