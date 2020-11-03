# mne-frequency-tagging
analyze electrophysiological data from frequency tagging experiments using mne-python


so far you start with already extracted PSD spectra + corresponding frequency bins.
all functions work with 3d (trials x channels x frequencies), 
2d (trials or channels x frequencies) and 1d data (single trial, single channel psd).

you can:
- compute the SNR spectrum (tweakable local peak ratio algorithm)
- extract snr for a given (stimulation) frequency
- plot PSD spectrum (all individual trials/channels or grand average + std range)
- plot snr spectrum (grand average snr as stem plot)
-- optional underlayed with trial or channel averages, 
-- optional annotation with stimulation frequency(ies)
- plot snr at a given (stimulation) frequency as a heatmap/topoplot 
-- on the exact used montage (incl. digitization), or a standard montage

alternatively, you can create an instance of FtSpectra class, that can do all the same things implemented as class methods.

installation using pip:
1. download file archive
2. unpack
3. open terminal, cd into unpacked folder, activate virtual environment, and call `pip install .` (or `pip install -e .` if you want to adapt things) 