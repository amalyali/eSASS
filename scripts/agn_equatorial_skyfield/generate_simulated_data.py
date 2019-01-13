"""
Simulate eROSITA event data from sky model using SIXTE.
A. Malyali, 2019. amalyali@mpe.mpg.de
"""
import subprocess
import os
import errno


class Simulator:
    """
    SIXTE simulator for eROSITA observations.
    1. Compute GTI file for given simput
    2. Simulate eROSITA observations of simput, using GTI to speed things up.
    """
    def __init__(self, with_bkg_par, t_start, exposure, seed, simput):
        """
        :param with_bkg_par: Simulate with particle background.
        :param t_start: Start time of simulation. Input units of [s]
        :param exposure: Length of time to simulate for after t_start
        :param seed: Seed for random number generator.
        :param simput: Simput file (ie. the sky model)
        """
        self._with_bkg_par = bool(with_bkg_par)
        self._t_start = float(t_start)  # secs
        self._exposure = float(exposure)
        self._seed = int(seed)
        self._simput = simput
        self._data_dir = "../../data/agn_equatorial_skyfield/events/"

    def make_event_directory(self):
        """
        Check for whether a directory exists and create if not.
        """
        try:
            os.makedirs(self._data_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    def compute_gti(self):
        """
        Compute the GTI (good time interval) file given the simput file.
        Use this as input to SIXTE call for reducing computational expense.
        """
        gti_file = "%s/agn.gti" % self._data_dir

        cmd = ["ero_vis",
               "Attitude=../../data/eRASS_Pc87M55_3dobi_att_remeis.fits",
               "Simput=%s" % self._simput,
               "RA=0.0",
               "Dec=0.0",
               "GTIfile=%s" % gti_file,
               "TSTART=%f" % self._t_start,
               "Exposure=%f" % self._exposure,
               "dt=1.0",
               "visibility_range=1.0",
               "clobber=yes"
               ]

        subprocess.check_call(cmd)

    def run_sixte(self):
        """
        Launch erosim from python.
        """
        prefix = "%s/agn_" % self._data_dir

        cmd = ["erosim",
               "Simput=%s" % self._simput,
               "Prefix=%s" % prefix,
               "Attitude=../../data/eRASS_Pc87M55_3dobi_att_remeis.fits",
               "RA=0.0",
               "Dec=0.0",
               "GTIFile=%s/agn.gti" % self._data_dir,
               "TSTART=%s" % self._t_start,
               "Exposure=%s" % self._exposure,
               "MJDREF=51543.875",
               "dt=1.0",
               "Seed=%s" % self._seed,
               "clobber=yes",
               "chatter=3"
               ]

        if self._with_bkg_par is True:
            cmd.append("Background=yes")
        else:
            cmd.append("Background=no")

        subprocess.check_call(cmd)

    def run_all(self):
        """
        Run SIXTE simulation of eRASS 1
        """
        self.make_event_directory()
        self.compute_gti()
        self.run_sixte()


# -------
# Define parameters for simulation
bkg = 1
t_start = 0.0
exposure = 15750000
seed = 42
simput_file = '../../data/raw/simput/agn/eRosita_eRASS8_simput_2M.fits'

# Launch...
Simulator(bkg, t_start, exposure, seed, simput_file).run_all()