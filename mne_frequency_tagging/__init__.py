"""
mne-frequency-tagging
analyze electrophysiological data from frequency tagging experiments using mne-python

Author: Dominik Welke <dominik.welke@web.de>
"""

from .frequency_tagging import snr_spectrum, snr_at_frequency
from .frequency_tagging import plot_psd_spectrum, plot_snr_topography, plot_snr_spectrum
from .FtSpectra import FtSpectra
