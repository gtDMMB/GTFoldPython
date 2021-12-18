# TODO: Working tasks and items for the code

## List of features that should eventually get integrated into the code 

* Save exactly all parameters used to load the thermo params (and do not reset these structures 
once loaded unless a FORCE parameter is set). The idea is to reduce the amount of time spent initializing 
these time consuming data structures. 
* The above, possibly with checking time-stamps and/or hashes on the files for the application where the 
thermo data will be frequently changing in realtime. 
* Test cases and unit tests
* Add a ``WRITEAUXFILES`` extern'ed variable in GTFold to set
* Need to test recent code on a Mac platform
* Check that in the returned BPP tuples, we are only providing the one-sided (lower triangular) versions of 
  the base pair probabilities
* Get the unit tests to pass with the *Turner04* parameters with "close enough" passing values obtained with 
  our versions of the files. NOTE: Afaf has pointed out that since the GTFold calculations are energy-based, 
  and we do not have the exact full list of parameter settings used by Vienna's RNAfold to generate her 
  test case data posted on Slack, there may very well be reasonable small variations on the MFE values 
  returned here. She points out that the MFE DOT **structures**, on the otherhand, should be expected to 
  match ViennaRNA's output exactly either way...
* Implement the following Python library methods (or something close to them):
```python
GTFP.SetSequenceName(string)
GTFP.LockThermodynamicParameters()
GTFP.UnlockThermodynamicParameters()
```

## Known bugs to work out in the current code

* The float value ``inf`` is consistently returned by the Boltzmann sampling functions, even though the 
  corresponding probability values printed as debugging information when running GTFold are not this value
* Check the ``max_num_structs`` variable to make sure it is &gt;&gt;1 (Perhaps this is the reason / problem 
  with the current subopt structures function not correctlt returning a list of subopt structures? ... )



