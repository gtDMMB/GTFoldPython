# Types of constraints used in GTFold and GTFoldPython

## Vienna RNAfold style constraint strings

* **|** : paired with another base
* **.** : no constraint at all
* **x** : base must not pair
* &lt; : base i is paired with a base j *less than* i
* &gt; : base i is paired with a base j *greater than* i
* matching brackets **( )**: base i pairs base j

For example, a sample constraint string for the following nucleotide sequence can be constructed 
([see guidelines](https://www.tbi.univie.ac.at/RNA/tutorial/#verbatim-34)): 
```
GCCGUGAUAGUUUAAUGGUCAGAAUGGGCGCUUGUCGCGUGCCAGAUCGGGGUUCAAUUCCCCGUCGCGGCGCCA
....<<<<<..((((((.>>>>>..........(((((.......)))))....))))))......
```

There is a script located in the GTFoldPython directory ``Utils/ForcedDOTToConstraints.py`` 
that can be used to convert a constraint 
string like the above into a list of F/P-style constraints accepted by GTFold. The first argument to the script is the 
(bash shell quoted) constraint string. 

## F/P constraint syntax:

The constraints given in constraint file should be formated as follows:
```
P i j k      Prohibits the formation of base pairs (i,j) (i+1,j-1) ... (i+k-1, j-k+1).
F i j k      Forces the formation of base pairs (i,j) (i+1,j-1) ... (i+k-1, j-k+1).
P i 0 k      Makes the bases from i to i+k-1 single stranded bases.
F i 0 k      Forces the bases from i to i+k-1 to be paired
             (without specifying their pairing parterns).
```
Note that k must be positive, and j-i must be at least 4.

## SHAPE constraint syntax:

For file format specs, see [this link](http://rna.urmc.rochester.edu/Releases/5.8/manual/Text/File_Formats.html#SHAPE). 

SHAPE values should be given in a file with two single-space-delimited columns,
for example:
--------
1 0.1
2 0.001
3 1.67
etc.,
--------
where the first column is the nucleotide position (INT) and the second column is the
SHAPE reactivity (DOUBLE) for that position. The file should have no header. Not all
positions need to be included in the file, and the values do not need to be in order of
increasing position. Negative SHAPE reactivities are ignored.

## Python Example (in `ipython3`):

```python
>>> import GTFoldPythonImportAll
>>> fpCons = GTFPUtils.ReadFPConstraintsFromFile("file.cons")
>>> GTFP.GetMFEStructure("ACGUACGU", fpCons)
>>> shapeCons = GTFPUtils.ReadSHAPEConstraintsFromFile("file.shape")
>>> GTFP.GetMFEStructureSHAPE("ACGUACGU", shapeCons)
```


