#### Makefile : Build the local GTFoldPython module source
#### Author: Maxie D. Schmidt (maxieds@gmail.com)
#### Created: 2020.01.22

SED=$(shell which sed)
GREP=$(shell which grep)
READLINK=$(shell which readlink)
BASH=$(shell which bash)
RANLIB=$(shell which ranlib)
LIBTOOL=$(shell which libtool)
LIBTOOLIZE=$(shell which libtoolize)

BUILD_PLATFORM=$(shell uname -s)
ifeq "$(BUILD_PLATFORM)" "Darwin" # Apple / Mac OSX
	SED=$(shell which gsed)
	GREP=$(shell which ggrep)
	READLINK=$(shell which greadlink)
     #LIBTOOL=$(shell which glibtool)
	#LIBTOOLIZE=$(shell which glibtoolize)
endif

GTFOLDMAKEDIR=../gtfold-mfe
GTFOLDSRC=../gtfold-mfe/src
GTFOLDINCL=$(shell $(READLINK) -f ../gtfold-mfe)
GTFOLDLIB=../gtfold-mfe/src
LIBGMPDIR=$(shell $(READLINK) -f ../libgmp-6.2.0)
LIBGMPSTATIC=$(LIBGMPDIR)/.libs/libgmp.a $(LIBGMPDIR)/.libs/libgmpxx.a
LIBGOMPDIR=$(shell $(READLINK) -f ../libgomp-10.0.1)
LIBGOMPSTATIC=$(LIBGOMPDIR)/.libs/libgomp
GTFPYTHONSRC=./PythonInterfaceSrc
GTFPYTHONLIB=./PythonLibrarySrc
OBJBUILDDIR=$(shell $(READLINK) -f ./Lib)
MODULEEXT=.so
MODULE_BASENAME=GTFoldPython
MODULENAME=$(MODULE_BASENAME)$(MODULEEXT)
GTFOLD_MODULENAME=$(OBJBUILDDIR)/GTFold.a

PYSPEC=-DPYTHON3
PYPKG=python3
PYTHON3RT=python3

## The --embed flag is only apparently good for >= python3.9:
PYCFG=$(shell which python3-config) --embed #python2.7-config
ifeq ([ $(shell python3 --version) -lt 3.9 ], true)
	PYCFG=$(shell which python3-config)
endif

CC=$(shell which gcc)
LD=$(shell which g++)
CXX=$(LD)

CFLAGS_BASE=-O0 -D_GNU_SOURCE -DGNU_SOURCE -D__USE_GNU -DPY3K #-D_GLIBCXX_DEBUG #-U_OPENMP
CFLAGS=
LDFLAGS_BASE=
LDFLAGS_LIBS=
LDFLAGS=$(LDFLAGS_BASE) $(LDFLAGS_LIBS)
SOLIBOUTFLAGS=

CC_LIBGOMP=$(shell which gcc)
CC_GTFOLD=$(shell which gcc)
CXX_GTFOLD=$(shell which g++)
GFORTRAN=$(shell which gfortran)

CFLAGS_LIBGMP=
CFLAGS_LIBGOMP=
CFLAGS_GTFOLD=-fPIC -m64 -fvisibility=default  -I$(shell $(READLINK) -f $(LIBGMPDIR)) -I$(shell $(READLINK) -f $(LIBGOMPDIR))
CXXFLAGS_LIBGMP=
CXXFLAGS_GTFOLD=
LDFLAGS_LIBGMP=
LDFLAGS_LIBGOMP=
LDFLAGS_GTFOLD=
FCFLAGS_LIBGOMP=

