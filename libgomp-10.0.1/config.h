/* config.h.  Generated from config.h.in by configure.  */
/* config.h.in.  Generated from configure.ac by autoheader.  */

/* Define to 1 if you have the `aligned_alloc' function. */
/* #undef HAVE_ALIGNED_ALLOC */

/* Define to 1 if the target assembler supports .symver directive. */
/* #undef HAVE_AS_SYMVER_DIRECTIVE */

/* Define to 1 if the target supports __attribute__((alias(...))). */
/* #undef HAVE_ATTRIBUTE_ALIAS */

/* Define to 1 if the target supports __attribute__((dllexport)). */
#define HAVE_ATTRIBUTE_DLLEXPORT 1

/* Define to 1 if the target supports __attribute__((visibility(...))). */
#define HAVE_ATTRIBUTE_VISIBILITY 1

/* Define if the POSIX Semaphores do not work on your system. */
#define HAVE_BROKEN_POSIX_SEMAPHORES 1

/* Define to 1 if the target assembler supports thread-local storage. */
/* #undef HAVE_CC_TLS */

/* Define to 1 if you have the `clock_gettime' function. */
#define HAVE_CLOCK_GETTIME 1

/* Define to 1 if you have the <dlfcn.h> header file. */
#define HAVE_DLFCN_H 1

/* Define to 1 if you have the `getegid' function. */
#define HAVE_GETEGID 1

/* Define to 1 if you have the `geteuid' function. */
#define HAVE_GETEUID 1

/* Define to 1 if you have the `getgid' function. */
#define HAVE_GETGID 1

/* Define if gethostname is supported. */
#define HAVE_GETHOSTNAME 1

/* Define to 1 if you have the `getloadavg' function. */
/* #undef HAVE_GETLOADAVG */

/* Define if getpid is supported. */
#define HAVE_GETPID 1

/* Define to 1 if you have the `getuid' function. */
#define HAVE_GETUID 1

/* Define to 1 if you have the <inttypes.h> header file. */
#define HAVE_INTTYPES_H 1

/* Define to 1 if you have the `dl' library (-ldl). */
#define HAVE_LIBDL 1

/* Define to 1 if you have the `memalign' function. */
/* #undef HAVE_MEMALIGN */

/* Define to 1 if you have the <memory.h> header file. */
#define HAVE_MEMORY_H 1

/* Define to 1 if you have the `posix_memalign' function. */
#define HAVE_POSIX_MEMALIGN 1

/* Define if pthread_{,attr_}{g,s}etaffinity_np is supported. */
/* #undef HAVE_PTHREAD_AFFINITY_NP */

/* Define to 1 if you have the <pthread.h> header file. */
#define HAVE_PTHREAD_H 1

/* Define to 1 if you have the `secure_getenv' function. */
/* #undef HAVE_SECURE_GETENV */

/* Define to 1 if you have the <semaphore.h> header file. */
#define HAVE_SEMAPHORE_H 1

/* Define to 1 if you have the <stdint.h> header file. */
#define HAVE_STDINT_H 1

/* Define to 1 if you have the <stdlib.h> header file. */
#define HAVE_STDLIB_H 1

/* Define to 1 if you have the <strings.h> header file. */
#define HAVE_STRINGS_H 1

/* Define to 1 if you have the <string.h> header file. */
#define HAVE_STRING_H 1

/* Define to 1 if you have the `strtoull' function. */
#define HAVE_STRTOULL 1

/* Define to 1 if the system has the type `struct _Mutex_Control'. */
/* #undef HAVE_STRUCT__MUTEX_CONTROL */

/* Define to 1 if the target runtime linker supports binding the same symbol
   to different versions. */
/* #undef HAVE_SYMVER_SYMBOL_RENAMING_RUNTIME_SUPPORT */

/* Define to 1 if the target supports __sync_*_compare_and_swap */
#define HAVE_SYNC_BUILTINS 1

/* Define to 1 if you have the <sys/loadavg.h> header file. */
/* #undef HAVE_SYS_LOADAVG_H */

/* Define to 1 if you have the <sys/stat.h> header file. */
#define HAVE_SYS_STAT_H 1

/* Define to 1 if you have the <sys/sysctl.h> header file. */
#define HAVE_SYS_SYSCTL_H 1

/* Define to 1 if you have the <sys/time.h> header file. */
#define HAVE_SYS_TIME_H 1

/* Define to 1 if you have the <sys/types.h> header file. */
#define HAVE_SYS_TYPES_H 1

/* Define to 1 if the target supports thread-local storage. */
/* #undef HAVE_TLS */

/* Define if uname is supported and struct utsname has nodename field. */
/* #undef HAVE_UNAME */

/* Define to 1 if you have the <unistd.h> header file. */
#define HAVE_UNISTD_H 1

/* Define to 1 if you have the `_aligned_malloc' function. */
/* #undef HAVE__ALIGNED_MALLOC */

/* Define to 1 if you have the `__secure_getenv' function. */
/* #undef HAVE___SECURE_GETENV */

/* Define path to HSA runtime. */
#define HSA_RUNTIME_LIB ""

/* Define to 1 if GNU symbol versioning is used for libgomp. */
/* #undef LIBGOMP_GNU_SYMBOL_VERSIONING */

/* Define to 1 if building libgomp for an accelerator-only target. */
/* #undef LIBGOMP_OFFLOADED_ONLY */

/* Define to 1 if libgomp should use POSIX threads. */
#define LIBGOMP_USE_PTHREADS 1

/* Define to the sub-directory in which libtool stores uninstalled libraries.
   */
#define LT_OBJDIR ".libs/"

/* Define to offload plugins, separated by commas. */
#define OFFLOAD_PLUGINS ""

/* Name of package */
#define PACKAGE "libgomp"

/* Define to the address where bug reports for this package should be sent. */
#define PACKAGE_BUGREPORT ""

/* Define to the full name of this package. */
#define PACKAGE_NAME "GNU Offloading and Multi Processing Runtime Library"

/* Define to the full name and version of this package. */
#define PACKAGE_STRING "GNU Offloading and Multi Processing Runtime Library 1.0"

/* Define to the one symbol short name of this package. */
#define PACKAGE_TARNAME "libgomp"

/* Define to the home page for this package. */
#define PACKAGE_URL "http://www.gnu.org/software/libgomp/"

/* Define to the version of this package. */
#define PACKAGE_VERSION "1.0"

/* Define to 1 if the GCN plugin is built, 0 if not. */
#define PLUGIN_GCN 0

/* Define to 1 if the HSA plugin is built, 0 if not. */
#define PLUGIN_HSA 0

/* Define to 1 if the NVIDIA plugin is built, 0 if not. */
#define PLUGIN_NVPTX 0

/* Define to 1 if the NVIDIA plugin should dlopen libcuda.so.1, 0 if it should
   be linked against it. */
#define PLUGIN_NVPTX_DYNAMIC 0

/* Define if all infrastructure, needed for plugins, is supported. */
#define PLUGIN_SUPPORT 1

/* Define to 1 if you have the ANSI C header files. */
#define STDC_HEADERS 1

/* Define if you can safely include both <string.h> and <strings.h>. */
#define STRING_WITH_STRINGS 1

/* Define to 1 if you can safely include both <sys/time.h> and <time.h>. */
#define TIME_WITH_SYS_TIME 1

/* Define to 1 if the target use emutls for thread-local storage. */
/* #undef USE_EMUTLS */

/* Version number of package */
#define VERSION "1.0"
