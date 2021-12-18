#ifndef _SUBOPT_MAIN_H_
#define _SUBOPT_MAIN_H_

extern char suboptFile[256];
extern int is_check_for_duplicates_enabled;
extern int UNIQUE_MULTILOOP_DECOMPOSITION;
extern int max_structure_count;

#ifdef __cplusplus
extern "C" {
     void write_header_subopt_file(const char *outputCFile, const char *seq, int energy);
}
#else 
     void write_header_subopt_file(const char *outputCFile, const char *seq, int energy);
#endif

void subopt_main(int argc, char** argv);

#endif
