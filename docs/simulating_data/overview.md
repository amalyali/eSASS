# Simulating eROSITA observations with SIXTE

## Brief overview
SIXTE is an end-to-end simulator for X-ray observations. It requires defining an instrument-independent sky model in a 
simput file (this effectively provides details of each source’s sky position, flux in a reference energy band, X-ray spectrum, light curve, image if 
an extended object); and also an instrument description file. In addition, a spacecraft attitude file is required to model the time-dependence of eROSITA’s 
pointing direction.

A photon population is then simulated given this sky model and propagated through the instrument model to produce a 
set of simulated event files. 

Further details, including a usage manual, can be found on the [SIXTE](https://www.sternwarte.uni-erlangen.de/research/sixte/index.php) website,
and also the small section on the [eSASS wiki](https://wiki.mpe.mpg.de/eRosita/ScienceRelatedStuff/sixte).

## Small tricks to speed things up
The following tasks in 1. and 2. should accompany each SIXTE installation:

1. ```simputverify```- this verifies that the SIMPUT file you want to use in your SIXTE simulator is in the correct file format.

2. ```erovis```- given a SIMPUT file and a [spacecraft attitude file](http://www.sternwarte.uni-erlangen.de/research/sixte/data/eRASS_Pc87M55_3dobi_att_remeis.fits.bz2), this computes the time intervals when objects within that simput file are within
eROSITA's FOV, storing this information in a .gti file. This can then be inputted into an ```erosim``` command,
such that SIXTE only simulates eROSITA observations during these good time intervals.

***Check*** the parameters that each task accepts using the command ```plist``` (provided by HEASARC). Changes to input 
parameter names can sometimes not be updated in code documentation.

Further useful tips can be found throughout [Katharina Borm's PhD thesis](http://hss.ulb.uni-bonn.de/2016/4329/4329.pdf), 
though a number of parameters used may have had minor name changes.

## Caveats
Older versions of SIXTE have had incompatibility issues with being analysed using the eSASS software, thus make sure that you use the most recent version of SIXTE you can
if simulating eROSITA data.

* SIXTE currently recreates perfect RA, Dec for photon events.

Further details on discrepancies between SIXTE and eSASS can be found on the eSASS wiki [here](https://wiki.mpe.mpg.de/eRosita/EroCat/eSASSvsSIXTE).

## Calibrating and preparing simulated event files for eSASS analysis

```ero_calevents```: ensure event files have correct extensions for eSASS

```evtool ```: merge event files across CCDs

```radec2xy```: centre the merged event files to a certain RA, Dec



