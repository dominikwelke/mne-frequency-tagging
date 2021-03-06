"""
module for analysis of neurophysiological data obtained with frequency-tagging methodology (visual or auditory).

Author: Dominik Welke <dominik.welke@web.de>
"""
import mne
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn')


# utils
def _make_montage(montage, verbose=False):
    if montage is None:  # take default 10-20 montage
        montage = mne.channels.make_standard_montage(
            'standard_1020', head_size=0.095)  # head_size parameter default = 0.095
        if verbose:
            print('create standard montage following 10-20 system')
    elif type(montage) is str:  # expect this to be
        try:
            if verbose:
                print('try to create standard montage following "%s" template' % montage)
            montage = mne.channels.make_standard_montage(montage, head_size=0.095)  # head_size parameter default 0.095
        except ValueError as e:
            raise ValueError(
                'provide id of a standard montage as implemented in mne.channels.make_standard_montage or leave '
                'empty.\ndetails: %s' % e)
    else:
        pass

    return montage


# spectra operations
def snr_spectrum(psd, noise_n_neighborfreqs=1, noise_skip_neighborfreqs=1):
    """
    Parameters
    ----------
    psd - np.array
        containing psd values as spit out by mne functions. must be 2d or 3d
        with frequencies in the last dimension
    noise_n_neighborfreqs - int
        number of neighboring frequencies used to compute noise level.
        increment by one to add one frequency bin ON BOTH SIDES
    noise_skip_neighborfreqs - int
        set this >=1 if you want to exclude the immediately neighboring
        frequency bins in noise level calculation

    Returns
    -------
    snr - np.array
        array containing snr for all epochs, channels, frequency bins.
        NaN for frequencies on the edge, that do not have enoug neighbors on
        one side to calculate snr
    """

    # prep not epoched / single channel data
    is_2d = True if (len(psd.shape) == 2) else False
    if is_2d:
        psd = psd.reshape((1, psd.shape[0], psd.shape[1]))

    # SNR loop
    snr = np.empty(psd.shape)
    for i_freq in range(psd.shape[2]):

        # skip freqs on the edges (without noise neighbors)

        start_freq_i = noise_n_neighborfreqs + noise_skip_neighborfreqs
        stop_freq_i = (psd.shape[2] - noise_n_neighborfreqs
                       - noise_skip_neighborfreqs)
        if not (stop_freq_i > i_freq >= start_freq_i):
            snr[:, :, i_freq] = np.nan
            continue

        # extract signal level
        signal = psd[:, :, i_freq]

        # ... and average noise level
        i_noise = []
        for i in range(noise_n_neighborfreqs):
            i_noise.append(i_freq + noise_skip_neighborfreqs + i + 1)
            i_noise.append(i_freq - noise_skip_neighborfreqs - i - 1)
        noise = psd[:, :, i_noise].mean(axis=2)

        snr[:, :, i_freq] = signal / noise

    # reshape not epoched / single channel data to original dimensions
    if is_2d:
        snr = snr.reshape(snr.shape[1], snr.shape[2])

    return snr


def snr_at_frequency(snrs, freqs, stim_freq, verbose=False):
    """

    """
    # get position closest to wanted frequency
    tmp_distlist = abs(np.subtract(freqs, stim_freq))
    i_signal = np.where(tmp_distlist == min(tmp_distlist))[0][0]
    # could be updated to support multiple frequencies

    # check dimensionality
    dimensionality = len(snrs.shape)
    if dimensionality == 3:
        snrs_stim = snrs[:, :, i_signal]  # trial subselection can be done here
    elif dimensionality == 2:
        snrs_stim = snrs[:, i_signal]  # trial subselection can be done here
    elif dimensionality == 1:
        snrs_stim = snrs
    else:
        raise ValueError('SNR array has more that 3 dimensions. whats happening?')

    if verbose:
        print('average SNR at %iHz: %.3f '
              % (stim_freq, snrs_stim.mean()))
    return snrs_stim


# visualization function
def plot_snr_spectrum(snrs, freqs, stim_freq=None, bg_var_trials=False, bg_var_channels=False, show=True):
    """
    Parameters
    ----------
    snrs - np.array
        array containing snr for all epochs, channels, frequency bins.
        NaN for frequencies on the edge, that do not have enoug neighbors on
        one side to calculate snr
    freqs - list, np.array
        containing all frequencies you calculated snr-vlues for.
    stim_freq - list
        stimulation frequencies, or any other frequency you want to be marked by a vertical line
    bg_var_trials - bool
        set to True, it you want the grand average SNR to be underlayed with average SNR by trial (blue, alpha=0.1)
    bg_var_channels - bool
        set to True, it you want the grand average SNR to be underlayed with average SNR by channel (green, alpha=0.1)
    show - bool
        show figure or not
    Returns
    -------
    fig - matplotlib.figure.Figure
    axes - matplotlib.axes.AxesSubplot
    """
    fig, axes = plt.subplots(1, 1, sharex='all', sharey='all', dpi=300)

    # check format
    dimension = len(snrs.shape)
    if dimension > 3:  # more than 3d array
        raise ValueError('SNR array has more that 3 dimensions. whats happening?')

    # Average over trials
    if bg_var_trials and (dimension == 3):
        axes.plot(freqs, snrs.mean(axis=0).T, color='b', alpha=0.1)
    # Average over channels
    if bg_var_channels and (dimension == 3):
        axes.plot(freqs, snrs.mean(axis=1).T, color='g', alpha=0.1)

    # annotate stim frequencies
    if stim_freq:
        if type(stim_freq) is int:
            axes.axvline(x=stim_freq, ls=':')
        elif type(stim_freq) in [list, np.ndarray]:
            for sf in stim_freq:
                axes.axvline(x=sf, ls=':')
        else:
            raise Warning('unsupported format for frequency annotations. will be ignored ')

    # grand average SNR over trials and channels as stem plot
    for i in range(dimension-1):
        snrs = snrs.mean(axis=0)
    axes.stem(freqs, snrs, linefmt='r-', markerfmt='rD')
    axes.set(title="SNR spectrum", xlabel='Frequency [Hz]',
             ylabel='SNR', ylim=[0, np.ceil(np.nanmax(snrs)+1)])

    # show plot or not?
    if show:
        fig.show()

    return fig, axes


