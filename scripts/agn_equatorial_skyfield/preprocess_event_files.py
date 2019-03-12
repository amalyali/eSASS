"""
Preprocess the simulated event files to make compatible with eSASS.

A. Malyali, 2019. amalyali@mpe.mpg.de
"""
import subprocess

ccds = [1, 2, 3, 4, 5, 6, 7]


class PrepareForEsass:
    def __init__(self, ra_cen, dec_cen):
        """
        :param ra_cen: Right ascension of skyfield center position
        :param dec_cen: Declination of skyfield center position
        """
        self._data_dir = "../../data/agn_equatorial_skyfield/events"
        self._ra_cen = ra_cen
        self._dec_cen = dec_cen

    def cal_events(self):
        """
        Prepare event lists from SIXTE simulation for the eSASS pipeline.
        Calibrate event lists from SIXTE (mainly to ensure we have the correct extensions for the FITS files).
        """
        for ii in ccds:
            uncal_file = '%s/agn_ccd%s_evt.fits' % (self._data_dir,  ii)
            cal_file = '%s/cal_agn_ccd%s_evt.fits' % (self._data_dir,  ii)

            cmd = ["ero_calevents",
                   "Projection=AIT",
                   "Attitude=../../data/eRASS_Pc87M55_3dobi_att_remeis.fits",
                   "clobber=yes",
                   "EvtFile=%s" % uncal_file,
                   "eroEvtFile=%s" % cal_file,
                   "CCDNr=%i" % ii,
                   "RA=%s" % self._ra_cen,
                   "Dec=%s" % self._dec_cen  # center of skyfield
                   ]
            print(cmd)
            subprocess.check_call(cmd)

            cmd = ["fparkey",
                   "fitsfile=%s[1]" % cal_file,
                   "keyword=PAT_SEL",
                   "value=15",
                   "add=yes"
                   ]
            print(cmd)
            subprocess.check_call(cmd)

    def merge_cal_events_across_ccds(self):
        """
        1. Merge all calibrated event files from all CCDs.
        2. Centre ra dec 2 xy
        """
        unmerged_cal_evt_files = []
        for ii in ccds:
            unmerged_cal_evt_files.append('%s/cal_agn_ccd%s_evt.fits' % (self._data_dir,  ii))

        merged_cal_evt_file = "%s/merged_agn.fits" % self._data_dir

        cmd = ["evtool",
               "eventfiles=%s" % ' '.join([str(x) for x in unmerged_cal_evt_files]),
               "outfile=%s" % merged_cal_evt_file,
               "pattern=15",
               "clobber=yes"
               ]
        print(cmd)
        subprocess.check_call(cmd)

        cmd = ["radec2xy",
               "file=%s" % merged_cal_evt_file,
               "ra0=%s" % self._ra_cen,
               "dec0=%s" % self._dec_cen
               ]
        print(cmd)
        subprocess.check_call(cmd)

    def prep_and_merge(self):
        self.cal_events()
        self.merge_cal_events_across_ccds()


if __name__ == '__main__':
    # Define parameters for simulation
    ra_cen = 1.5
    dec_cen = 0.0

    # Preprocess event files...
    PrepareForEsass(ra_cen, dec_cen).prep_and_merge()