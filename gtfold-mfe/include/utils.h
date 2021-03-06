#ifndef _UTILS_H_
#define _UTILS_H_

#include "constants.h"

#define MIN(X,Y) ((X) < (Y) ? (X) : (Y))
#define MAX(X,Y) ((X) > (Y) ? (X) : (Y))
#define MIN4(W,X,Y,Z) MIN(MIN(W,X),MIN(Y,Z))
#define MIN3(W,X,Y) MIN(MIN(W,X),Y)

#ifdef __cplusplus
extern "C" {
     int is_valid_base(char c);
     char baseToDigit(const char* base) ;
     unsigned char encode(char base);
     int isWatsonCrickBase(char base);
     double get_seconds();
}
#else 
     int is_valid_base(char c);
     char baseToDigit(const char* base) ;
     unsigned char encode(char base);
     int isWatsonCrickBase(char base);
     double get_seconds();
#endif 

#endif