def plot_snr_topography(snrs_at_frequency, ch_names, montage=None, plot_montage=False, show=False, verbose=False):
    """
    Parameters
    ----------
    snrs_at_frequency - numpy.Array, list
        list or array with snr at a given frequency.
        if list or 1d array, length must correspond to len(ch_names).
        if 2d or 3d array, 1st dimension reflects number of trials, 2nd dimension number of channels.
        if 3d dimension is larger than 1, results might not make sense - average is taken.
    ch_names - list
        list of channel names, e.g. obtained from raw.Info['ch_names']
    montage - mne.channels.montage.DigMontage, str, None
        specify the montage for visualization.
        can be the exact montage as used, but also a standard montage.
        if str, specify name of a standard montage provided with mne.channels.make_standard_montage() function.
        if None, standard 10-20 montage is used
    plot_montage - bool
        also show a plot of the general montage?
    show - bool
        show plot or not
    verbose - bool
        print some additional info
    Returns
    -------
    fig - matplotlib.figure.Figure
    axes - matplotlib.axes.AxesSubplot
    """

    # get channel locations from montage
    montage = _make_montage(montage, verbose=verbose)
    # convert digitization to xyz coordinates
    montage.positions = montage._get_ch_pos()  # luckily i dug this out in the mne code!

    # plot montage, if wanted
    if plot_montage:
        montage.plot(show=True)

    # get grand average SNR per channel (all subs, all trials) and electrode labels
    dimensionality = len(snrs_at_frequency.shape) if type(snrs_at_frequency) != list else 1
    if dimensionality == 1:
        snr_grave = snrs_at_frequency
    elif dimensionality == 2:
        snr_grave = snrs_at_frequency.mean(axis=0)
    elif dimensionality == 3:
        snr_grave = snrs_at_frequency.mean(axis=2).mean(axis=0)
    else:
        raise ValueError('SNR array has more that 3 dimensions. whats happening?')

    # select only present channels from the standard montage
    topo_pos_grave = []
    [topo_pos_grave.append(montage.positions[ch][:2]) for ch in ch_names]
    topo_pos_grave = np.array(topo_pos_grave)

    # plot SNR topography
    fig, axes = plt.subplots()
    mne.viz.plot_topomap(snr_grave, topo_pos_grave, vmin=0, axes=axes, show=show)

    if verbose:
        print('plot topography of given snr array')
        print("grand average SNR at given frequency: %f" % snr_grave.mean())

    return fig, axes


def plot_psd_spectrum(psds, freqs, fmin=None, fmax=None, plot_type='average', show=True):
    # plot average psd plus/minus std.
    # code snippets from:
    # https://martinos.org/mne/stable/auto_examples/time_frequency/plot_compute_raw_data_spectrum.html

    # get dimensionality of data
    dimensionality = len(psds.shape)
    if dimensionality > 3:
        raise ValueError('PSD array has more that 3 dimensions. whats happening?')

    # get indices of plotted values
    if fmin is None:
        fmin = np.nanmin(freqs)
    if fmax is None:
        fmax = np.nanmax(freqs)

    rng = range(np.where(np.floor(freqs) == fmin + 1)[0][0],
                np.where(np.ceil(freqs) == fmax - 1)[0][0])

    # prepare figure
    fig, axes = plt.subplots(1, 1, sharex='all', sharey='all', dpi=300)
    # prepare psd (transform to db scale)
    psds_plot = 10 * np.log10(psds)
    if plot_type == 'average' and dimensionality > 1:
        # get mean and std
        if dimensionality == 3:
            psds_mean = psds_plot.mean((0, 1))[rng]
            psds_std = psds_plot.std((0, 1))[rng]
        else:
            psds_mean = psds_plot.mean(axis=0)[rng]
            psds_std = psds_plot.std(axis=0)[rng]
        # plot
        axes.plot(freqs[rng], psds_mean, color='b')
        axes.fill_between(freqs[rng], psds_mean - psds_std, psds_mean + psds_std,
                          color='b', alpha=.5)
        axes.set(title="PSD spectrum (average +- std)", xlabel='Frequency [Hz]',
                 ylabel='Power Spectral Density [dB]')
        plt.xlim([fmin, fmax])
    else:
        # plot
        if dimensionality == 1:
            axes.plot(freqs[rng], psds_plot[rng], color='b')
        elif dimensionality == 2:
            axes.plot(
                freqs[rng],
                psds_plot[:, rng].T,
                color='b', alpha=.5)
        else:
            axes.plot(
                freqs[rng],
                psds_plot.reshape(psds_plot.shape[0]*psds_plot.shape[1], psds_plot.shape[2])[:, rng].T,
                color='b', alpha=.5)
        axes.set(title="PSD spectrum (individual channels/trials)", xlabel='Frequency [Hz]',
                 ylabel='Power Spectral Density [dB]')
        plt.xlim([fmin, fmax])

    # show plot or not?
    if show:
        fig.show()

    return fig, axes
