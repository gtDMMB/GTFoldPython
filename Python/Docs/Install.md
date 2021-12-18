# Install instructions

## Platform specific install instructions

### Dependencies: Linux (Debian-based, e.g., Ubuntu or Mint)

To get the necessary Python3 development and other C source headers 
installed, run the following:
```bash
$ sudo apt-get install python3-dev shtool m4 texinfo libgomp1 libgmp-dev
$ sudo apt-get install python3-numpy
```
Next, check the version of the ``gcc`` compiler you are running by typing
```bash
$ gcc --version
gcc (Ubuntu 9.2.1-9ubuntu2) 9.2.1 20191008
Copyright (C) 2019 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
```
If you are running an older distribution using a version of ``gcc`` prior to ``gcc-8``, then 
you will need to upgrade your GNU C compiler:
```bash
$ apt-cache search gcc-8 gcc-9
$ sudo apt-get install gcc-8
$ which gcc && ls -l $(which gcc)
/usr/bin/gcc
lrwxrwxrwx 1 root root 5 Jan 28 07:13 /usr/bin/gcc -> gcc-9
$ sudo rm /usr/bin/gcc
$ sudo ln -s gcc-8 /usr/bin/gcc
$ gcc --version
```
All set!

### Dependencies: Mac OSX 10.14.x (codename Mojave)

```bash
$ brew install coreutils gnu-sed python@3 shtool
$ brew install autoconf automake libtool
$ brew install binutils
```

#### Installing a recent, sane version of Python3 with debugging symbols

I created a new formula for this with ``brew`` in our public gtDMMB tap. Press "i" to ignore any errors
that come up when running the following install command:
```bash
$ brew update && brew install --build-from-source --verbose --debug gtdmmb/core/python-dbg@3.7
```
It's important to notice which particular python binary version is the special one we are linking against 
(and there are now several). Consider examining the following output:
```bash
$ /usr/local/Cellar/python-dbg\@3.7/3.7.6_13/bin/python3-config --ldflags
-L/usr/local/Cellar/python-dbg@3.7/3.7.6_13/Frameworks/Python.framework/Versions/3.7/lib/python3.7/config-3.7dm-darwin -lpython3.7dm -ldl -framework CoreFoundation
```
You will then notice that our Python binary should be called ``python3.7dm`` (in particular, in the path 
``/usr/local/Cellar/python-dbg\@3.7/3.7.6_13/bin/python3.7dm``). Omitting the trailing **.7dm** fromthe standard issue ``python3`` 
command next will cause you undue headaches! We will create an alias to this ``python3.7dm`` binary location to keep things short 
in the next step for you. 

## Installing GTFoldPython from source

To compile and resolve the Python library dependencies, run the following:
```bash
$ cd ~
$ git clone https://github.gatech.edu/gtDMMB/GTFoldPython.git
$ cd GTFoldPython/Python
$ make clean && make
$ make bash-configure
$ touch ~/.bashrc && source ~/.bashrc || source ~/.bash_profile
$ make test
```
You can also try running the following from within the same directory:
```bash
$ python3dbg Testing/RunBasicInterface.py
```
This file is a good starting point for howto use the library. 

Now if all of the tests run smoothly, you can continue on to installing the 
[rnadb-construction-script](https://github.gatech.edu/gtDMMB/RNADB-construction).

