#### setup.py : Python3 setup script 
#### Author: Maxie D. Schmidt (maxieds@gmail.com)
#### Created: 2020.02.23

from setuptools import setup, Executable, find_packages
from GTFoldPythonConfig import PLATFORM_DARWIN, PLATFORM_LINUX, PLATFORM_VERSION
from os import path

hereSetupFile = path.abspath(path.dirname(__file__))
gtfpDistSrcPythonDir = path.join(path.abspath(path.dirname(__file__)), "../../../Python")

# Get the long description from the README file:
with open(path.join(hereSetupFile, 'README.md'), encoding='utf-8') as f:
    pkgLongDescription = f.read()

gtfpSharedObjDir = gtfpDistSrcPythonDir + "/Lib/"
gtfpDynamicSharedObj = gtfpSharedObjDir + "GTFoldPython.dylib" if PLATFORM_DARWIN else "GTFoldPython.so"
thermoParamsExtraDataDir = gtfpDistSrcPythonDir + "/Testing/ExtraGTFoldThermoData/"
thermoParamsExtraData = []
for dataDir in [ "DefaultGTFold", "DefaultRNAFold", "DefaultRNAFold", "Turner99GTFold", "Turner04GTFold" ]:
     thermoParamsExtraData.append(thermoParamsExtraDataDir + dataDir + "/*.DAT")

setup(
   name               = 'GTFoldPython',
   version            = '1.0.0',
   description        = 'A Python3 wrapper around the GTFold C library functionality.',
   long_description   = pkgLongDescription, 
   long_description_content_type = 'text/markdown', 
   license            = "GNU GPL -- v3",
   author             = 'Maxie D. Schmidt (aka Code Godesss for gtDMMB at GA Tech)',
   author_email       = 'maxieds@gmail.com',
   maintainer_email   = 'gtdmmb@gatech.edu', 
   url                = 'https://github.gatech.edu/gtDMMB/GTFoldPython',
   download_url       = 'https://github.gatech.edu/gtDMMB/GTFoldPython',
   package_dir        = { '' : 'src' },
   packages           = find_packages(where = 'src'),
   install_requires   = [], 
   scripts            = [],
   executables        = [Executable(gtfpDynamicSharedObj, base=PLATFORM_VERSION)], 
   extras_require     = {
        'test': [],
   },
   platforms          = [ "Linux", "MacOS", "MacOS (Mojave/10.14.x)", "Generic Unix" ], 
   classifiers        = [
       'Development Status :: 4 - Beta',
       'Environment :: Console',
       'Intended Audience :: Developers',
       'Intended Audience :: Education',
       'Intended Audience :: End Users/Console',
       'Intended Audience :: Science/Research',
       'Programming Language :: Python :: 3',
       'Programming Language :: Python :: 3.7',
       'Programming Language :: Python :: 3.8', 
       'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
       'Operating System :: MacOS',
       'Operating System :: MacOS :: MacOS X',
       'Operating System :: POSIX',
       'Operating System :: POSIX :: Linux',
       'Operating System :: POSIX :: BSD :: BSD/OS',
       'Operating System :: Unix',
       'Operating System :: OS Independent',
       'Programming Language :: C',
       'Programming Language :: C++',
       'Programming Language :: Other',
       'Programming Language :: Python',
       'Programming Language :: Python :: 3',
       'Programming Language :: Unix Shell',
       'Topic :: Documentation',
       'Topic :: Education', 
       'Topic :: Education :: Testing',
       'Topic :: Other/Nonlisted Topic',
       'Topic :: Scientific/Engineering',
       'Topic :: Scientific/Engineering :: Bio-Informatics',
       'Topic :: Scientific/Engineering :: Mathematics',
       'Topic :: Scientific/Engineering :: Visualization',
       'Topic :: Scientific/Engineering :: Information Analysis',
       'Topic :: Software Development :: Documentation',
       'Topic :: Software Development :: Libraries',
       'Topic :: Software Development :: Libraries :: Python Modules',
       'Topic :: Software Development :: Testing',
       'Topic :: System :: Installation/Setup',
       'Topic :: System :: Software Distribution',
       'Topic :: Utilities',
   ],
   keywords           = 'GTFold RNAfold ViennaRNA RNAstructure rna mfe sampling subopt',
   python_requires    = '>=3.*, !=2.7.*, !=2.*, <4',
   project_urls       = {
        'Install Notes'             : 'https://github.gatech.edu/gtDMMB/GTFoldPython/blob/master/Python/Docs/Install.md',
        'Bug Reports'               : 'https://github.gatech.edu/gtDMMB/GTFoldPython/issues',
        'Funding'                   : 'https://sites.google.com/site/christineheitsch/research',
        'Developer GitHub'          : 'https://github.com/maxieds',
        'Developer Webpage'         : 'http://people.math.gatech.edu/~mschmidt34/', 
        'Source'                    : 'https://github.gatech.edu/gtDMMB/GTFoldPython/Python',
        'Organization GH (Private)' : 'https://github.gatech.edu/gtDMMB', 
        'Organization GH (Public)'  : 'https://github.com/gtDMMB',
    },
   package_data         = { 
           'GTFoldPython'   :   thermoParamsExtraData, 
           'Docs'           :   [ gtfpDistSrcPythonDir + "/Docs/*.md" ],
           'Utils'          :   [ gtfpDistSrcPythonDir + "Utils/*.py" ],
   },
   include_package_data = True, 
   develop              = True,
   zip_safe             = False
)
