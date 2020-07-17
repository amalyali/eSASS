from astropy.io import fits
from astropy.table import Table
import matplotlib.pyplot as plt
import numpy as np

rebin_time_threshold = 100.
fracexp_thresh = 0.001


def rebin_lc(time, counts, fracexp, bkg_counts, backratio, timedel_old):
    """
    Rebin lightcurves using non-weighted averaging.
    Riccardo Arcodia, 2020
    """
    i = 0
    while i + 1 < len(time):
        if counts[i] <= 0:
            if time[i + 1] - time[i] >= rebin_time_threshold:
                yield (time[i], counts[i], 1 + np.sqrt(counts[i] + 0.75),
                       fracexp[i], timedel_old[i], bkg_counts[i],
                       1 + np.sqrt(bkg_counts[i] + 0.75), backratio[i])
                i = i + 1
        for j in range(i, len(time)):
            if time[j] - time[i] >= rebin_time_threshold or (
                    time[j] - time[i] < rebin_time_threshold and j + 1 == len(time)):
                if time[j] - time[i] < rebin_time_threshold and j + 1 == len(time):
                    time_mask = np.logical_and(time >= time[i], time <= time[j])
                else:
                    time_mask = np.logical_and(time >= time[i], time < time[j])
                average_time = np.average(time[time_mask])
                average_fracexp = np.average(fracexp[time_mask])
                average_backratio = np.average(backratio[time_mask])
                timedel = np.sum(timedel_old[time_mask])
                # yielding new t, new counts, counts error, fracexp and timedel,
                # ..summed bkg cts, bkg_cts_err_average backratio
                yield (average_time, counts[time_mask].sum(), 1 + np.sqrt(counts[time_mask].sum() + 0.75),
                       average_fracexp, timedel, bkg_counts[time_mask].sum(),
                       1 + np.sqrt(bkg_counts[time_mask].sum() + 0.75), average_backratio)
                if j + 1 != len(time):
                    break
                if time[j] - time[i] >= rebin_time_threshold and j + 1 == len(time):
                    # print(i, j+1, time[j]-time[i])
                    time_mask = np.logical_and(time >= time[j], time <= time[j])
                    average_time = np.average(time[time_mask])
                    average_fracexp = np.average(fracexp[time_mask])
                    average_backratio = np.average(backratio[time_mask])
                    timedel = timedel_old[j]
                    yield (average_time, counts[time_mask].sum(), 1 + np.sqrt(counts[time_mask].sum() + 0.75),
                           average_fracexp, timedel, bkg_counts[time_mask].sum(),
                           1 + np.sqrt(bkg_counts[time_mask].sum() + 0.75), average_backratio)
                    break
        i = j


def weighted_rebin_lc(time, timedel, counts, fractime, fracarea, bkg_counts, backratio):
    """
    Rebin lightcurves using non-weighted averaging.

    ***potentially dodgy....***

    Riccardo Arcodia, Adam Malyali, 2020
    """
    i = 0
    len_lc = len(time)
    while i + 1 < len_lc:
        for j in range(i, len_lc):
            if time[j] - time[i] >= 100 or j + 1 >= len_lc:
                if j + 1 >= len(time):
                    time_mask = np.logical_and(time >= time[i], time <= time[j])
                else:
                    time_mask = np.logical_and(time >= time[i], time < time[j])
                average_time = np.average(time[time_mask])

                # weighted rebinning version different from here
                try:
                    average_fracexp = np.sum(
                        fracarea[time_mask] * np.power(fractime[time_mask], 2.) / np.sum(fractime[time_mask]))
                    average_backratio = np.average(backratio[time_mask],
                                                   weights=fractime[time_mask] / np.sum(fractime[time_mask]))
                except IndexError as e:
                    average_fracexp = np.average(fractime[time_mask])
                    average_backratio = np.average(backratio[time_mask])

                if j + 1 >= len(time):
                    timedel = time[j] - time[i]  # TODO: fix this bug
                else:
                    timedel = time[j - 1] - time[i]  # TODO: fix this bug

                # yielding new t, new counts, counts error, fracexp and timedel, summed bkg cts, bkg_cts_err_average backratio
                summed_src_cts = counts[time_mask].sum()
                summed_bkg_cts = bkg_counts[time_mask].sum()
                yield (average_time, summed_src_cts, 1 + np.sqrt(summed_src_cts + 0.75),
                       average_fracexp, timedel, summed_bkg_cts,
                       1 + np.sqrt(summed_bkg_cts + 0.75), average_backratio)
                break
        i = j