ifeq "$(BUILD_PLATFORM)" "Darwin" # Apple / Mac OSX
	#MODULEEXT=$(shell $(PYCFG) --extension-suffix)
	MODULEEXT=.dylib
	RANLIB=$(shell which ranlib) -c
	#CC=$(shell which clang)
	#CXX=$(shell which clang++)
	#LD=$(shell which ld64.lld)
	CFLAGS_BASE= -g -march=native -pedantic -fPIC -Xpreprocessor -fopenmp \
			-fno-strict-aliasing -Wall -Wextra -I$(GTFOLDINCL) -m64 \
			-DBUILD_SHARED_LIBS=ON $(PYSPEC) -fvisibility=default \
			-fno-stack-check -fno-stack-protector -D_FORTIFY_SOURCE=0 \
			-I/usr/local/opt/llvm/include \
			-I$(shell $(READLINK) -f $(LIBGMPDIR)) -I$(shell $(READLINK) -f $(LIBGOMPDIR))
	CFLAGS=$(CFLAGS_BASE)
	CFLAGS+= -DNDEBUG -Wstrict-prototypes \
		 $(shell $(PYCFG) --includes | $(SED) -e 's/-no-cpp-precomp//g')
	LDFLAGS_BASE= -dynamic -bind_at_load -flat_namespace -Wl,-undefined,error 
	LDFLAGS_LIBS+= -Wl,-all_load $(LIBGOMPSTATIC).a $(LIBGMPSTATIC) -Wl,-noall_load \
			-ldl -lpthread -lc++ -lc -L/usr/local/opt/llvm/lib -lomp #-lc++abi
	LDFLAGS+= $(shell $(PYCFG) --ldflags | $(SED) -e 's/-no-cpp-precomp//g') \
			-read_only_relocs suppress \
			#-rpath Lib #$(shell $(READLINK) -f ../)
	SOLIBOUTFLAGS= -dynamiclib -install_name @rpath/$(MODULE_BASENAME) \
    			-current_version 1.0.0 -compatibility_version 1.0
	CC_LIBGOMP=$(CC) -march=native -force_cpusubtype_ALL 
	CC_GTFOLD=$(CC) -march=native -force_cpusubtype_ALL
	CXX_GTFOLD=$(CXX) -march=native -force_cpusubtype_ALL
	GFORTRAN=gfortran -march=native -force_cpusubtype_ALL
	CFLAGS_LIBGMP= -march=native -force_cpusubtype_ALL -std=gnu99 -fPIC -m64 -fvisibility=default #-Wno-error
	CFLAGS_LIBGOMP= -Wno-error=implicit-function-declaration \
			-fno-short-enums -Wno-error -std=gnu99 -I. -fPIC -I./gcc-include -m64 \
			-fvisibility=default -Wno-error
	CXXFLAGS_LIBGMP= -march=native -force_cpusubtype_ALL -fPIC -m64 \
			 -fvisibility=default #-Wno-error
	CXXFLAGS_GTFOLD= -march=native -force_cpusubtype_ALL -fPIC -I../include -m64 \
			 -fvisibility=default -Wno-error -lc++ -lc++abi
	LDFLAGS_LIBGMP= -march=native -force_cpusubtype_ALL -rdynamic \
			-Wl,-undefined,error -fPIC -fvisibility=default
	LDFLAGS_LIBGOMP= -march=native -force_cpusubtype_ALL -rdynamic \
			 -fPIC -fvisibility=default -Wno-error
	LDFLAGS_GTFOLD= -march=native -bind_at_load -flat_namespace -force_cpusubtype_ALL \
			-rdynamic -Wl,-undefined,error -fPIC
	FCFLAGS_LIBGOMP=-fPIC -fvisibility=default
else
	CFLAGS_BASE= -g -pedantic -Wl,--no-undefined -shared -fPIC \
			-fno-strict-aliasing -Wall -Wextra -rdynamic -I$(GTFOLDINCL) -m64 \
			-DBUILD_SHARED_LIBS=ON $(PYSPEC) -Wl,-z,defs -fvisibility=default \
			-I$(shell $(READLINK) -f $(LIBGMPDIR)) -I$(shell $(READLINK) -f $(LIBGOMPDIR))

	CFLAGS=$(CFLAGS_BASE)
	CFLAGS_BASE+= -I/usr/include -fno-stack-check -fno-stack-protector -D_FORTIFY_SOURCE=0 
	CFLAGS+= $(shell echo $(shell $(PYCFG) --cflags --includes) | \
		 $(SED) -e 's/-specs=\/usr\/share\/dpkg\/no-pie-compile\.specs //g')
	LDFLAGS_BASE= -Wl,-export-dynamic -Wl,--no-undefined -shared -fPIC \
	      		-fvisibility=default -Wl,-Bsymbolic 
	LDFLAGS_LIBS+= -Wl,-Bstatic \
		       -Wl,--whole-archive $(LIBGOMPSTATIC).a $(LIBGMPSTATIC) -Wl,--no-whole-archive \
		       -Wl,-Bdynamic -ldl -Wl,--no-as-needed -ldl -lpthread -lgmp
	LDFLAGS+= $(shell $(PYCFG) --ldflags --libs) 
	SOLIBOUTFLAGS= -Wl,-soname,$(MODULENAME)
	CFLAGS_LIBGMP= -Wl,--no-undefined -fPIC -pie -m64 -fvisibility=default
	CFLAGS_LIBGOMP= -Wl,--no-undefined -fPIC -pie -I./gcc-include -m64 -fvisibility=default
	CXXFLAGS_LIBGMP= -Wl,--no-undefined -fPIC -pie -m64 -fvisibility=default
	CXXFLAGS_GTFOLD= -O0 -fPIC -pie -I../include -m64 -fvisibility=default
	LDFLAGS_LIBGMP= -Wl,-export-dynamic -fPIC -pie -fvisibility=default
	LDFLAGS_LIBGOMP= -Wl,-export-dynamic -fPIC -pie -fvisibility=default
	LDFLAGS_GTFOLD= -Wl,-export-dynamic -fPIC -pie
	FCFLAGS_LIBGOMP=-fPIC -pie -fvisibility=default
