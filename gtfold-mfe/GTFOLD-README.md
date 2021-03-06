# GTfold: A Scalable Multicore Code for RNA Secondary Structure Prediction

(C) 2007-2011, David A. Bader
                College of Computing, Georgia Institute of Technology
               Christine E. Heitsch
                School of Mathematics, Georgia Institute of Technology
               Stephen C. Harvey
                School of Biology, Georgia Institute of Technology
               And various contributing authors

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

The prediction of the correct secondary structures of large RNAs is
one of the unsolved challenges of computational molecular biology.
Among the major obstacles is the fact that accurate calculations scale
as O(n^4), so the computational requirements become prohibitive as the
length increases.  Existing folding programs implement heuristics and
approximations to overcome these limitations. GTfold, a parallel
multicore and scalable program, is one to two orders of magnitude
faster than the de facto standard programs and achieves comparable
accuracy of prediction. Development of GTfold opens up a new path for
the algorithmic improvements and application of an improved
thermodynamic model to increase the prediction accuracy.

This work was supported in part by National Institutes of Health grant
NIH NIGMS R01 GM083621, and by NSF Grants CNS-0614915 and
DBI-04-20513. Additionally, the research of Christine E. Heitsch,
Ph.D., is supported in part by a Career Award at the Scientific
Interface (CASI) from the Burroughs Wellcome Fund (BWF). 

Additional contributors to GTfold's implementation include 
Georgia Tech graduate students Sainath Mallidi, Amrita Mathuriya, 
and Prashant Gaurav, undergraduates Joshua Anderson and Andrew Ash
and visiting students Gregory Nou, Sonny Hernandez, Manoj Soni,
and Zsuzsanna Sukosd.

# INSTALLATION (Typical from source) --
Please execute the following commands
```
  gtar zxvf gtfold-version.tar.gz
  cd gtfold-version
```
1. Installing with the root user
  1. ./configure 
  2. make
  2. make install  

2. Installing in a local directory
  1. ./configure --prefix=(Full path of the directory where gtfold will be installed.)
  2. make
  3/ make install

Also, you can specify C and C++ compiler using the CC and CXX variables. 
For example -
```  
./configure CC=gcc CXX=g++ --prefix=/home/username/gtfold
```
Note: After running make install, you should see a directory bin containing executable 'gtfold'. To run gtfold as described in the documentation, you need to make three symbolic links:
1. cd bin
2. ln -sf gtfold gtmfe
3. ln -sf gtfold gtsubopt
4. ln -sf gtfold gtboltzmann

# Installation (Ubuntu 64-bit Linux) -- Creating the libGTFold static library

```
$ sudo apt-get install libgmp3-dev libiomp-dev libgomp1
$ ./configure --enable-64bit CXXFLAGS="-fPIC -fno-strict-aliasing" LIBS="-Wl,--as-needed -L/usr/lib/x86_64-linux-gnu -lgmp -lgmpxx -L/usr/lib/gcc/x86_64-linux-gnu/8 -lgomp -static -lpthread -ldl"
$ make
$ ar rcs libgtfold_x86_64-linux-gnu.a src/*.o
``` 

# Understanding Source Code --
1. Please use a program called CSCOPE to get understanding of the source code. It may be preinstalled in your Linux system or get it from 
    http://cscope.sourceforge.net/
2. Please refer Chapter 3 of Mirela Stefania Andronescu's Masters thesis understanding of calculating the energy of various types of loops.
    http://www.cs.ubc.ca/grads/resources/thesis/Nov03/Mirela_Andronescu.pdf
3. You can look Chapter 4 to understand the thermodynamic recurssion formulas. Also, pesudocode given in the paper should be helpful.
4. To understand traceback, you may want to look at the following publication -
    Biopolymers, Volume 49 Issue 2, Pages 145 - 165
    Complete suboptimal folding of RNA and the stability of secondary structures
    Stefan Wuchty, Walter Fontana, Ivo L. Hofacker, Peter Schuster
5. Please look at the paper here -
    A. Mathuriya, D.A. Bader, C.E. Heitsch, and S.C. Harvey, 
    ``GTfold: A Scalable Multicore Code for RNA Secondary Structure Prediction,''  
     24th Annual ACM Symposium on Applied Computing (SAC), Computational Sciences Track, 
     Honolulu, HI, March 8-12, 2008. 

