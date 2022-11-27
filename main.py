import os
import random
import threading
import time
from datetime import datetime

import cv2
import numpy as np
import pygame
from pylsl import resolve_stream, StreamInlet

from connection import Stream, take_data_amplitude, take_data_frequency
from filters import bandpass, notch
from gui import Bird, WINDOW_HEIGHT, WINDOW_WIDTH, display_concentration, Prompt

sampling_rate = 250
electricity_frequency = 50  # Europe 50 USA 60

activity_numbers = {'break': 0, 'imaginary_left': 1, 'imaginary_right': 2, 'silent_yes': 3, 'silent_no': 4,
                    'imaginary_yes': 3, 'imaginary_no': 4}
numbers_activity = {0: 'break', 1: 'imaginary_left', 2: 'imaginary_right', 3: 'silent_yes', 4: 'silent_no',
                    5: 'imaginary_yes', 6: 'imaginary_no'}


def examine_concentration(session, length_of_preparations_session=30, length_concentration_session=120,
                          length_relax_session=120, max_frequency=60, n_channels=8, alpha_frequency=None,
                          beta_frequency=None):
    if alpha_frequency is None:
        alpha_frequency = (7, 13)
    if beta_frequency is None:
        beta_frequency = (12, 30)
    start = time.time()
    bird = Bird(WINDOW_HEIGHT)
    bird.rotation_velocity = 100
    bird.speed = 100
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    collector = frequency_collector(f'data/{session}/test_filtered.csv', f'data/{session}/test_unfiltered.csv',
                                    notch(electricity_frequency, sampling_rate), bandpass(5, 35, sampling_rate))
    while time.time() - length_of_preparations_session < start:
        display_concentration(window, bird, 0.01)
        next(collector)
    full_power = np.sum(
        np.loadtxt(f'data/{session}/test_filtered.csv', usecols=range(1, n_channels + 1))[:max_frequency])
    alpha_power = np.loadtxt(f'data/{session}/test_filtered.csv',
                             usecols=range(1, n_channels + 1))[:, alpha_frequency[0]:alpha_frequency[1] + 1]
    beta_power = np.loadtxt(f'data/{session}/test_filtered.csv',
                            usecols=range(1, n_channels + 1))[:, beta_frequency[0]:beta_frequency[1] + 1]
    collector = frequency_collector(f'data/{session}/concentration_filtered.csv',
                                    f'data/{session}/concentration_unfiltered.csv',
                                    notch(electricity_frequency, sampling_rate), bandpass(5, 35, sampling_rate))
    relative_alpha, relative_beta = alpha_power / full_power, beta_power / full_power
    while time.time() - (length_of_preparations_session + length_concentration_session) < start:
        filtered, unfiltered = next(collector)
        bird.speed = 100 / (
                (np.sum(filtered[beta_frequency[0]:beta_frequency[1] + 1]) / np.sum(filtered)) / relative_beta)
        display_concentration(window, bird, 0.01, Prompt('imgs/concentrate.png'))
    collector = frequency_collector(f'data/{session}/relax_filtered.csv', f'data/{session}/relax_unfiltered.csv',
                                    notch(electricity_frequency, sampling_rate), bandpass(5, 35, sampling_rate))
    while time.time() - (length_of_preparations_session + length_concentration_session + length_relax_session) < start:
        filtered, unfiltered = next(collector)
        bird.speed = 100 / (
                (np.sum(filtered[alpha_frequency[0]:alpha_frequency[1] + 1]) / np.sum(filtered)) / relative_alpha)
        display_concentration(window, bird, 0.01, Prompt('imgs/relax.png'))
    pygame.quit()


def show_image(image_path, display_duration=4000):
    cv2.imshow("window", cv2.imread(image_path))
    cv2.waitKey(display_duration)


def pause(duration=2000):
    cv2.imshow("window", cv2.imread('imgs/empty.png'))
    cv2.waitKey(duration)


def examine_paradigm(session, amplitude_stream, choices, wait_before_register=2, display_time=2, break_time=2, trials=60):
    n_channels = 8
    for _ in range(trials):
        showing = threading.Thread(target=pause, args=(1000 * break_time,))
        showing.start()
        start = time.time()
        while break_time + start < time.time():
            with open(session, 'a') as file:
                timestamp, data = take_data_amplitude(amplitude_stream, n_channels)
                file.write(','.join((timestamp, 0, *data)) + '\n')
        showing.join()
        showing = threading.Thread(target=show_image, args=('imgs/' + numbers_activity[choice := random.choice(choices)],
                                                            1000 * break_time))
        start = time.time()
        while wait_before_register + start < time.time():
            with open(session, 'a') as file:
                timestamp, data = take_data_amplitude(amplitude_stream, n_channels)
                file.write(','.join((timestamp, 0, *data)) + '\n')
        showing.join()
        showing.start()
        start = time.time()
        while display_time + start < time.time():
            with open(session, 'a') as file:
                timestamp, data = take_data_amplitude(amplitude_stream, n_channels)
                file.write(','.join((timestamp, choice, *data)) + '\n')
        showing.join()


def frequency_collector(write_to_filtered, write_to_unfiltered, *filters, duration=120):
    start = time.time()
    n_channels = 8
    streams = resolve_stream('type', 'EEG')
    frequency_stream = StreamInlet(streams[Stream.FREQUENCY])
    while time.time() - duration < start:
        timestamp, unfiltered, filtered = take_data_frequency(frequency_stream, *filters, n_channels)
        with open(write_to_filtered, 'a') as file:
            file.write(','.join((str(timestamp), *map(str, filtered))))
        with open(write_to_unfiltered, 'a') as file:
            file.write(','.join((str(timestamp), *map(str, unfiltered))))
        yield filtered, unfiltered


def start_session():
    now = str(datetime.now()).split('.')[0]
    session_name = f'data/session_{now}.csv'
    with open(session_name, 'w') as _:
        pass
    return session_name


def main():
    session = start_session()
    stream = resolve_stream('type', 'EEG')
    amplitude_stream = StreamInlet(stream[Stream.AMPLITUDE])
    examine_paradigm(session, amplitude_stream, (1, 2,))
    examine_paradigm(session, amplitude_stream, (3, 4))
    examine_paradigm(session, amplitude_stream, (5, 6))
    # examine_concentration(session)


if __name__ == '__main__':
    main()