endif

GTFOLD_OBJECTS= \
		$(GTFOLDLIB)/mfe_main.o $(GTFOLDLIB)/loader.o $(GTFOLDLIB)/utils.o \
		$(GTFOLDLIB)/options.o $(GTFOLDLIB)/constraints.o \
        	$(GTFOLDLIB)/global.o $(GTFOLDLIB)/energy.o $(GTFOLDLIB)/algorithms.o \
		$(GTFOLDLIB)/traceback.o $(GTFOLDLIB)/subopt_main.o \
        	$(GTFOLDLIB)/subopt_traceback.o $(GTFOLDLIB)/stochastic-sampling.o \
		$(GTFOLDLIB)/stochastic-sampling-d2.o $(GTFOLDLIB)/algorithms-partition.o \
		$(GTFOLDLIB)/boltzmann_main.o $(GTFOLDLIB)/partition-dangle.o \
        	$(GTFOLDLIB)/partition-func.o $(GTFOLDLIB)/partition-func-d2.o $(GTFOLDLIB)/shapereader.o \
		$(GTFOLDLIB)/pf-shel-check.o $(GTFOLDLIB)/key.o
GTFOLD_PYTHON_OBJECTS= \
	$(OBJBUILDDIR)/ANSIFormatPrinting.o \
	$(OBJBUILDDIR)/BoltzmannSampling.o \
	$(OBJBUILDDIR)/Constraints.o \
	$(OBJBUILDDIR)/ErrorHandling.o \
	$(OBJBUILDDIR)/GTFoldPython.o \
	$(OBJBUILDDIR)/LoadThermoParams.o \
	$(OBJBUILDDIR)/MFEStruct.o \
	$(OBJBUILDDIR)/PartitionFunction.o \
	$(OBJBUILDDIR)/StructureTypes.o \
	$(OBJBUILDDIR)/SuboptStructs.o \
	$(OBJBUILDDIR)/Utils.o

default: make_GTFoldPython

libconfig-reinit: make_runLibDepsConfigureScripts make GTFoldPython

