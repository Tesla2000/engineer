import time
from collections import deque
from enum import Enum

import numpy as np
from pylsl import StreamInlet, resolve_stream
from sympy import fft, ifft


class Stream(Enum):
    FREQUENCY = 1
    AMPLITUDE = 0


def take_data_amplitude(stream):
    start = time.time()
    sample = np.empty((n_channels,))
    for channel in range(n_channels):
        channel_sample, _ = stream.pull_sample()
        sample[channel] = channel_sample
    return time.time() - start, sample


def take_data_frequency(stream, *filters, max_frequency=60):
    start = time.time()
    sample = np.empty((n_channels, max_frequency))
    for channel in range(n_channels):
        channel_sample, _ = stream.pull_sample()
        sample[channel + 1] = filter_sample(channel_sample[:max_frequency], filters)
    return time.time() - start, sample


def filter_sample(sample, *filters):
    filtered = sample
    if filters:
        filtered = ifft(filtered)
    for f in filters:
        filtered = f(filtered)
    return fft(filtered)


if __name__ == '__main__':
    n_channels = 8
    fps_counter = deque(maxlen=150)
    streams = resolve_stream('type', 'EEG')
    amplitude_stream = StreamInlet(streams[Stream.AMPLITUDE])
    frequency_stream = StreamInlet(streams[Stream.FREQUENCY])