# Version History:
```
1.0.  16 August 2008  Base Version
1.1.  17 August 2008  Converted DP tables from static to dynamic allocation
1.2.  18 August 2008  Fixed a bug with chPair rnap2/continue introduced in gtfold-1.1
		     Changed to 0-based indexing for dangle, stack, tskth, tskti, 
                      iloop22, iloop21, iloop11.
1.3.  20 August 2008  Changed RNA mapping to 0 based
1.4   23 August 2008  Flattened arrays stack, tskth, tskti.
1.5   29 August 2008  Added OpenMP parallelization
1.6    4 October 2008  Changed calcW function in algorithms.c to have Wim1 = MIN (W[i-1],0) in place of Wim1 = W[i-1].
		      Initialized W[i] values to INFINITY_ in function initTables in place of 0.
		      loader.cc file is modified to open the data files in read mode instead of read/write mode.
		      The sequence file is opened in read mode instead of write mode in file main.cc in main function.
		      The version directly produces ct files from the sequence in the working directory.
1.7  22 October 2008   Corrected a bug in file loader.cc, function - initInt22Values
1.8  03 January 2009   (1) Adding functionality of Internal Loop Speedup Algorithm ( ILSA )  
                      (2) Corrected one invalid memory access bug, in function calcWM() of file algorithms.c
                      (3) MFE will be printed in correct floating point format - change in file main.c
                      (4) Converted constant 30, 31, 32 of function calcVBI() in terms of MAXLOOP constant
                      (5) Modified gtfold command line options. Run "gtfold -help" to see the usage.
		      (6) Now, multConst array contains the multiloop penalty constants. Functions for multicloop energy 
                          calculations are modified to read the penalties from this array.
1.9  15 January 2009   Documented GTfold with various comments.  
1.10 22 January 2009   More documentation 
1.11 30 Spetember 2009 Added Better support for input sequence files (removing intermediate white spaces)
1.12 5 Mar 2010   Added support for constraints, forcing, prohibitng a base pair, specifying single stranded regions.
            Modified gtfold command line options. Run "gtfold -help".
1.13 25 Mar 2010  Added a toggle switch for preventing isolated base pairs
            Handling constraints has been changed drastically and it produces much better output now.
            Modified gtfold command line options. Run "gtfold -help".
1.14 30 Mar 2010  Added support to change data directory on fly.
            Support for generating binaries which reads the data files from its subdir data/
            More robust handling of input file sequences
            Changed the output print sequence of GTfold, now also prints in Vienna format
            Modified the command line options. Run "gtfold -help" to see the usage.
            Changed the output format of traceback to print loop energies instead of running energy.
            Changed the initialized values of W[i] to 0 to play nice with the constraints.
1.15 18 May 2010  Fixed a nasty bug with reading constraints by increasing the length of string to 100 that reads the lines from sontraints file.
1.16 20 May 2010  Fixed another nasty bug with prohibited constraints handling.
            Earlier not used to update the WM array if a base pair is prohibited which is causing GTfold to trace partial structure.
            Some documentation added.
2.0 11 July 2011                      
            Optimized the code to enable faster multiloop calculations 
            Added -d, --dangle to allow treatment of dangling end energies based on user input 
            Added -m  --mismatch to enable terminal mismatch calculations
            Added -o, --output, , -w --workdir options to allow to write output files/directories with desired name 
            Added -p  --paramdir to allow user to provide custom parameters		
            Added -t, --threads to limit number of threads used
            Added -v, --verbose to print loop-by-loop energy decomposition and confirm that constraints are satisfied
            Added --prefilter to prohibit any basepair which does not have appropriate neighboring nucleotides 
                    such that it could be part of a helix of length INT
            Added --rnafold to run GTfold in RNAfold default mode (ViennaPackage version 1.8.5)
            Added --unafold to run GTfold in UNAfold default mode (version 3.8)
            Added --subopt NUM (Beta only) to produce all suboptimal structures whose energies are within NUM of the MFE 
            Added --bpp (Beta only) which outputs basepair probabilities based on the partition function 
            Added --useShape (Beta only) which allows the user to incorporate SHAPE-type data
```