# May ocassionally need to rebuild when autotools versions change:
# $ export _lt_pkgdatadir=/usr/local/share/libtool
# $ sudo ln -s /usr/local/opt/libtool/share/aclocal /usr/local/share/libtool/libltdl/m4
# $ sudo ln -s /usr/local/share/libtool/config /usr/local/share/libtool/libltdl/config
# $ cd ../libgmp-* && autoreconf --install --force --verbose 
# $ aclocal && libtoolize -f && autoheader && automake
# $ cd ../libgomp-* && autoreconf --install --force --verbose
# $ aclocal && libtoolize -f && autoheader && automake
make_runLibDepsConsfigureScripts: 
	@mkdir -p ./Lib
	@cd $(LIBGMPDIR) && rm -f ./shtool && \
		CFLAGS="$(CFLAGS_LIBGMP)" \
		CXXFLAGS="$(CXXFLAGS_LIBGMP)" \
		LDFLAGS="$(LDFLAGS_LIBGMP)" \
		READLINK="$(READLINK)" \
		RANLIB="$(RANLIB)" \
		CONFIG_SHELL=$(BASH) \
		CC="$(CC)" CCLD="$(LD)" CXX="$(CXX)" CXXLD="$(LD)" \
		/bin/bash ./configure --enable-static --disable-shared --with-pic --enable-cxx \
			--disable-assembly gmp_cv_asm_underscore=yes
	@cd $(LIBGOMPDIR) && rm -f ./shtool && \
		touch libtool-dist && cp -Rp libtool-dist libtool && \
		CC="$(CC_LIBGOMP)" \
		FC="$(GFORTRAN)" \
		CFLAGS="$(CFLAGS_LIBGOMP)" \
		LDFLAGS="$(LDFLAGS_LIBGOMP)" \
		FCFLAGS="$(FCFLAGS_LIBGOMP)" \
		READLINK="$(READLINK)" \
		RANLIB="$(RANLIB)" \
		CONFIG_SHELL=$(BASH) \
		LIBTOOL=$(shell which libtool) \
		CC="$(CC)" CCLD="$(LD)" CXX="$(CXX)" CXXLD="$(LD)" \
		/bin/bash ./configure --srcdir=. \
			--enable-static --disable-shared --disable-tls \
			--disable-werror --disable-assembly --disable-dependency-tracking \
			gmp_cv_asm_underscore=yes gcc_cv_use_emutls=no && \
		cp libtool-dist libtool
	@cd $(GTFOLDMAKEDIR) && \
		CFLAGS="$(CFLAGS_GTFOLD)" \
		CXXFLAGS="$(CXXFLAGS_GTFOLD)" \
                LDFLAGS="$(LDFLAGS_GTFOLD)" \
		LIB_OMP="$(shell $(READLINK) -f $(LIBGOMPSTATIC).a)" \
		READLINK="$(READLINK)" \
		CC="$(CC)" CCLD="$(CC)" CXX="$(LD)" CXXLD="$(LD)" \
		./configure

make_libgmp: $(LIBGMPSTATIC)

$(LIBGMPSTATIC):
	@cd $(LIBGMPDIR) && make 

make_libgomp: $(LIBGOMPSTATIC).a $(LIBGOMPSTATIC).so

$(LIBGOMPSTATIC).%:
	@cd $(LIBGOMPDIR) && make libgomp.la 
	#@cd $(LIBGOMPDIR) && ld -r -o tmp.otemp *.o && rm -f tmp.o && \
		nm -u tmp.otemp && ar rvs temp.a tmp.otemp && mv temp.a .libs/libgomp.a && rm -f tmp.otemp
	@/bin/bash BuildScripts/InstallMacRenameSymbols.sh $(LIBGOMPDIR)/.libs/libgomp.a

make_GTFold:
	@cd $(GTFOLDMAKEDIR)/src && \
		make $(GTFOLD_OBJECTS_STRIPPED) CC="$(CC_GTFOLD) $(CFLAGS_BASE)" \
		CCLD="$(CC_GTFOLD) $(LDFLAGS_BASE) $(LDFLAGS_LIBS)" \
		CPP="$(CC_GTFOLD) -E $(CFLAGS_BASE)" \
		CXX="$(CXX_GTFOLD) $(CFLAGS_BASE)" \
		CXXLD="$(CXX_GTFOLD) $(LDFLAGS_BASE) $(LDFLAGS_LIBS)" 
	@cd $(GTFOLDMAKEDIR) && \
		make CC="$(CC_GTFOLD) $(CFLAGS_BASE)" \
		CCLD="$(CC_GTFOLD) $(LDFLAGS_BASE) $(LDFLAGS_LIBS)" \
		CPP="$(CC_GTFOLD) -E $(CFLAGS_BASE)" \
		CXX="$(CXX_GTFOLD) $(CFLAGS_BASE)" \
		CXXLD="$(CXX_GTFOLD) $(LDFLAGS_BASE) $(LDFLAGS_LIBS)" 
	
make_GTFoldPython: make_libgmp make_libgomp make_GTFold \
	$(GTFPYTHONSRC)/GTFoldDataDir.c $(GTFPYTHONLIB)/GTFoldPythonConfig.py \
	$(GTFOLD_PYTHON_OBJECTS) $(OBJBUILDDIR)/$(MODULENAME)
	
