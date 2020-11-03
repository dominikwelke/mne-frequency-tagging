"""
class for analysis of neurophysiological data obtained with frequency-tagging methodology (visual or auditory).

Author: Dominik Welke <dominik.welke@web.de>
"""
from .frequency_tagging import _make_montage
from .frequency_tagging import snr_spectrum, snr_at_frequency
from .frequency_tagging import plot_snr_spectrum, plot_snr_topography, plot_psd_spectrum


class FtSpectra:
    def __init__(self, frequency_bins, psd, ch_names, stim_freq=None, montage=None, verbose=False):
        self.frequency_bins = frequency_bins
        self.psd = psd
        self.snr = None
        self.info = {
            'dim': self.psd.shape,
            'stim_freq': stim_freq,
            'ch_names': ch_names,
            'montage': _make_montage(montage, verbose=verbose)
        }
        self.verbose = verbose

        # integrity check
        if self.info['dim'][-1] != len(self.frequency_bins):
            raise Warning('check your data! ' 
                          'dimensions of PSD array do not fit with number of frequency bins you provided')
        if self.info['dim'][-2] != len(self.info['ch_names']):
            raise Warning('check your data! '
                          'dimensions of PSD array do not fit with number of channels you provided')

    # spectrum operations
    def add_snr_spectrum(self, noise_n_neighborfreqs=1, noise_skip_neighborfreqs=1):
        try:
            self.snr = snr_spectrum(
                self.psd,
                noise_n_neighborfreqs=noise_n_neighborfreqs,
                noise_skip_neighborfreqs=noise_skip_neighborfreqs)
        except ValueError:
            raise Warning('could not compute SNR spectrum. PSD and/or frequency bins missing')

    # plots
    def plot_psd_spectrum(self, fmin=None, fmax=None, show=True):
        return plot_psd_spectrum(self.psd, self.frequency_bins, fmin=fmin, fmax=fmax, show=show)

    def plot_snr_spectrum(self, bg_var_trials=False, bg_var_channels=False, show=True):
        if self.snr is not None:
            return plot_snr_spectrum(
                self.snr, self.frequency_bins, stim_freq=self.info['stim_freq'],
                bg_var_trials=bg_var_trials, bg_var_channels=bg_var_channels, show=show)
        else:
            raise Warning('could not plot SNR spectrum. run add_snr_spectrum function first')

    def plot_snr_topography(self, plot_montage=False, show=False, verbose=False):
        snrs_at_frequency = snr_at_frequency(self.snr, self.frequency_bins, self.info['stim_freq'], verbose=verbose)
        plot_snr_topography(
            snrs_at_frequency, self.info['ch_names'], montage=self.info['montage'],
            plot_montage=plot_montage, show=show, verbose=verbose)
