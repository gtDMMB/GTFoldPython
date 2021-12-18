#ifndef __SUBOPT_TRACEBACK_CINCLUDE_H__
#define __SUBOPT_TRACEBACK_CINCLUDE_H__

typedef struct {
     char *dotStruct;
     int energy;
} ss_ctype_t;

#ifdef __cplusplus
extern "C" {
ss_ctype_t * SuboptTraceback(int len, int gap, const char *suboptFile, int writeToFile, 
                             int is_check_for_duplicates_enabled, int max_structure_count, 
			     int *arrayCount);
}
#else 
ss_ctype_t * SuboptTraceback(int len, int gap, const char *suboptFile, int writeToFile, 
                             int is_check_for_duplicates_enabled, int max_structure_count, 
			     int *arrayCount);
#endif

#endif
