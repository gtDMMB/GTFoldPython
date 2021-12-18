#### GTFoldPythonConfig.py.in : Stub header used to generate platform specific 
####                            configuration and other parameters for the library at build time

from collections import namedtuple
import os

class GTFoldPythonConfig(object):
    
    ## OS / Platform specs to be filled in at build time:
    PLATFORM_DARWIN       = True
    PLATFORM_LINUX        = False
    PLATFORM_OTHER        = False
    PLATFORM_VERSION      = "Darwin"
    PLATFORM_VERSION_FULL = "Darwin mathm1703 18.7.0 Darwin Kernel Version 18.7.0: Thu Jan 23 06:52:12 PST 2020; root:xnu-4903.278.25~1/RELEASE_X86_64 x86_64"

    @staticmethod
    def IsPlatformAppleDarwinOSX():
         return GTFoldPythonConfig.PLATFORM_DARWIN
    ##

    @staticmethod
    def IsPlatformLinux():
         return GTFoldPythonConfig.PLATFORM_LINUX
    ##

    @staticmethod
    def GetPlatformByString(fullPlatformDesc = False):
        if fullPlatformDesc:
             return GTFoldPythonConfig.PLATFORM_VERSION_FULL
        return GTFoldPythonConfig.PLATFORM_VERSION
    ##

    ## Thermodynamic parameters types (enum / constants for shorthands):
    THERMO_PARAMS_SPEC_GTFOLD       = "GTFold"
    THERMO_PARAMS_SPEC_RNAFOLD      = "RNAFold"
    THERMO_PARAMS_SPEC_UNAFOLD      = "UNAFold"
    THERMO_PARAMS_SPEC_TURNER04     = "Turner04"
    THERMO_PARAMS_SPEC_RNASTRUCTURE = "RNAStructure"
    THERMO_PARAMS_SPEC_DEFAULT      = "default"
    THERMO_PARAMS_SPEC_TURNER99     = "default-Turner99"
    THERMO_PARAMS_SPEC_MT09         = "default-MT09"
    THERMO_PARAMS_SPEC_MT99         = "default-MT99"
    THERMO_PARAMS_SPEC_TFMCDANGLES  = "default-TurnerConstrDangles"
    THERMO_PARAMS_SPEC_TFMDANGLES0  = "default-TurnerDangles0"

    #THERMO_PARAMS_BASEDIR        = os.path.abspath("/Users/mschmidt34/GTFoldPython/Python/Testing/ExtraGTFoldThermoData/")
    THERMO_PARAMS_BASEDIR        = os.path.abspath("./Testing/ExtraGTFoldThermoData/") + "/"
    THERMO_PARAMS_SUBDIRS        = dict(
        {
            THERMO_PARAMS_SPEC_GTFOLD       :    "DefaultGTFold", 
            THERMO_PARAMS_SPEC_RNAFOLD      :    "DefaultRNAFold", 
            THERMO_PARAMS_SPEC_UNAFOLD      :    "DefaultUNAFold", 
            THERMO_PARAMS_SPEC_TURNER99     :    "GTFoldTurner99", 
            THERMO_PARAMS_SPEC_TURNER04     :    "GTFoldTurner04", 
            THERMO_PARAMS_SPEC_RNASTRUCTURE :    "RNAstructure-6.0.1",
            THERMO_PARAMS_SPEC_DEFAULT      :    "DefaultGTFold", 
            THERMO_PARAMS_SPEC_MT09         :    "MT09", 
            THERMO_PARAMS_SPEC_MT99         :    "MT99",
            THERMO_PARAMS_SPEC_TFMCDANGLES  :    "TurnerFM363ConstrDangles", 
            THERMO_PARAMS_SPEC_TFMDANGLES0  :    "TurnerFM363Dangles0",
        }
    )

    @staticmethod
    def GetThermodynamicParametersDirectory(specType):
         specSubDir = GTFoldPythonConfig.THERMO_PARAMS_SUBDIRS[specType]
         if specSubDir == None:
             raise NotImplementedError
         return GTFoldPythonConfig.THERMO_PARAMS_BASEDIR + specSubDir
    ##

    _ThermoParamsSpecType = namedtuple('ThermoParams', ['name', 'subdir', 'fulldirpath'])

    @staticmethod
    def GetThermodynamicParametersList():
        ThermoParamsType = GTFoldPythonConfig._ThermoParamsSpecType
        thermoParamsList = [ ]
        for (specKey, subDirValue) in GTFoldPythonConfig.THERMO_PARAMS_SUBDIRS:
            fullDirPath = GTFoldPythonConfig.GetThermoDynamicParametersDirectory(specKey)
            tpSpecs = ThermoParamsType(name = specKey, subDir = subDirValue, fulldirpath = fullDirPath)
            thermoParamsList.append(tpSpecs)
        return thermoParamsList
    ##

##

