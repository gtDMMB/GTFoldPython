#### GTFoldPythonImportAll.py : Import all functions from all of the sub-files 
#### Author: Maxie D. Schmidt (maxieds@gmail.com)
#### Created: 2020.02.06

## GTFoldPythonConfig:
from GTFoldPythonConfig import GTFoldPythonConfig as GTFPConfig
PLATFORM_DARWIN       = GTFPConfig.PLATFORM_DARWIN
PLATFORM_LINUX        = GTFPConfig.PLATFORM_LINUX
PLATFORM_OTHER        = GTFPConfig.PLATFORM_OTHER
PLATFORM_VERSION      = GTFPConfig.PLATFORM_VERSION
PLATFORM_VERSION_FULL = GTFPConfig.PLATFORM_VERSION_FULL

IsPlatformAppleDarwinOSX = GTFPConfig.IsPlatformAppleDarwinOSX
IsPlatformLinux          = GTFPConfig.IsPlatformLinux
GetPlatformByString      = GTFPConfig.GetPlatformByString

GTFOLD                = GTFPConfig.THERMO_PARAMS_SPEC_GTFOLD
RNAFOLD               = GTFPConfig.THERMO_PARAMS_SPEC_RNAFOLD
UNAFOLD               = GTFPConfig.THERMO_PARAMS_SPEC_UNAFOLD
TURNER04              = GTFPConfig.THERMO_PARAMS_SPEC_TURNER04
TURNER99              = GTFPConfig.THERMO_PARAMS_SPEC_TURNER99
RNASTRUCTURE          = GTFPConfig.THERMO_PARAMS_SPEC_RNASTRUCTURE
THERMO_PARAMS_DEFAULT = GTFPConfig.THERMO_PARAMS_SPEC_DEFAULT
MT09                  = GTFPConfig.THERMO_PARAMS_SPEC_MT09
MT99                  = GTFPConfig.THERMO_PARAMS_SPEC_MT99
DEFAULT               = GTFPConfig.THERMO_PARAMS_SPEC_DEFAULT

THERMO_PARAMS_BASEDIR = GTFPConfig.THERMO_PARAMS_BASEDIR
GetThermodynamicParametersDirectory = GTFPConfig.GetThermodynamicParametersDirectory
GetThermodynamicParametersList      = GTFPConfig.GetThermodynamicParametersList

## GTFoldPythonCTypes:
from GTFoldPythonCTypes import GTFoldPythonCTypes as GTFPTypes
IntType                  = GTFPTypes.IntType
UIntType                 = GTFPTypes.UIntType
CStringType              = GTFPTypes.CStringType
FPConstraintType         = GTFPTypes.FPConstraintType
FPConstraintStructType   = GTFPTypes.FPConstraintStructType
SHAPEConstraintType      = GTFPTypes.SHAPEConstraintType
IsStringType             = GTFPTypes.IsStringType
IsIntType                = GTFPTypes.IsIntType
IsFloatType              = GTFPTypes.IsFloatType
IsFPConstraintsList      = GTFPTypes.IsFPConstraintsList
IsSHAPEConstraintList    = GTFPTypes.IsSHAPEConstraintsList
CString                  = GTFPTypes.CString
FPConstraintsListType    = GTFPTypes.FPConstraintsListType
SHAPECOnstraintsListType = GTFPTypes.SHAPEConstraintsListType
ConstraintsListType      = GTFPTypes.ConstraintsListType
FPConstraintsListType    = GTFPTypes.FPConstraintsList
SHAPEConstraintsList     = GTFPTypes.SHAPEConstraintsList
FPConstraintsList        = GTFPTypes.FPConstraintsList
SHAPEConstraintsList     = GTFPTypes.SHAPEConstraintsList
ConstraintsList          = GTFPTypes.ConstraintsList

## GTFoldPythonUtils:
from GTFoldPythonUtils import GTFoldPythonUtils as GTFPUtils
Constraint                   = GTFPUtils.Constraint
ForcedConstraint             = GTFPUtils.ForcedConstraint
ProhibitedConstraint         = GTFPUtils.ProhibitedConstraint
SHAPEConstraint              = GTFPUtils.SHAPEConstraint
GetFPConstraintsFromString   = GTFPUtils.GetFPConstraintsFromString
ReadFPConstraintsFromFile    = GTFPUtils.ReadFPConstraintsFromFile
ReadSHAPEConstraintsFromFile = GTFPUtils.ReadSHAPEConstraintsFromFile
ReadConstraintsFromFile      = GTFPUtils.ReadConstraintsFromFile
DOTStructToPairsList         = GTFPUtils.DOTStructToPairsList
ParseFASTAFile               = GTFPUtils.ParseFASTAFile
ParseCTFile                  = GTFPUtils.ParseCTFile
ParseDOTBracketFile          = GTFPUtils.ParseDOTBracketFile

## GTFoldPython:
from GTFoldPython import GTFoldPython as GTFP
F                                      = GTFP.F
P                                      = GTFP.P
Init                                   = GTFP.Init
Config                                 = GTFP.Config
ConfigSettings                         = GTFP.ConfigExtraSettings
PrintRunConfiguration                  = GTFP.PrintRunConfiguration
SetGTFoldDataDirectory                 = GTFP.SetGTFoldDataDirectory
SetThermodynamicParameters             = GTFP.SetThermodynamicParameters
SetThermodynamicParametersFromDefaults = GTFP.SetThermodynamicParametersFromDefaults
SetDangleParameter                     = GTFP.SetDangleParameter
EnableTerminalMismatch                 = GTFP.EnableTerminalMismatch
DisableTerminalMismatch                = GTFP.DisableTerminalMismatch
SetLimitContactDistance                = GTFP.SetLimitContactDistance
SetPrefilterParameter                  = GTFP.SetPrefilterParameter
GetPFuncCount                          = GTFP.GetPFuncCount
GetPFuncCountSHAPE                     = GTFP.GetPFuncCountSHAPE
ComputeBPP                             = GTFP.ComputeBPP
ComputeBPPSHAPE                        = GTFP.ComputeBPPSHAPE
GetMFEStructure                        = GTFP.GetMFEStructure
GetMFEStructureSHAPE                   = GTFP.GetMFEStructureSHAPE
GetSuboptStructures                    = GTFP.GetSuboptStructures
GetBoltzmannStructures                 = GTFP.SampleBoltzmannStructures
GetBoltzmannStructuresSHAPE            = GTFP.SampleBoltzmannStructuresSHAPE
DisplayDetailedHelp                    = GTFP.DisplayDetailedHelp
DisplayHelp                            = GTFP.DisplayHelp

