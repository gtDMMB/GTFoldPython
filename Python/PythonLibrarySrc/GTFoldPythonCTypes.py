#### GTFoldPythonCTypes.py : Wrappers, definitions, and constructors for common 
####                         composite types used by the `ctypes` module
#### Author: Maxie D. Schmidt (maxieds@gmail.com
#### Created: 2020.02.03

from ctypes import POINTER
import ctypes

class FPConstraintStruct(ctypes.Structure):
    _fields_ = (('consType', ctypes.c_short),
                ('i', ctypes.c_short), ('j', ctypes.c_short), ('k', ctypes.c_short),)
##

class SHAPEConstraintStruct(ctypes.Structure):
    _fields_ = (('basePos', ctypes.c_int), ('shape', ctypes.c_double),)
##

class GTFoldPythonCTypes(object):

    ## Common types we we re-use frequently with `ctypes`:
    IntType = ctypes.c_int
    UIntType = ctypes.c_uint
    CStringType = POINTER(ctypes.c_char)
    FPConstraintType = ctypes.c_short * 4
    FPConstraintStructType = FPConstraintStruct
    SHAPEConstraintType = SHAPEConstraintStruct

    _GetNxMListOfListsType = lambda N, M, lst: (ctypes.c_int * M * N)(*[(ctypes.c_int * M)(*sublst) for sublst in lst])
    
    ## Perform type checking for validity before passing off to ctypes:
    PerformTypeChecking = True
    
    @staticmethod
    def IsStringType(x):
        return not GTFoldPythonCTypes.PerformTypeChecking or \
                type(x) == str or type(x) == bytearray

    @staticmethod
    def IsIntType(x): 
        return not GTFoldPythonCTypes.PerformTypeChecking or type(x) == int

    @staticmethod
    def IsFloatType(x):
        return not GTFoldPythonCTypes.PerformTypeChecking or type(x) == float

    @staticmethod
    def IsListType(x):
        return not GTFoldPythonCTypes.PerformTypeChecking or \
                type(x) == list or type(x) == tuple or len(x) == 0
    
    @staticmethod
    def IsFPConstraintsList(x):
        if not GTFoldPythonCTypes.IsListType(x):
            return False
        isCons = lambda elem: len([ e for e in elem if GTFoldPythonCTypes.IsIntType(e) ]) == 4
        return not GTFoldPythonCTypes.PerformTypeChecking or \
                len([ elem for elem in x if not isCons(elem) ]) == 0

    @staticmethod
    def IsSHAPEConstraintsList(x):
        if not GTFoldPythonCTypes.IsListType(x):
            return False
        isCons = lambda elem: len(elem) == 2 and GTFoldPythonCTypes.IsIntType(elem[0]) and \
                GTFoldPythonCTypes.IsFloatType(elem[1])
        return not GTFoldPythonCTypes.PerformTypeChecking or \
                len([ elem for elem in x if not isCons(elem) ]) == 0

    ## Transform stock (composite) Python objects into a useful `ctypes` typed variants:
    @staticmethod
    def CString(x):
        if GTFoldPythonCTypes.IsStringType(x):
            return ctypes.byref(ctypes.c_char.from_buffer(bytearray(x, encoding = 'utf-8')))
        elif x == None:
            return None     # Same as passing NULL string
        else:
            raise TypeError

    @staticmethod
    def FPConstraintsListType(x):
        if not GTFoldPythonCTypes.IsFPConstraintsList(x):
            raise TypeError
        consType = GTFoldPythonCTypes.FPConstraintType
        consListType = consType * len(x) if len(x) > 0 else ctypes.py_object
        return consListType

    @staticmethod
    def SHAPEConstraintsListType(x):
        if not GTFoldPythonCTypes.IsSHAPEConstraintsList(x):
            raise TypeError
        consType = GTFoldPythonCTypes.SHAPEConstraintType
        consListType = consType * len(x) if len(x) > 0 else ctypes.py_object
        return consListType

    @staticmethod
    def ConstraintsListType(x):
        if len(x) == 0:
            return ctypes.py_object
        elif (type(x[1]) == list or type(x[1]) == tuple) and len(x[1]) == 4:
            return FPConstraintsListType(x)
        elif type(x[1]) == tuple:
            return SHAPEConstraintsListType(x)
        else:
            raise TypeError

    @staticmethod
    def FPConstraintsList(x):
        if GTFoldPythonCTypes.IsFPConstraintsList(x):
            xlst = [ GTFoldPythonCTypes.FPConstraintType(*xi) for xi in x ]
            return GTFoldPythonCTypes.FPConstraintsListType(x)(*xlst) if len(x) > 0 else []
        else:
            raise TypeError

    @staticmethod
    def SHAPEConstraintsList(x):
        if GTFoldPythonCTypes.IsSHAPEConstraintsList(x):
            xlst = [ GTFoldPythonCTypes.SHAPEConstraintType(*xi) for xi in x ]
            return GTFoldPythonCTypes.SHAPEConstraintsListType(x)(*xlst) if len(x) > 0 else []
        else:
            raise TypeError

    @staticmethod
    def ConstraintsList(x):
        if not GTFoldPythonCTypes.IsListType(x):
            raise TypeError
        elif len(x) == 0:
            return []
        elif (type(x[1]) == list or type(x[1]) == tuple) and len(x[1]) == 4:
            return FPConstraintsList(x)
        elif type(x[1]) == tuple:
            return SHAPEConstraintsList(x)
        else:
            raise TypeError

## 
