/* GTFoldPython.h : Function definitions and data structures to run the bulk of the library wrapper 
 *                  methods; 
 * Author: Maxie D. Schmidt (maxieds@gmail.com) 
 * Created: 2020.01.22
 */

#ifndef __GTFOLD_PYTHON_H__
#define __GTFOLD_PYTHON_H__

#include "PythonConfig.h"
#include "ANSIFormatPrinting.h"
#include "Constraints.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef void                 __VOID__;
typedef int                  __INT__;
typedef const char *         __BASESEQ__;
typedef const char *         __CSTR__;
typedef ConsListCType_t      __CONSLIST__;
typedef SHAPEConstraint_t *  __SHAPECONSLIST__;
typedef int                  __INTLEN__;
typedef double               __DELTA__;
typedef int                  __INTNUM__;
typedef const char *         __FILENO__;
typedef PyObject *           __PYOBJ__;
typedef PyObject *           __PYARGS__;
typedef PyObject *           __PYKWARGS__;

PyObject * __EXPORT__ GTFoldPythonInit( __VOID__ );
PyObject * __EXPORT__ GTFoldPythonConfig( __INT__, __INT__, __INT__, __FILENO__ );
PyObject * __EXPORT__ GTFoldPythonConfigSettings( __PYOBJ__ );
PyObject * __EXPORT__ PrintGTFoldRunConfiguration( __INT__);
PyObject * __EXPORT__ SetGTFoldDataDirectory( __CSTR__, __INTLEN__ );
PyObject * __EXPORT__ SetThermodynamicParameters( __CSTR__, __CSTR__ );
PyObject * __EXPORT__ SetDangleParameter( __INT__ );
PyObject * __EXPORT__ SetTerminalMismatch( __INT__ );
PyObject * __EXPORT__ SetLimitContactDistance( __INT__ );
PyObject * __EXPORT__ SetPrefilterParameter( __INT__ );
PyObject * __EXPORT__ GetPFuncCount( __BASESEQ__, __CONSLIST__, __INTLEN__ );
PyObject * __EXPORT__ GetPFuncCountSHAPE( __BASESEQ__, __SHAPECONSLIST__, __INTLEN__ );
PyObject * __EXPORT__ ComputeBPP( __BASESEQ__, __CONSLIST__, __INTLEN__ );
PyObject * __EXPORT__ ComputeBPPSHAPE( __BASESEQ__, __SHAPECONSLIST__, __INTLEN__ );
PyObject * __EXPORT__ GetMFEStructure( __BASESEQ__, __CONSLIST__, __INTLEN__ );
PyObject * __EXPORT__ GetMFEStructureSHAPE( __BASESEQ__, __SHAPECONSLIST__, __INTLEN__ );
PyObject * __EXPORT__ GetSuboptStructuresWithinRange( __BASESEQ__, __DELTA__ );
PyObject * __EXPORT__ SampleBoltzmannStructures( __BASESEQ__, __CONSLIST__, __INTLEN__, __INTNUM__ );
PyObject * __EXPORT__ SampleBoltzmannStructuresSHAPE( __BASESEQ__, __SHAPECONSLIST__, 
		                                      __INTLEN__, __INTNUM__ );

extern const PyMethodDef GTFoldPython_Methods[];

typedef enum {
     VOID     = 0,
     BOOL     = 1,
     INT      = 2, 
     UINT     = 3, 
     SHORT    = 4, 
     FLOAT    = 5, 
     DOUBLE   = 6, 
     STRING   = 7, 
} CTypePrimitive_t;

static inline const char * CPrimitiveTypeToString(CTypePrimitive_t ctypeSpec) {
     switch(ctypeSpec) {
          case VOID:   return "VOID";
	  case BOOL:   return "BOOL|INT";
	  case INT:    return "INT";
	  case UINT:   return "UINT|INT";
	  case SHORT:  return "SHORT|INT";
	  case FLOAT:  return "FLOAT";
	  case DOUBLE: return "DOUBLE";
	  case STRING: return "STRING";
	  default:     return "";
     }
     return "";
}

typedef struct {
     const char       *keywordID;
     CTypePrimitive_t ctype;
     const char       *gtfoldOptions;
     const char       *help;
     int              *boolTruthVar;
     void             *dataRef[4]; // the size 4 is chosen as an upper bound, change it if necessary
} GTFoldKeywordSpec_t;

#define PRINT_HELP_BULLET_ANSIFMT           (DARK_GRAY | BOLD)
#define PRINT_HELP_ITEMHDR_ANSIFMT          (LIGHT_PURPLE | BOLD)
#define PRINT_HELP_ITEMVAL_ANSIFMT          (LIGHT_RED | ITALIC | BOLD)
#define PRINT_HELP_MAINHDR_ANSIFMT          (LIGHT_WHITE | BGBLACK | BOLD | ITALIC | UNDERLINE)
#define PRINT_HELP_DOCSTR_ANSIFMT           (LIGHT_BLUE | ITALIC)
#define PRINT_HELP_ERRORSTR_ANSIFMT         (FGRED | ITALIC)

#define PrintHelpListItem(bullet, itemHdr, itemTxt) \
	PrintBulletItem(CONFIG_STDMSGOUT, bullet, PRINT_HELP_BULLET_ANSIFMT, \
			itemHdr, PRINT_HELP_ITEMHDR_ANSIFMT, \
			itemTxt, PRINT_HELP_ITEMVAL_ANSIFMT, true)

PyObject * __EXPORT__ DisplayDetailedHelp(void);
PyObject * __HIDDEN__ DisplayDetailedHelpSettings(void);
PyObject * __EXPORT__ DisplayHelp(const char *methodName);

#ifdef PY3K
PyMODINIT_FUNC PyInit_GTFoldPython(void);
extern struct PyModuleDef GTFoldPythonModule;
#endif

/* Define a "dummy" method that calls all of our interface functions to 
 * make sure each is easily included in the final shared library (GTFoldPython.so);
 */
void __HIDDEN__ ModuleInterfaceDeps(void);

#ifdef __cplusplus
}
#endif

#endif
