# GTFoldPython.py : Python code wrapper around the shared C library functionality
# included using the ctypes module;
# Author: Maxie D. Schmidt (maxieds@gmail.com)
# Created: 2020.01.23

from _ctypes import dlopen as __dlopen
from _ctypes import dlclose as __dlclose
import ctypes
from ctypes import POINTER, pointer
import os

from GTFoldPythonConfig import GTFoldPythonConfig as GTFPConfig
from GTFoldPythonCTypes import GTFoldPythonCTypes as GTFPTypes

class GTFoldPython:
    """
    GTFoldPython : defines an interface for calling the GTFold C library functions
    """

    # Static definitions and initialization:
    F = int(0x01010101)
    P = int(0x00000000)

    _libGTFoldIsInit = False
    _libGTFoldHandle = None

    _configQuiet = 0
    _configVerbose = 0
    _configDebugging = 0
    _configStdMsgOut = "stderr"
    _configExtraSettingsDict = dict([])
    _configDataDir = ""
    _configEnergyModelName = GTFPConfig.THERMO_PARAMS_SPEC_TURNER04
    _configEnergyModelDataDir = None
    _configDangle = 0
    _configTerminalMismatch = False
    _configLimitContactDistance = 0
    _configPrefilter = 0

    # Static helper methods:
    @staticmethod
    def _WrapCTypesFunction(funcname, restype=None, argtypes=None):
        """Simplify wrapping ctypes functions"""
        func = GTFoldPython._libGTFoldHandle.__getattr__(funcname)
        if restype != None:
            func.restype = restype
        if argtypes != None:
            func.argtypes = argtypes
        return func
    ##

    @staticmethod
    def _ConstructLibGTFold(reinit = False):
        """Run this before calling any LibGTFold methods"""
        if not GTFoldPython._libGTFoldIsInit or reinit:
            #if reinit: GTFoldPython._CloseCTypesLibrary()
            if GTFoldPython._libGTFoldHandle == None or reinit:
                if GTFPConfig.PLATFORM_DARWIN:
                    GTFoldPython._libGTFoldHandle = ctypes.cdll.LoadLibrary("GTFoldPython.dylib")
                else:
                    GTFoldPython._libGTFoldHandle = ctypes.PyDLL(
                            "GTFoldPython.so", 
                            mode = ctypes.RTLD_GLOBAL, 
                            use_errno = True
                    )
            GTFoldPython._libGTFoldHandle.GTFoldPythonInit()
            GTFoldPython._libGTFoldIsInit = True
            if reinit:
                #GTFoldPython.Config(
                #        quiet=GTFoldPython._configQuiet,
                #        verbose=GTFoldPython._configVerbose,
                #        debugging=GTFoldPython._configDebugging,
                #        stdmsgout=GTFoldPython._configStdMsgOut
                #)
                if GTFoldPython._configDataDir != '':
                    GTFoldPython.SetGTFoldDataDirectory(GTFoldPython._configDataDir)
                if GTFoldPython._configEnergyModelName != None:
                    GTFoldPython.SetThermodynamicParameters(
                            GTFoldPython._configEnergyModelName, 
                            GTFoldPython._configEnergyModelDataDir
                    )
                if GTFoldPython._configDangle != None:
                    GTFoldPython.SetDangleParameter(GTFoldPython._configDangle)
                if GTFoldPython._configTerminalMismatch != None:
                    GTFoldPython.SetTerminalMismatch(GTFoldPython._configTerminalMismatch)
                if GTFoldPython._configLimitContactDistance != None:
                    GTFoldPython.SetLimitContactDistance(GTFoldPython._configLimitContactDistance)
                if GTFoldPython._configPrefilter != None:
                    GTFoldPython.SetPrefilterParameter(GTFoldPython._configPrefilter)
                GTFoldPython.ConfigExtraSettings(GTFoldPython._configExtraSettingsDict)
        ##
    ##

    @staticmethod
    def _CloseCTypesLibrary():
        if False and GTFoldPython._libGTFoldHandle != None:
            OS_PLATFORM = platform.system()
            dlCloseFunc = __dlclose
            try:
                if OS_PLATFORM == "Windows":
                    dlCloseFunc = ctypes.windll.kernel32.FreeLibrary
                elif OS_PLATFORM == "Darwin":
                    try:
                        try:
                            # MacOS 11 -- Big Sur: 
                            stdlib = ctypes.CDLL("libc.dylib")
                        except OSError:
                            stdlib = ctypes.CDLL("libSystem")
                    except OSError:
                        try:
                            stdlib = ctypes.CDLL("/usr/lib/system/libsystem_c.dylib")
                        except OSError:
                            stdlib = ctypes.CDLL(None)
                            #GTFoldPython._libGTFoldHandle
                    dlCloseFunc = stdlib.dlclose
                elif OS_PLATFORM == "Linux":
                    try:
                        stdlib = ctypes.CDLL("")
                    except OSError:
                        stdlib = ctypes.CDLL("libc.so")
                    dlCloseFunc = stdlib.dlclose
                elif OS_PLATFORM == "msys":
                    stdlib = ctypes.CDLL("msys-2.0.dll")
                    dlCloseFunc = stdlib.dlclose
                elif OS_PLATFORM == "cygwin":
                    stdlib = ctypes.CDLL("cygwin1.dll")
                    dlCloseFunc = stdlib.dlclose
                elif OS_PLATFORM == "FreeBSD":
                    stdlib = ctypes.CDLL("libc.so.7")
                    dlCloseFunc = stdlib.dlclose
            except OSError:
                dlCloseFunc = __dlclose
            dlCloseFunc.argtypes = [ ctypes.c_void_p ]
            dlCloseFunc.restype = ctypes.c_int
            dlCloseFunc(GTFoldPython._libGTFoldHandle._handle)
            del GTFoldPython._libGTFoldPython
            GTFoldPython._libGTFoldHandle = None
            GTFoldPython._libGTFoldIsInit = False
    ##

    # The actual interface for users:
    @staticmethod
    def Init(reinitLibrary = False):
        """Initialize the LibGTFold instance (C source variables init)"""
        if reinitLibrary:
            pass
            #GTFoldPython._configExtraSettingsDict = {}
            #GTFoldPython._configQuiet = 0
            #GTFoldPython._configVerbose = 0
            #GTFoldPython._configDebugging = 0
            #GTFoldPython._configStdMsgOut = "stderr"
            #GTFoldPython._configDataDir = ""
            #GTFoldPython._configEnergyModelName = GTFPConfig.THERMO_PARAMS_SPEC_TURNER04
            #GTFoldPython._configEnergyModelDataDir = None
            #GTFoldPython._configDangle = 0
            #GTFoldPython._configTerminalMismatch = False
            #GTFoldPython._configLimitContactDistance = 0
            #GTFoldPython._configPrefilter = 0
        GTFoldPython._ConstructLibGTFold(reinitLibrary)
        GTFoldPython.Config(
                quiet=GTFoldPython._configQuiet,
                verbose=GTFoldPython._configVerbose,
                debugging=GTFoldPython._configDebugging,
                stdmsgout=GTFoldPython._configStdMsgOut
        )   
    ##

    @staticmethod
    def Config(quiet=0, verbose=0, debugging=0, stdmsgout="stderr"):
        """Set up global configuration options for running GTFold:
           - quiet 0/1                   : turn on/off printing of messages
           - verbose 0/1                 : turn on/off printing of verbose messages
           - debugging 0/1               : turn on/off printing of extra verbose debugging messages
           - stdmsgout "stderr"|"stdout" : sets default out stream to print messages
        """
        GTFoldPython._configQuiet = quiet
        GTFoldPython._configVerbose = verbose
        GTFoldPython._configDebugging = debugging
        GTFoldPython._configStdMsgOut = stdmsgout
        GTFoldPython._ConstructLibGTFold(False)
        resType = ctypes.py_object
        argTypes = [ctypes.c_int, ctypes.c_int,
                    ctypes.c_int, GTFPTypes.CStringType ]
        libGTFoldFunc = GTFoldPython._WrapCTypesFunction("GTFoldPythonConfig", resType, argTypes)
        return libGTFoldFunc(ctypes.c_int(quiet),
                             ctypes.c_int(verbose),
                             ctypes.c_int(debugging),
                             GTFPTypes.CString(stdmsgout))
    ##

    @staticmethod
    def ConfigExtraSettings(kwargs):
        """Setup misc GTFold options AND hidden developer settings

        :EXAMPLE:
        >>> import GTFoldPythonImportAll
        >>> GTFP.DisplayHelp("Settings")

        :EXAMPLE:
        >>> import GTFoldPythonImportAll
        >>> cfgSettings = { 
                verbose          : False, 
                quiet            : False, 
                debugging        : False,        
                dangle           : 0,
                tmismatch        : True,
                limitcdist       : -1,
                prefilter        : -1,
                energydetail     : True,
                estimatebpp      : True,
                groupbyfreq      : True,
                outputprefix     : "output_prefix_",
                writeauxfiles    : True,
                numthreads       : 4,
                workdir          : "./output",
                rnafold          : True,
                unafold          : False,
                calcpartition    : True,
                printarrays      : True,
                exactintloop     : True,
                checkfraction    : False,
                dS               : False,
                sampleenergy     : 10.0,
                scale            : 0.75,
                parallelsample   : False,
                countsparallel   : False,
                separatectfiles  : True,
                ctfilesdir       : "./ctfiles",
                summaryfile      : True,
                advancedouble    : 1, 
                bignumprecision  : 512,
                uniquemultiloop  : True,
                duplicatecheck   : True
        };
        >>> GTFP.ConfigSettings(**cfgSettings)
        """
        curConfigDict = GTFoldPython._configExtraSettingsDict
        curConfigDict.update(kwargs)
        GTFoldPython._configExtraSettingsDict = curConfigDict
        GTFoldPython._ConstructLibGTFold(False)
        resType = ctypes.py_object
        argTypes = [ ctypes.py_object ]
        libGTFoldFunc = GTFoldPython._WrapCTypesFunction("GTFoldPythonConfigSettings", resType, argTypes)
        return libGTFoldFunc(GTFoldPython._configExtraSettingsDict)
    ##

    @staticmethod
    def PrintRunConfiguration(printVerboseParams = True):
        """Print the GTFold settings AND local developer-only settings configuration status"""
        GTFoldPython._ConstructLibGTFold(False)
        resType = ctypes.py_object
        argTypes = [ ctypes.c_int ]
        libGTFoldFunc = GTFoldPython._WrapCTypesFunction("PrintGTFoldRunConfiguration", resType, argTypes)
        return libGTFoldFunc(ctypes.c_int(1 if printVerboseParams else 0))
    ##

    @staticmethod
    def SetGTFoldDataDirectory(relDirPath):
        """Sets the GTFold DAT / distribution data location where the path is 
           relative to that of the calling script
           See options: -p, --paramdir DIR
           Also can be set by exporting the env variable GTFOLDDATADIR at runtime
        """
        GTFoldPython._configDataDir = relDirPath
        GTFoldPython._ConstructLibGTFold(False)
        #absDataPath = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), relDirPath)) 
        absDataPath = relDirPath
        resType = ctypes.py_object
        argTypes = [ GTFPTypes.CStringType, ctypes.c_int ]
        libGTFoldFunc = GTFoldPython._WrapCTypesFunction("SetGTFoldDataDirectory", resType, argTypes)
        absDataPathParam = GTFPTypes.CString(absDataPath)
        return libGTFoldFunc(absDataPathParam, len(absDataPath))
    ##

    @staticmethod
    def SetThermodynamicParameters(energyModelName, baseDataDir = None):
        """Sets the energy model data set file names according to 
           predefined supported name 
           (GTFold, RNAFold, UNAFold, Turner99, Turner04, default; 
            -DP03, -DP09, -CC06, -CC09), and optionally sets the data file location 
           directory if the second parameter to the function is not set to None.
           
           To view extensive help on this topic, run the following Python3 code:
           >>> from GTFoldPythonImportAll import *
           >>> DisplayHelp("SetThermodynamicParameters")
        """
        if baseDataDir == None or baseDataDir == '':
            return GTFoldPython.SetThermodynamicParametersFromDefaults(energyModelName)
        GTFoldPython._configEnergyModelName = energyModelName
        GTFoldPython._configEnergyModelBaseDataDir = baseDataDir
        GTFoldPython._ConstructLibGTFold(False)
        resType = ctypes.py_object
        argTypes = [ GTFPTypes.CStringType, GTFPTypes.CStringType ]
        libGTFoldFunc = GTFoldPython._WrapCTypesFunction("SetThermodynamicParameters", resType, argTypes)
        emodelParam = GTFPTypes.CString(energyModelName)
        baseDataDirParam = GTFPTypes.CString(baseDataDir)
        return libGTFoldFunc(emodelParam, baseDataDirParam)
    ##

    @staticmethod
    def SetThermodynamicParametersFromDefaults(energyModelName):
        """Set the energy model data set parameters using the default local directory 
           names for the locations of the data set files.
           ::seealso GTFoldPython.SetThermodynamicParameters
        """
        defaultDataDir = GTFPConfig.GetThermodynamicParametersDirectory(energyModelName, resetDir=True)
        return GTFoldPython.SetThermodynamicParameters(energyModelName, defaultDataDir)
    ##

    @staticmethod
    def SetDangleParameter(dangle):
        """Restricts treatment of dangling energies
           Values of the parameter: 
           INT=0	Ignores dangling energies (mostly for debugging).
           INT=1	Unpaired nucleotides adjacent to a branch in a multi-loop or external loop
                        are allowed to dangle on at most one branch in that loop.
                        This is the default setting for gtmfe.
           INT=2	Dangling energies are added for nucleotides on either side of each branch in 
                        multi-loops and external loops.
                        This is the default setting for gtboltzmann and gtsubopt.
                        (This is the same as the -d2 setting in the RNAfold from the Vienna RNA Package.)
           otherwise	INT is ignored and the default setting is used.

           See options: -d, --dangle INT
        """
        GTFoldPython._configDangle = dangle
        GTFoldPython._ConstructLibGTFold(False)
        resType = ctypes.py_object
        argTypes = [ ctypes.c_int ]
        libGTFoldFunc = GTFoldPython._WrapCTypesFunction("SetDangleParameter", resType, argTypes)
        return libGTFoldFunc(ctypes.c_int(dangle))
    ##

    @staticmethod
    def SetTerminalMismatch(enable):
        """Enable terminal mismatch calculations.
           See the options -m, --mismatch in the GTFold docs
        """
        if type(enable) == bool:
            enable = 1 if enable else 0
        GTFoldPython._configTerminalMismatch = enable
        GTFoldPython._ConstructLibGTFold(False)
        resType = ctypes.py_object
        argTypes = [ ctypes.c_int ]
        libGTFoldFunc = GTFoldPython._WrapCTypesFunction("SetTerminalMismatch", resType, argTypes)
        return libGTFoldFunc(ctypes.c_int(enable))
    ##

    @staticmethod
    def EnableTerminalMismatch():
        return GTFoldPython.SetTerminalMismatch(True)
    ##

    @staticmethod
    def DisableTerminalMismatch():
        return GTFoldPython.SetTerminalMismatch(False)
    ##

    @staticmethod
    def SetLimitContactDistance(lcDist):
        """Set a maximum base pair contact distance to INT. If no limit is given, 
           base pairs can be over any distance.
           See options: -l, --limitcd INT
        """
        GTFoldPython._configLimitContactDist = lcDist
        GTFoldPython._ConstructLibGTFold(False)
        resType = ctypes.py_object
        argTypes = [ ctypes.c_int ]
        libGTFoldFunc = GTFoldPython._WrapCTypesFunction("SetLimitContactDistance", resType, argTypes)
        return libGTFoldFunc(ctypes.c_int(lcDist))
    ##

    @staticmethod
    def SetPrefilterParameter(prefilter):
        """Prohibits any basepair which does not have appropriate neighboring 
           nucleotides such that it could be part of a helix of length INT.
           See options: --prefilter INT
        """
        GTFoldPython._configPrefilter = prefilter
        GTFoldPython._ConstructLibGTFold(False)
        resType = ctypes.py_object
        argTypes = [ ctypes.c_int ]
        libGTFoldFunc = GTFoldPython._WrapCTypesFunction("SetPrefilterParameter", resType, argTypes)
        return libGTFoldFunc(ctypes.c_int(prefilter))
    ##

    @staticmethod
    def GetPFuncCount(baseSeq, consList = []):
        """Output the number of possibles structures (using the partition function)
           See options: --pfcount (with gtboltzmann), -c, --constraints FILE
        """
        GTFoldPython._ConstructLibGTFold()
        resType = ctypes.py_object
        argTypes = [ GTFPTypes.CStringType, GTFPTypes.FPConstraintsListType(consList), 
                     ctypes.c_int ]
        libGTFoldFunc = GTFoldPython._WrapCTypesFunction("GetPFuncCount", resType, argTypes)
        pfCount = libGTFoldFunc(GTFPTypes.CString(baseSeq), GTFPTypes.FPConstraintsList(consList), 
                                len(consList))
        return str(pfCount)
    ##
    
    @staticmethod
    def GetPFuncCountSHAPE(baseSeq, consList = []):
        """Output the number of possibles structures (using the partition function) -- 
           using SHAPE style constraints
           See options: --pfcount (with gtboltzmann), --useSHAPE FILE
        """
        GTFoldPython._ConstructLibGTFold()
        resType = ctypes.py_object
        argTypes = [ GTFPTypes.CStringType, GTFPTypes.SHAPEConstraintsListType(consList), 
                     ctypes.c_int ]
        libGTFoldFunc = GTFoldPython._WrapCTypesFunction("GetPFuncCount", resType, argTypes)
        pfCount = libGTFoldFunc(GTFPTypes.CString(baseSeq), 
                                GTFPTypes.SHAPEConstraintsList(consList), 
                                len(consList))
        return str(pfCount)
    ##

    @staticmethod
    def ComputeBPP(baseSeq, consList = []):
        """Calculate base pair probabilities and unpaired probabilities (Beta feature)
           See options: --bpp (for use with gtboltzmann), -c, --constraints FILE
        """
        GTFoldPython._ConstructLibGTFold()
        resType = ctypes.py_object
        argTypes = [ GTFPTypes.CStringType, GTFPTypes.FPConstraintsListType(consList), 
                     ctypes.c_int ]
        libGTFoldFunc = GTFoldPython._WrapCTypesFunction("ComputeBPP", resType, argTypes)
        bppTuple = libGTFoldFunc(GTFPTypes.CString(baseSeq), GTFPTypes.FPConstraintsList(consList), 
                                 len(consList))
        return [ (int(i), int(j), float(p)) for (i, j, p) in bppTuple ]
   ##

    @staticmethod
    def ComputeBPPSHAPE(baseSeq, consList = []):
        """Calculate base pair probabilities and unpaired probabilities (Beta feature) -- 
           use with with SHAPE style constraints 
           See options: --bpp (for use with gtboltzmann), --useSHAPE FILE
        """
        GTFoldPython._ConstructLibGTFold()
        resType = ctypes.py_object
        argTypes = [ GTFPTypes.CStringType, GTFPTypes.SHAPEConstraintsListType(consList), 
                     ctypes.c_int ]
        libGTFoldFunc = GTFoldPython._WrapCTypesFunction("ComputeBPP", resType, argTypes)
        bppTuple = libGTFoldFunc(GTFPTypes.CString(baseSeq), GTFPTypes.SHAPEConstraintsList(consList), 
                                 len(consList))
        return [ (int(i), int(j), float(p)) for (i, j, p) in bppTuple ]
    ##

    @staticmethod
    def GetMFEStructure(baseSeq, consList = []):
        """Get the MFE and MFE structure (in DOTBracket structure notation)

        :param baseSeq: A string of valid bases (ATGU/X) 
        :param consList: A list of constraints on the MFE structure
        :return: A tuple (MFE as double, MFE structure as string in DOTBracket notation)
        :rtype: tuple
        """
        GTFoldPython._ConstructLibGTFold()
        resType = ctypes.py_object
        argTypes = [ GTFPTypes.CStringType, GTFPTypes.FPConstraintsListType(consList), ctypes.c_int ]
        libGTFoldFunc = GTFoldPython._WrapCTypesFunction("GetMFEStructure", resType, argTypes)
        (mfe, mfeStruct) = libGTFoldFunc(GTFPTypes.CString(baseSeq), GTFPTypes.FPConstraintsList(consList), 
                                         len(consList))
        return (float(mfe), str(mfeStruct))
    ##

    @staticmethod
    def GetMFEStructureSHAPE(baseSeq, shapeConsList = []):
        """Compute the MFE and MFE structure using SHAPE based constraints"""
        GTFoldPython._ConstructLibGTFold()
        resType = ctypes.py_object
        argTypes = [ GTFPTypes.CStringType, GTFPTypes.SHAPEConstraintsListType(shapeConsList), ctypes.c_int ]
        libGTFoldFunc = GTFoldPython._WrapCTypesFunction("GetMFEStructureSHAPE", resType, argTypes)
        baseSeqParam = GTFPTypes.CString(baseSeq)
        shapeConsParam = GTFPTypes.SHAPEConstraintsList(shapeConsList)
        numConsParam = len(shapeConsList)
        (mfe, mfeStruct) = libGTFoldFunc(baseSeqParam, shapeConsParam, numConsParam)
        return (float(mfe), str(mfeStruct))
    ##

    @staticmethod
    def GetSuboptStructures(baseSeq, delta):
        """Compute suboptimal structures within DOUBLE kcal/mole of MFE.
           - Dangle option can only be set to INT=2
           See options: --delta DOUBLE (for use with gtsubopt)
        """
        GTFoldPython._ConstructLibGTFold()
        resType = ctypes.py_object
        argTypes = [ GTFPTypes.CStringType, ctypes.c_double ]
        libGTFoldFunc = GTFoldPython._WrapCTypesFunction("GetSuboptStructuresWithinRange", resType, argTypes)
        structTupleLst = libGTFoldFunc(GTFPTypes.CString(baseSeq), ctypes.c_double(delta))
        structTupleLst = [ (str(struct), int(e)) for (struct, e) in structTupleLst ]
        return structTupleLst
    ##

    @staticmethod
    def SampleBoltzmannStructures(baseSeq, N, consList = []):
        """Sample INT (param N > 0) structures from Boltzmann distribution 
           See options: -s, --sample INT (for use with gtboltzman), -c, --constraints FILE
        """
        GTFoldPython._ConstructLibGTFold()
        resType = ctypes.py_object
        argTypes = [ GTFPTypes.CStringType, GTFPTypes.FPConstraintsListType(consList), 
                     ctypes.c_int, ctypes.c_int ]
        libGTFoldFunc = GTFoldPython._WrapCTypesFunction("SampleBoltzmannStructures", resType, argTypes)
        structTupleLst = libGTFoldFunc(GTFPTypes.CString(baseSeq), GTFPTypes.FPConstraintsList(consList), 
                                       ctypes.c_int(len(consList)), ctypes.c_int(N))
        structTupleLst = [ (float(ep), float(ap), float(e), str(struct)) for \
                                (ep, ap, e, struct) in structTupleLst ]
        return structTupleLst
    ##

    @staticmethod
    def SampleBoltzmannStructuresSHAPE(baseSeq, N, consList = []):
        """Sample INT (param N > 0) structures from Boltzmann distribution -- 
           using SHAPE style constraints 
           See options: -s, --sample INT (for use with gtboltzman), --useSHAPE FILE
        """
        GTFoldPython._ConstructLibGTFold()
        resType = ctypes.py_object
        argTypes = [ GTFPTypes.CStringType, GTFPTypes.SHAPEConstraintsListType(consList), 
                     ctypes.c_int, ctypes.c_int ]
        libGTFoldFunc = GTFoldPython._WrapCTypesFunction("SampleBoltzmannStructuresSHAPE", resType, argTypes)
        structTupleLst = libGTFoldFunc(GTFPTypes.CString(baseSeq), GTFPTypes.SHAPEConstraintsList(consList), 
                                       c_types.c_int(len(consList)), ctypes.c_int(N))
        structTupleLst = [ (float(ep), float(ap), float(e), str(struct)) for \
                                (ep, ap, e, struct) in structTupleLst ]
        return structTupleLst
    ##

    @staticmethod
    def DisplayDetailedHelp():
        """Display detailed help message. Includes examples and additional options useful to developers.
        ::seealso:: DisplayHelp
        """
        GTFoldPython._ConstructLibGTFold(False)
        resType = ctypes.py_object
        argTypes = []
        libGTFoldFunc = GTFoldPython._WrapCTypesFunction("DisplayDetailedHelp", resType, argTypes)
        return libGTFoldFunc()
    ##

    @staticmethod
    def DisplayHelp(funcHelpTopic):
        """Display detailed help message about a specifid function, setting, or help topic. 
           Includes examples and additional options useful to developers.
        ::seealso:: DisplayDetailedHelp
        """
        GTFoldPython._ConstructLibGTFold(False)
        resType = ctypes.py_object
        argTypes = [ GTFPTypes.CStringType ]
        libGTFoldFunc = GTFoldPython._WrapCTypesFunction("DisplayHelp", resType, argTypes)
        return libGTFoldFunc(GTFPTypes.CString(funcHelpTopic))
    ##

## class GTFoldPython
