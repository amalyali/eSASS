# Installation

There are two different types of eSASS installation:

1. eSASS devel(opment) (*recommended*)

2. An eSASS user release

The development version is recommended over older user releases as bugs identified within the latest user release may have been fixed.
If you plan to base your work on the ds machines at MPE, then your best option is to follow the steps presented for setting
up eSASS devel.

## eSASS devel
This will be the most up-to-date version of eSASS. To setup the code for usage on the ds machines at MPE, simply run the line
from your terminal:

```
source /utils/lheasoft-setup.sh
source /home/erosita/sw/sass-setup.sh eSASSdevel
```

which should then print on your terminal:
```
SASS_ROOT: /home/erosita/sw/eSASSdevel
package SASS
package EROSITA
setup complete
```

## eSASS user releases
From the ds machines at MPE, setting up of the code is similar to the eSASSdevel case. 
For example, to install the most recent user release from 16/4/18:

```
source /home/erosita/sw/sass-setup.sh eSASSusers_180416
```

Alternatively one may set up a local installation; those interested are referred to the [installation page](https://wiki.mpe.mpg.de/eRosita/eSASSinstall) on the eSASS wiki.

## MPCDF cluster 

In addition, if you're interested in using eSASS on the MPCDF computing cluster, get in contact with [Adam Malyali](http://www.mpe.mpg.de/person/54593/1302618). 
