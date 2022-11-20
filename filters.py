from scipy.signal import iirfilter, filtfilt, iirnotch


def bandpass(low_pass, high_pass, sampling_rate, order=6):
    a, b = iirfilter(order, [low_pass / sampling_rate * 2, high_pass / sampling_rate * 2])
    return lambda signal: filtfilt(a, b, signal)


def notch(notch_frequency, sampling_rate, quality_factor=30):
    a, b = iirnotch(notch_frequency, quality_factor, sampling_rate)
    return lambda signal: filtfilt(a, b, signal)