$(OBJBUILDDIR)/$(MODULENAME): $(GTFOLD_PYTHON_OBJECTS)
	@$(LD) $(LDFLAGS) \
		$(SOLIBOUTFLAGS) -o $(OBJBUILDDIR)/$(MODULENAME) \
		$(GTFOLD_OBJECTS) $(GTFOLD_PYTHON_OBJECTS)

clean:
	@rm -f $(GTFOLD_PYTHON_OBJECTS) *.code $(GTFOLD_MODULENAME) $(OBJBUILDDIR)/$(MODULENAME) \
		$(GTFPYTHONSRC)/GTFoldDataDir.c $(GTFPYTHONLIB)/GTFoldPythonConfig.py \
		$(OBJBUILDDIR)/* LocalBashConfigInstalled.lock
	@rm -rf ctfiles/ *.txt *.samples *.frequency *.pfarrays *.out *.energy *.ct
	@rm -rf $(GTFPYTHONLIB)/__pycache__ $(GTFPYTHONLIB)/*.pyc
	@cd $(GTFOLDMAKEDIR) && make clean || echo "make clean failed (GTFold) ... "
	@cd $(LIBGMPDIR) && make distclean || echo "make clean failed (libgmp) ... "
	@cd $(LINGOMPDIR) && make distclean || echo "make clean failed (libgomp) ... "
	@make make_runLibDepsConsfigureScripts

local-clean:
	-rm -rf ctfiles/ *.txt *.samples *.frequency *.pfarrays *.out *.energy *.ct
	-rm -f $(GTFOLD_PYTHON_OBJECTS) *.code $(GTFOLD_MODULENAME) $(OBJBUILDDIR)/$(MODULENAME) $(OBJBUILDDIR)/* \
	-rm -rf $(GTFPYTHONLIB)/__pycache__ $(GTFPYTHONLIB)/*.pyc
	-cp $(GTFPYTHONSRC)/GTFoldDataDir.c $(GTFPYTHONSRC)/GTFoldDataDir.c.bak
	-cp $(GTFPYTHONLIB)/GTFoldPythonConfig.py $(GTFPYTHONLIB)/GTFoldPythonConfig.py.bak 
	-rm -rf $(GTFPYTHONSRC)/GTFoldDataDir.c $(GTFPYTHONLIB)/GTFoldPythonConfig.py
	@cd $(GTFOLDMAKEDIR) && make clean

test: make_GTFoldPython
	@rm -rf $(GTFPYTHONLIB)/*.pyc $(GTFPYTHONLIB)/__pycache__
	@$(BASH) ./BuildScripts/RunLibGTFoldPythonUnitTests.sh

install: make_GTFoldPython bash-configure
	@echo "Make sure to run `source ~/.bashrc || ~/.bash_profile` when you are done!"

bash-configure:
	@$(BASH) BuildScripts/InstallSetupBash.sh

git-add-all:
	-git add PythonLibrarySrc/*.{py,py.in} PythonInterfaceSrc/*.{c,cpp,h,c.in}
	-git add Makefile BuildScripts/*.sh Testing/*.{py,sh} Testing/* 
	-git add SampleScripts/*.{py,sh} Utils/*.{sh,py} Docs/*

$(GTFPYTHONSRC)/GTFoldDataDir.c: $(GTFPYTHONLIB)/GTFoldPythonConfig.py
	@$(BASH) BuildScripts/InstallConfigGTFoldDataDirSource.sh

$(GTFPYTHONLIB)/GTFoldPythonConfig.py:
	@$(BASH) BuildScripts/InstallConfigPlatformExports.sh

$(OBJBUILDDIR)/ANSIFormatPrinting.o: $(GTFPYTHONSRC)/PythonConfig.h \
	$(GTFPYTHONSRC)/Utils.h \
	$(GTFPYTHONSRC)/ANSIFormatPrinting.h $(GTFPYTHONSRC)/ANSIFormatPrinting.c
	$(CC) $(CFLAGS) -c $(GTFPYTHONSRC)/ANSIFormatPrinting.c -o $@

$(OBJBUILDDIR)/BoltzmannSampling.o: $(GTFPYTHONSRC)/PythonConfig.h \
	$(GTFPYTHONSRC)/Utils.h $(GTFPYTHONSRC)/ErrorHandling.h \
	$(GTFPYTHONSRC)/BoltzmannSampling.h $(GTFPYTHONSRC)/BoltzmannSampling.cpp
	$(CXX) $(CFLAGS) -c $(GTFPYTHONSRC)/BoltzmannSampling.cpp -o $@

$(OBJBUILDDIR)/Constraints.o: $(GTFPYTHONSRC)/PythonConfig.h \
	$(GTFPYTHONSRC)/Constraints.h $(GTFPYTHONSRC)/Constraints.c
	$(CC) $(CFLAGS) -c $(GTFPYTHONSRC)/Constraints.c -o $@

$(OBJBUILDDIR)/ErrorHandling.o: $(GTFPYTHONSRC)/PythonConfig.h \
	$(GTFPYTHONSRC)/Utils.h \
	$(GTFPYTHONSRC)/ErrorHandling.h $(GTFPYTHONSRC)/ErrorHandling.c
	$(CC) $(CFLAGS) -c $(GTFPYTHONSRC)/ErrorHandling.c -o $@

$(OBJBUILDDIR)/GTFoldPython.o: $(GTFPYTHONSRC)/PythonConfig.h \
	$(GTFPYTHONSRC)/*.h $(GTFPYTHONSRC)/ErrorHandling.c \
	$(GTFPYTHONSRC)/GTFoldPython.c
	$(CC) $(CFLAGS) -c $(GTFPYTHONSRC)/GTFoldPython.c -o $@

$(OBJBUILDDIR)/LoadThermoParams.o: $(GTFPYTHONSRC)/PythonConfig.h \
	$(GTFPYTHONSRC)/ErrorHandling.h $(GTFPYTHONSRC)/Utils.h \
	$(GTFPYTHONSRC)/LoadThermoParams.h $(GTFPYTHONSRC)/LoadThermoParams.cpp
	$(CXX) $(CFLAGS) -c $(GTFPYTHONSRC)/LoadThermoParams.cpp -o $@

$(OBJBUILDDIR)/MFEStruct.o: $(GTFPYTHONSRC)/PythonConfig.h \
	$(GTFPYTHONSRC)/Constraints.h $(GTFPYTHONSRC)/ErrorHandling.h \
	$(GTFPYTHONSRC)/Utils.h \
	$(GTFPYTHONSRC)/MFEStruct.h $(GTFPYTHONSRC)/MFEStruct.c
	$(CC) $(CFLAGS) -c $(GTFPYTHONSRC)/MFEStruct.c -o $@

$(OBJBUILDDIR)/PartitionFunction.o: $(GTFPYTHONSRC)/PythonConfig.h \
	$(GTFPYTHONSRC)/ErrorHandling.h $(GTFPYTHONSRC)/MFEStruct.h \
	$(GTFPYTHONSRC)/PartitionFunction.h $(GTFPYTHONSRC)/PartitionFunction.cpp
	$(CXX) $(CFLAGS) -c $(GTFPYTHONSRC)/PartitionFunction.cpp -o $@

$(OBJBUILDDIR)/StructureTypes.o: $(GTFPYTHONSRC)/PythonConfig.h \
	$(GTFPYTHONSRC)/Utils.h $(GTFPYTHONSRC)/ErrorHandling.h \
	$(GTFPYTHONSRC)/StructureTypes.h $(GTFPYTHONSRC)/StructureTypes.c
	$(CC) $(CFLAGS) -c $(GTFPYTHONSRC)/StructureTypes.c -o $@

$(OBJBUILDDIR)/SuboptStructs.o: $(GTFPYTHONSRC)/PythonConfig.h \
	$(GTFPYTHONSRC)/Utils.h \
	$(GTFPYTHONSRC)/SuboptStructs.h $(GTFPYTHONSRC)/SuboptStructs.c
	$(CC) $(CFLAGS) -c $(GTFPYTHONSRC)/SuboptStructs.c -o $@

$(OBJBUILDDIR)/Utils.o: $(GTFPYTHONSRC)/PythonConfig.h \
	$(GTFPYTHONSRC)/ErrorHandling.h \
	$(GTFPYTHONSRC)/Utils.h $(GTFPYTHONSRC)/Utils.c
	$(CC) $(CFLAGS) -c $(GTFPYTHONSRC)/Utils.c -o $@
