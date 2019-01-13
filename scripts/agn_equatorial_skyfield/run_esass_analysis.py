#!/usr/bin/python
"""
eSASS analysis of SIXTE simulated (and preprocessed) event data.
Adapted from demo script written by eSASS team (Christoph Grossberger?)
"""
import os, os.path, errno, subprocess

config = "001"
version = "002"


class EsassPipeline():
    def __init__(self):
        self._data_dir = "../../data/agn_equatorial_skyfield"

    def run_pipeline(self):
        """
        Run all steps of the eSASS analysis in required order.
        """
        subdir = self._data_dir
        evt_dir = "%s/events" % subdir
        infile = "%s/merged_agn.fits" % evt_dir
        outfile = "products"
        outfile_suffix = "post"
        suffix_srctool = "_001_t%s" % version

        product_dir = "%s/%s" % (subdir, outfile)
        try:
            os.makedirs(product_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        srctool_dir = "%s/srctool_products" % product_dir
        try:
            os.makedirs(srctool_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        # Choose energy bands for analysis
        emin_ev = [100, 500, 2000, 5000]
        emax_ev = [500, 2000, 5000, 10000]
        emin_kev = [0.1, 0.5, 2.0, 5.0]
        emax_kev = [0.5, 2.0, 5.0, 10.0]
        eband = ["1", "2", "3", "4"]
        ccd = [1, 2, 3, 4, 5, 6, 7]

        # Subselect eSASS tasks to perform
        eband_selected = [0, 1, 2, 3]
        do_evtool = True
        do_expmap = True
        do_ermask = True
        do_erbox_local = True
        do_erbackmap = True
        do_erbox_m = True
        do_ermldet = True
        do_catprep = True
        do_srctool = False

        expmaps = []
        expmap_all = []
        infile_expmap = []
        emin = []
        emax = []
        emin_ev_str = []
        emax_ev_str = []
        outfile_evtool = []
        cheesemask = []
        bkgimage = []
        srcmaps = []

        """
        Image each of the four energy bands.
        Construct exposure map for each CCD event list +
        a merged exposure map.
        """
        for ii in range(len(eband_selected)):
            index = eband_selected[ii]
            outfile_evtool.append("%s02%s_EventList_%s.fits" % (os.path.join(subdir, outfile), eband[index], outfile_suffix))
            srcmaps.append("%s02%s_SourceMap_%s" % (os.path.join(subdir, outfile), eband[index], outfile_suffix))
            print(outfile_evtool, os.path.join(subdir, outfile), eband[index], outfile_suffix)
            cmd = ["evtool",
                   "eventfiles=%s" % (infile),
                   "outfile=%s" % (outfile_evtool[ii]),
                   "emin=%s" % (emin_kev[index]),
                   "emax=%s" % (emax_kev[index]),
                   "image=yes",
                   "rebin=128",
                   "size=4096",
                   "pattern=15"
                   ]
            print (cmd)
            if do_evtool == True:
                subprocess.check_call(cmd)

            infile_expmap.append(outfile_evtool[ii])

            for jj in range(len(ccd)):  # if making exp map for each ccd
                expmaps.append("%s%d2%s_ExposureMap_%s" % (os.path.join(subdir, outfile), ccd[jj], eband[index], outfile_suffix))
            expmap_all.append("%s02%s_ExposureMap_%s" % (os.path.join(subdir, outfile), eband[index], outfile_suffix))
            emin.append("%f" % (emin_kev[index]))
            emax.append("%f" % (emax_kev[index]))
            emin_ev_str.append("%ld" % (emin_ev[index]))
            emax_ev_str.append("%ld" % (emax_ev[index]))

            print('expmap_all ', (" ").join(expmap_all))
            print((" ").join(emin))

        if do_expmap == True:
            for kk in range(len(eband)):
                print(emin_kev[kk])
                cmd = ["expmap",
                       "inputdatasets=%s" % (infile),
                       "templateimage=%s[0]" % (infile_expmap[kk]),
                       "emin=%s" % (emin_kev[kk]),
                       "emax=%s" % (emax_kev[kk]),
                       "withvignetting=no",  # not supported atm.
                       "withmergedmaps=yes",
                       #"withsinglemaps=no",
                       # "expmaps=%s" %((" ").join(expmaps)),
                       "mergedmaps=%s" % (expmap_all[kk])
                       ]
                print(cmd)
                subprocess.check_call(cmd)
            print('final test')


        # ------------------------------------------------------------------------------
        """
        Detection mask.
        """
        detmask = "%s020_DetectionMask_%s" % (os.path.join(subdir, outfile), outfile_suffix)
        cmd = ["ermask",
               "expimage=%s" % (expmap_all[0]),
               # use the first exposure maps calculated for that skyfield, independent of the energy band
               "detmask=%s" % (detmask),
               "threshold1=0.2",
               "threshold2=0.9",  # 1.0
               "regionfile_flag=no"
               ]
        if (do_ermask == True):
            if (os.path.isfile(detmask) == True):
                os.remove(detmask)
            print(cmd)
            subprocess.check_call(cmd)


        boxlist_l = "%s020_BoxDetSourceListL_%s" % (os.path.join(subdir, outfile), outfile_suffix)

        cmd = ["erbox",
               "images=%s" % ((" ").join(outfile_evtool)),
               "boxlist=%s" % (boxlist_l),
               "expimages=%s" % ((" ").join(expmap_all)),
               "detmasks=%s" % (detmask),
               "emin=%s" % ((" ").join(emin_ev_str)),
               "emax=%s" % ((" ").join(emax_ev_str)),
               "hrdef=",
               "ecf=1.0 1.0 1.0 1.0",
               "nruns=3",
               "likemin=6.0",
               "boxsize=4",
               "compress_flag=N",
               "bkgima_flag=N",
               "expima_flag=Y",
               "detmask_flag=Y"
               ]

        if (do_erbox_local == True):
            if (os.path.isfile(boxlist_l) == True):
                os.remove(boxlist_l)
            print(cmd)
            subprocess.check_call(cmd)

        # ------------------------------------------------------------------

        for ii in range(len(eband_selected)):
            index = eband_selected[ii]
            cheesemask.append("%s02%s_CheeseMask_%s" % (os.path.join(subdir, outfile), eband[index], outfile_suffix))
            bkgimage.append("%s02%s_BackgrImage_%s" % (os.path.join(subdir, outfile), eband[index], outfile_suffix))

            cmd = ["erbackmap",
                   "image=%s" % (outfile_evtool[ii]),
                   "expimage=%s" % (expmap_all[ii]),
                   "boxlist=%s" % (boxlist_l),
                   "detmask=%s" % (detmask),
                   "cheesemask=%s" % (cheesemask[ii]),
                   "bkgimage=%s" % (bkgimage[ii]),
                   "idband=%s" % (eband_selected[ii]),
                   "scut=0.001",
                   "mlmin=6",  # GL: 0
                   "maxcut=0.5",
                   "fitmethod=smooth",
                   "nsplinenodes=36",
                   "degree=2",
                   "smoothflag=yes",
                   "smoothval=15.",
                   "snr=40.0",
                   "excesssigma=10000.",
                   "nfitrun=1",
                   "cheesemaskflag=Y"
                   ]
            if (do_erbackmap == True):
                if (os.path.isfile(cheesemask[ii]) == True):
                    os.remove(cheesemask[ii])
                if (os.path.isfile(bkgimage[ii]) == True):
                    os.remove(bkgimage[ii])
                print(cmd)
                subprocess.check_call(cmd)

        # --------------------------------------------------------------------------

        boxlist_m = "%s020_BoxDetSourceListM_%s" % (os.path.join(subdir, outfile), outfile_suffix)
        cmd = ["erbox",
               "images=%s" % ((" ").join(outfile_evtool)),
               "boxlist=%s" % (boxlist_m),
               "expimages=%s" % ((" ").join(expmap_all)),
               "detmasks=%s" % (detmask),
               "bkgimages=%s" % ((" ").join(bkgimage)),
               "emin=%s" % ((" ").join(emin_ev_str)),
               "emax=%s" % ((" ").join(emax_ev_str)),
               "hrdef=",
               "ecf=1.0 1.0 1.0 1.0",
               "nruns=3",
               "likemin=6.",  # GL: 4
               "boxsize=4",
               "compress_flag=N",
               "bkgima_flag=Y",
               "expima_flag=Y",
               "detmask_flag=Y"
               ]
        if (do_erbox_m == True):
            if (os.path.isfile(boxlist_m) == True):
                os.remove(boxlist_m)
            print(cmd)
            subprocess.check_call(cmd)

        # ----------------------------------------------------------------------------

        mllist = "%s020_MaxLikSourceList_%s" % (os.path.join(subdir, outfile), outfile_suffix)
        cmd = ["ermldet",
               "mllist=%s" % (mllist),
               "boxlist=%s" % (boxlist_m),
               "images=%s" % ((" ").join(outfile_evtool)),
               "expimages=%s" % ((" ").join(expmap_all)),
               "detmasks=%s" % (detmask),
               "bkgimages=%s" % ((" ").join(bkgimage)),
               "emin=%s" % ((" ").join(emin_ev_str)),
               "emax=%s" % ((" ").join(emax_ev_str)),
               "hrdef=",
               "ecf=1.0",
               "likemin=6.",  # TODO: Are these good values?
               "extlikemin=3.",
               "compress_flag=N",
               "cutrad=15.",
               "multrad=15.",
               "extmin=1.5",
               "extmax=30.0",
               "bkgima_flag=Y",
               "expima_flag=Y",
               "detmask_flag=Y",
               "extentmodel=beta",
               "thres_flag=N",
               "thres_col=like",
               "thres_val=30.",
               "nmaxfit=3",
               "nmulsou=2",
               "fitext_flag=yes",
               "srcima_flag=yes",
               "srcimages=%s" % ((" ").join(srcmaps)),
               "shapelet_flag=no",
               "photon_flag=no"
               ]
        if (do_ermldet == True):
            if (os.path.isfile(mllist) == True):
                os.remove(mllist)
            for ii in range(len(srcmaps)):
                if (os.path.isfile(srcmaps[ii]) == True):
                    os.remove(srcmaps[ii])
                    print(srcmaps[ii])
            print(cmd)
            subprocess.check_call(cmd)

        # -------------------------------------------------------------------------

        catprep = "%s020_SourceCatalog_%s" % (os.path.join(subdir, outfile), outfile_suffix)
        cmd = ["catprep",
               "infile=%s" % mllist,
               "outfile=%s" % catprep,
               "skymap=../../SKYMAPS.fits"
               ]
        if (do_catprep == True):
            if (os.path.isfile(catprep) == True):
                os.remove(catprep)
            print(cmd)
            subprocess.check_call(cmd)

        # ----------------------------------------------------------------

        cmd = ['srctool',
               'todo=ALL',
               'eventfiles=%s' % (infile),
               'prefix=%s' % (os.path.join(subdir, srctool_dir, outfile)),
               'suffix=%s' % (suffix_srctool),
               'srccoord=%s' % (catprep),
               'srcreg=AUTO',
               'backreg=AUTO',
               "clobber=yes"
               ]


        if (do_srctool == True):
            if (os.path.isdir(os.path.join(subdir, srctool_dir)) == False):
                os.mkdir(os.path.join(subdir, srctool_dir))
            print(cmd)
            subprocess.check_call(cmd)


# -------
# Perform eSASS run
EsassPipeline().run_pipeline()