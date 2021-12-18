/* ANSIFormatPrinting.c : Implementation to allow ANSI colored terminal printing;
 * Author: Maxie D. Schmidt (maxieds@gmail.com)
 * Created: 2020.02.09
 */

#include <stdio.h>
#include <stdarg.h>

#include "ANSIFormatPrinting.h"
#include "Utils.h"

const ANSIColorCode _ANSIFG          = "3";
const ANSIColorCode _ANSIBG          = "4";
const ANSIColorCode _BLACK           = "\x1b[0;%s0m";
const ANSIColorCode _RED             = "\x1b[0;%s1m";
const ANSIColorCode _GREEN           = "\x1b[0;%s2m";
const ANSIColorCode _BROWN           = "\x1b[0;%s3m";
const ANSIColorCode _BLUE            = "\x1b[0;%s4m";
const ANSIColorCode _PURPLE          = "\x1b[0;%s5m";
const ANSIColorCode _CYAN            = "\x1b[0;%s6m";
const ANSIColorCode _LIGHT_GRAY      = "\x1b[0;37m";
const ANSIColorCode _DARK_GRAY       = "\x1b[1;30m";
const ANSIColorCode _LIGHT_RED       = "\x1b[1;31m";
const ANSIColorCode _LIGHT_GREEN     = "\x1b[1;32m";
const ANSIColorCode _YELLOW          = "\x1b[1;%s3m";
const ANSIColorCode _LIGHT_BLUE      = "\x1b[1;34m";
const ANSIColorCode _LIGHT_PURPLE    = "\x1b[1;35m";
const ANSIColorCode _LIGHT_CYAN      = "\x1b[1;36m";
const ANSIColorCode _LIGHT_WHITE     = "\x1b[1;37m";
const ANSIColorCode _BOLD            = "\x1b[1m";
const ANSIColorCode _ITALIC          = "\x1b[3m";
const ANSIColorCode _UNDERLINE       = "\x1b[4m";
const ANSIColorCode _END             = "\x1b[0m";

char _ANSI_FORMAT_STYLE[STR_BUFFER_SIZE];

FormatStyleMap_t FORMAT_STYLE_MAPS[] = {
     { NORMAL,       _END,            false,   ""      },
     { FGBLACK,      _BLACK,          true,    _ANSIFG }, 
     { FGRED,        _RED,            true,    _ANSIFG }, 
     { FGGREEN,      _GREEN,          true,    _ANSIFG },
     { FGYELLOW,     _YELLOW,         true,    _ANSIFG }, 
     { FGBLUE,       _BLUE,           true,    _ANSIFG }, 
     { FGPURPLE,     _PURPLE,         true,    _ANSIFG }, 
     { FGCYAN,       _CYAN,           true,    _ANSIFG }, 
     { BGBLACK,      _BLACK,          true,    _ANSIBG }, 
     { BGRED,        _RED,            true,    _ANSIBG }, 
     { BGGREEN,      _GREEN,          true,    _ANSIBG }, 
     { BGBROWN,      _BROWN,          true,    _ANSIBG }, 
     { BGBLUE,       _BLUE,           true,    _ANSIBG }, 
     { BGPURPLE,     _PURPLE,         true,    _ANSIBG }, 
     { BGCYAN,       _CYAN,           true,    _ANSIBG }, 
     { LIGHT_GRAY,   _LIGHT_GRAY,     false,   ""      }, 
     { DARK_GRAY,    _DARK_GRAY,      false,   ""      }, 
     { LIGHT_RED,    _LIGHT_RED,      false,   ""      }, 
     { LIGHT_GREEN,  _LIGHT_GREEN,    false,   ""      }, 
     { LIGHT_BLUE,   _LIGHT_BLUE,     false,   ""      }, 
     { LIGHT_PURPLE, _LIGHT_PURPLE,   false,   ""      }, 
     { LIGHT_CYAN,   _LIGHT_CYAN,     false,   ""      }, 
     { LIGHT_WHITE,  _LIGHT_WHITE,    false,   ""      }, 
     { BOLD,         _BOLD,           false,   ""      }, 
     { ITALIC,       _ITALIC,         false,   ""      }, 
     { UNDERLINE,    _UNDERLINE,      false,   ""      }, 
};

void GetANSIFormatStyle(char *outputBuf, int formatStyleCode) {
     outputBuf[0] = '\0';
     for(int fs = 0; fs < GetArrayLength(FORMAT_STYLE_MAPS); fs++) {
          if(!FormatCodeContains(formatStyleCode, FORMAT_STYLE_MAPS[fs].fmtStyle)) {
	       continue;
	  }
          char tempStyleBuf[32];
	  sprintf(tempStyleBuf, "%s", FORMAT_STYLE_MAPS[fs].colorCode);
	  if(FORMAT_STYLE_MAPS[fs].requiresParam) {
	        char tempStyleBuf2[32];
	        sprintf(tempStyleBuf2, tempStyleBuf, FORMAT_STYLE_MAPS[fs].codeParam);
		strcpy(tempStyleBuf, tempStyleBuf2);
	  }
	  strcat(outputBuf, tempStyleBuf);
     }
}

void TerminalPrint(FILE *whichOut, int ansiFmtStyle, const char *strFmt, ...) {
     char fmtStyle[STR_BUFFER_SIZE];
     GetANSIFormatStyle(fmtStyle, ansiFmtStyle);
     fprintf(whichOut, "%s", fmtStyle);
     size_t numNewlines = 0, backPos = strlen(strFmt);
     while(backPos > 0) {
          if(strFmt[--backPos] != '\n') break;
	  numNewlines++;
     }
     char strFmtNoNewlines[STR_BUFFER_SIZE];
     strcpy(strFmtNoNewlines, strFmt);
     if(backPos > 0) {
          strFmtNoNewlines[backPos + 1] = '\0';
     }
     va_list argList;
     va_start(argList, strFmt);
     vfprintf(whichOut, strFmtNoNewlines, argList);
     va_end(argList);
     fprintf(whichOut, "%s", _END);
     for(int nl = 0; nl < numNewlines; nl++) {
          fprintf(whichOut, "\n");
     }
}

void PrintBulletItem(FILE *whichOut, const char *bullet, int bulletFmt, 
		     const char *header, int headerFmt,
                     const char *listItem, int listItemFmt, bool printNewline) {
     fprintf(whichOut, "%s  ", _END);
     TerminalPrint(whichOut, bulletFmt, "%s", bullet);
     fprintf(whichOut, "%s ", _END);
     TerminalPrint(whichOut, headerFmt, "%s", header);
     fprintf(whichOut, "%s ", _END);
     TerminalPrint(whichOut, listItemFmt, "%s%s", listItem, _END);
     if(printNewline) {
          fprintf(whichOut, "\n");
     }
}