def plot_lightcurve_single(_lc, id_band, _rebin=False, _weighted_rebin=False):
    """
    Plot eSASS lightcurve
    :return:
    """
    fig_width_pt = 246.0  # Get this from LaTeX using \showthe\columnwidth
    inches_per_pt = 1.0 / 72.27  # Convert pt to inch
    golden_mean = (np.sqrt(5) - 1.0) / 2.0  # Aesthetic ratio
    fig_width = fig_width_pt * inches_per_pt  # width in inches
    fig_height = fig_width * golden_mean  # height in inches
    fig_size = [fig_width, fig_height]

    ### Plot options.
    params = {'backend': 'ps',
              'axes.labelsize': 10,
              'axes.linewidth': 1,
              'xtick.direction': 'in',
              'ytick.direction': 'in',
              'xtick.top': True,
              'ytick.right': True,
              'xtick.major.width': 1,
              'xtick.major.size': 4,
              'ytick.major.width': 1,
              'ytick.major.size': 4,
              'xtick.labelsize': 10,
              'ytick.labelsize': 10,
              # 'text.usetex': True,
              'font.family': 'sans-serif',
              'font.sans-serif': 'Arial',
              # 'mathtext.fontset': 'stix',
              # 'text.latex.unicode': True,
              'font.size': 10,
              'legend.fontsize': 10,
              'figure.figsize': fig_size}

    plt.rcParams.update(params)
    plt.clf()

    if _rebin is False:
        _lc['TIME'] = _lc['TIME'] - min(_lc['TIME'])
        _lc['TIME'] = _lc['TIME'] / (24. * 3600)

        for id_b in id_band:
            _lc = _lc[np.where(_lc['FRACEXP'][:, id_b] > 0.01)]
            plt.errorbar(_lc['TIME'], _lc['RATE'][:, id_b], _lc['RATE_ERR'][:, id_b],
                         marker='o', markersize=1,
                         # label='%s' % label_dict[id_b], #color=color_dict[id_b],
                         linestyle='-')
        plt.ylabel('Rate [cts/s]')
        plt.xlabel('$t - t_0$ [MJD]')
        plt.ylim(-0.3, 1.5 * max(_lc['RATE'][1]))

        plt.legend()
        # plt.title('SRGt J123822-253206')
        plt.savefig('./example_lightcurve.pdf', bbox_inches='tight')

    if _rebin is True:
        bands = [i for i in range(len(_lc['COUNTS'][0]))]
        label_dict = {0: '0.2-0.6keV', 1: '0.6-2.3keV', 2: '2.3-5keV'}
        for band in bands:
            x_unbinned = _lc['TIME'] - _lc['TIME'][0]
            xdel_unbinned = _lc['TIMEDEL']
            bc_unbinned = _lc['BACK_COUNTS'][:, band]
            c_unbinned = _lc['COUNTS'][:, band]
            bgarea_unbinned = 1. / _lc['BACKRATIO']
            rate_conversion_unbinned = _lc['FRACEXP'][:, band] * _lc['TIMEDEL']

            if _weighted_rebin is False:
                t, c, c_err, fracexp, timedel, bc, bc_err, backratio = np.transpose(
                    list(rebin_lc(x_unbinned, c_unbinned, _lc['FRACEXP'][:, band], bc_unbinned, 1. / bgarea_unbinned, xdel_unbinned)))

                # Mask out low fractional exposure bins
                mask_low_fracexp = np.where(fracexp > fracexp_thresh, True, False)
                t = t[mask_low_fracexp]
                c = c[mask_low_fracexp]
                c_err = c_err[mask_low_fracexp]
                fracexp = fracexp[mask_low_fracexp]
                timedel = timedel[mask_low_fracexp]
                bc = bc[mask_low_fracexp]
                bc_err = bc_err[mask_low_fracexp]
                backratio = backratio[mask_low_fracexp]

                # Compute rates
                rate_tot = (c - bc * backratio) / (fracexp * timedel)
                rate_tot_err = (c_err ** 2 + bc_err ** 2 * backratio) ** 0.5 / (fracexp * timedel)
                bkg_rate = bc * backratio / (fracexp * timedel)

                print(rate_tot)
                plt.errorbar(t, rate_tot, xerr=timedel, yerr=rate_tot_err, linestyle='', marker='o', markersize=2,
                             label=label_dict[band])

            if _weighted_rebin is True:
                # Weighted
                t, c, c_err, w_fracexp, w_timedel, bc, bc_err, backratio = np.transpose(list(
                    weighted_rebin_lc(x_unbinned, xdel_unbinned, c_unbinned, _lc['FRACTIME'], _lc['FRACAREA'][:, band],
                                      bc_unbinned, 1. / bgarea_unbinned)))
                w_rate_tot = (c - bc * backratio) / (w_fracexp * w_timedel)
                print(w_rate_tot)
                w_rate_tot_err = (c_err ** 2 + bc_err ** 2 * backratio) ** 0.5 / (w_fracexp * w_timedel)
                w_bkg_rate = bc * backratio / (w_fracexp * w_timedel)

                plt.errorbar(t, w_rate_tot, w_rate_tot_err,
                             marker='o', markersize=2, linestyle='', label=label_dict[band])
        plt.ylim(0.0, 3)
        plt.ylabel('Rate [cts/s]')
        plt.xlabel('$t - t_0$ [s]')
        plt.legend()
        plt.savefig('./example_lightcurve_rebinned.pdf', bbox_inches='tight')


if __name__ == '__main__':
    lc = Table.read('../../../Downloads/em02_148153_020_LightCurve_00004_003_c946.fits', format='fits')
    # lc =
    plot_lightcurve_single(lc, [0, 1, 2], _rebin=True, _weighted_rebin=False)
