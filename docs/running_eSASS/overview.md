# Running eSASS
## AGN equatorial skyfield example

There is an [AGN equatorial skyfield](../../scripts/agn_equatorial_skyfield) repository, which contains a set of scripts
that:

1. ```generate_simulated_data.py```: Run a SIXTE simulation of an AGN equatorial skyfield, starting from a simput file .
2. ```preprocess_event_files.py```: Preprocess the simulated event files to make compatible with eSASS.
3. ```run_esass_analysis.py```: Run the eSASS analysis of the event files.

with example datasets found in ```/home/amalyali/data1/eSASS/data``` from the ds machines. 


## Encountered an error?
***Check*** the parameters that each task accepts using the command ```plist``` (provided by HEASARC). Changes to input 
parameter names can sometimes not be updated in code documentation.

