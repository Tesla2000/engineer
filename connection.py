import time
from enum import Enum

import numpy as np
from numpy.fft import fft, ifft


class Stream(Enum):
    FREQUENCY = 1
    AMPLITUDE = 0


def take_data_amplitude(stream, n_channels):
    start = time.time()
    sample = np.empty((n_channels,))
    for channel in range(n_channels):
        channel_sample, _ = stream.pull_sample()
        sample[channel] = channel_sample
    return time.time() - start, sample


def take_data_frequency(stream, *filters, n_channels=8, max_frequency=60):
    start = time.time()
    unfiltered, filtered = np.empty((n_channels, max_frequency)), np.empty((n_channels, max_frequency))
    for channel in range(n_channels):
        sample, _ = stream.pull_sample()
        unfiltered[channel] = sample[:max_frequency]
        filtered[channel] = filter_sample(unfiltered[channel], filters)
    return time.time() - start, unfiltered, filtered


def filter_sample(sample, *filters):
    filtered = sample
    if filters:
        filtered = ifft(filtered)
    for f in filters:
        filtered = f(filtered)
    return fft(filtered)
