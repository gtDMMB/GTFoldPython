#ifndef _MFE_MAIN_H_
#define _MFE_MAIN_H_

extern int nThreads;
extern char constraintsFile[256];

#ifdef __cplusplus
extern "C" {
     int mfe_main(int argc, char** argv);
     double calculate_mfe(int seqLength);
     void init_fold(const char* seq);
     void parse_mfe_options(int argc, char** argv);
     void free_fold(int len);
}
#else
     int mfe_main(int argc, char** argv);
     double calculate_mfe(int seqLength);
     void init_fold(const char* seq);
     void parse_mfe_options(int argc, char** argv);
     void free_fold(int len);
#endif

#endif
