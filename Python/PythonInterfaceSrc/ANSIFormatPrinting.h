/* ANSIFormatPrinting.h : Add a little color to spice up the terminal output!
 * Author: Maxie D. Schmidt (maxieds@gmail.com)
 * Created: 2020.02.07
 */

#ifndef __ANSI_FORMAT_PRINTING_H__
#define __ANSI_FORMAT_PRINTING_H__

#include "PythonConfig.h"

typedef const char * ANSIColorCode;
extern const ANSIColorCode _ANSIFG;
extern const ANSIColorCode _ANSIBG;
extern const ANSIColorCode _BLACK;
extern const ANSIColorCode _RED;
extern const ANSIColorCode _GREEN;
extern const ANSIColorCode _BROWN;
extern const ANSIColorCode _BLUE;
extern const ANSIColorCode _PURPLE;
extern const ANSIColorCode _CYAN;
extern const ANSIColorCode _LIGHT_GRAY;
extern const ANSIColorCode _DARK_GRAY;
extern const ANSIColorCode _LIGHT_RED;
extern const ANSIColorCode _LIGHT_GREEN;
extern const ANSIColorCode _YELLOW;
extern const ANSIColorCode _LIGHT_BLUE;
extern const ANSIColorCode _LIGHT_PURPLE;
extern const ANSIColorCode _LIGHT_CYAN;
extern const ANSIColorCode _LIGHT_WHITE;
extern const ANSIColorCode _BOLD;
extern const ANSIColorCode _ITALIC;
extern const ANSIColorCode _UNDERLINE;
extern const ANSIColorCode _END;

typedef enum {
    NORMAL         = 1, 
    FGBLACK        = 1 << 1, 
    FGRED          = 1 << 2, 
    FGGREEN        = 1 << 3, 
    FGYELLOW       = 1 << 4, 
    FGBLUE         = 1 << 5, 
    FGPURPLE       = 1 << 6,
    FGCYAN         = 1 << 7,
    BGBLACK        = 1 << 8, 
    BGRED          = 1 << 9, 
    BGGREEN        = 1 << 10, 
    BGBROWN        = 1 << 11, 
    BGBLUE         = 1 << 12, 
    BGPURPLE       = 1 << 13,
    BGCYAN         = 1 << 14,
    LIGHT_GRAY     = 1 << 15, 
    DARK_GRAY      = 1 << 16, 
    LIGHT_RED      = 1 << 17, 
    LIGHT_GREEN    = 1 << 18, 
    LIGHT_BLUE     = 1 << 19, 
    LIGHT_PURPLE   = 1 << 20, 
    LIGHT_CYAN     = 1 << 21, 
    LIGHT_WHITE    = 1 << 22,
    BOLD           = 1 << 23, 
    ITALIC         = 1 << 24, 
    UNDERLINE      = 1 << 25, 
} ANSIFormatStyleType_t;

#define FormatCodeContains(fcode, fmtStyle)          ((fcode & fmtStyle) != 0)

typedef struct {
     ANSIFormatStyleType_t fmtStyle;
     ANSIColorCode         colorCode;
     bool                  requiresParam;
     ANSIColorCode         codeParam;
} FormatStyleMap_t;

extern char _ANSI_FORMAT_STYLE[STR_BUFFER_SIZE];
extern FormatStyleMap_t FORMAT_STYLE_MAPS[];

void GetANSIFormatStyle(char *outputBuf, int formatStyleCode);
void TerminalPrint(FILE *whichOut, int ansiFmtStyle, const char *strFmt, ...);
void PrintBulletItem(FILE *whichOut, const char *bullet, int bulletFmt, 
		     const char *header, int headerFmt, 
		     const char *listItem, int listItemFmt, bool printNewline);

#endif
