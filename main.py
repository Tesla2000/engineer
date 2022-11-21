import os
import random
import threading
import time
from datetime import datetime

import numpy as np
import pygame
from numpy.fft import fft, fftfreq
from pylsl import resolve_stream, StreamInlet

from filters import bandpass, notch
from connection import filter_sample, Stream, take_data_amplitude, take_data_frequency
import cv2
from gui import Bird, WINDOW_HEIGHT, WINDOW_WIDTH, display_concentration

sampling_rate = 250
electricity_frequency = 50  # Europe 50 USA 60


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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        display_concentration(window, bird, 0.01)
        next(collector)
    full_power = np.sum(np.loadtxt(f'data/{session}/test_filtered.csv', usecols=range(1, n_channels + 1)))
    alpha_power = np.loadtxt(f'data/{session}/test_filtered.csv',
                             usecols=range(1, n_channels + 1))[:, alpha_frequency[0]:alpha_frequency[1] + 1]
    beta_power = np.loadtxt(f'data/{session}/test_filtered.csv',
                            usecols=range(1, n_channels + 1))[:, beta_frequency[0]:beta_frequency[1] + 1]
    relative_alpha, relative_beta = alpha_power / full_power, beta_power / full_power
    while time.time() - (length_of_preparations_session + length_concentration_session) < start:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        filtered, unfiltered = next(collector)
        bird.speed = 100 / (
                    (np.sum(filtered[beta_frequency[0]:beta_frequency[1] + 1]) / np.sum(filtered)) / relative_beta)
        display_concentration(window, bird, 0.01)
    while time.time() - (length_of_preparations_session + length_concentration_session + length_relax_session) < start:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        filtered, unfiltered = next(collector)
        bird.speed = 100 / (
                    (np.sum(filtered[alpha_frequency[0]:alpha_frequency[1] + 1]) / np.sum(filtered)) / relative_alpha)
        display_concentration(window, bird, 0.01)


def show_image(image_path, display_duration=4000, break_duration=2000):
    cv2.imshow("window", cv2.imread(image_path))
    cv2.waitKey(display_duration)
    cv2.imshow("window", cv2.imread('imgs/empty.png'))
    cv2.waitKey(break_duration)


def examine_MI(session, wait_before_display=2000, display_time=2000, break_time=2000, trials=60):
    for _ in range(trials):
        showing = threading.Thread(target=show_image, args=('imgs/' + (choice := random.choice(('l', 'r'))) +
                                                            '_letter.png', display_time + wait_before_display
                                                            , break_time))
        collecting = threading.Thread(target=collect_amplitude, args=
        (f'data/{session}/MI_' + ('right' if choice == 'r' else 'left') + '_hand.csv'
         , wait_before_display, display_time, break_time))
        showing.start()
        collecting.start()
        showing.join()
        collecting.join()


def examine_SS(session, wait_before_display=2000, display_time=2000, break_time=2000, trials=60):
    for _ in range(trials):
        showing = threading.Thread(target=show_image, args=('imgs/' + (choice := random.choice(('t', 'n'))) +
                                                            '_letter.png', display_time + wait_before_display
                                                            , break_time))
        collecting = threading.Thread(target=collect_amplitude, args=
        (f'data/{session}/SS_' + ('no' if choice == 'n' else 'yes') + '.csv'
         , wait_before_display, display_time, break_time))
        showing.start()
        collecting.start()
        showing.join()
        collecting.join()


def examine_IS(session, wait_before_display=2000, display_time=2000, break_time=2000, trials=60):
    for _ in range(trials):
        showing = threading.Thread(target=show_image, args=('imgs/' + (choice := random.choice(('t', 'n'))) +
                                                            '_letter.png', display_time + wait_before_display
                                                            , break_time))
        collecting = threading.Thread(target=collect_amplitude, args=
        (f'data/{session}/IS_' + ('no' if choice == 'n' else 'yes') + '.csv'
         , wait_before_display, display_time, break_time))
        showing.start()
        collecting.start()
        showing.join()
        collecting.join()


def collect_amplitude(write_to, wait_before_display=2000, display_time=2000, break_time=2000):
    start = time.time()
    n_channels = 8
    streams = resolve_stream('type', 'EEG')
    amplitude_stream = StreamInlet(streams[Stream.AMPLITUDE])
    while time.time() - wait_before_display / 1000 > start:
        take_data_amplitude(amplitude_stream, n_channels)
    while time.time() - (wait_before_display + display_time) / 1000 > start:
        with open(write_to, 'a') as file:
            timestamp, samples = take_data_amplitude(amplitude_stream, n_channels)
            file.write(','.join((str(timestamp), *map(str, samples))))
    while time.time() - (wait_before_display + display_time + break_time) / 1000 > start:
        take_data_amplitude(amplitude_stream, n_channels)


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
    session_name = f'data/session_{now}'
    os.makedirs(session_name)
    for paradigm in ('MI_right_hand', 'MI_left_hand', 'SS_yes', 'SS_no', 'IS_yes', 'IS_no', 'concentration_filtered',
                     'relax_filtered', 'concentration_unfiltered', 'relax_unfiltered', 'test_filtered',
                     'test_unfiltered'):
        with open(f'data/session_{now}/{paradigm}.csv', 'w') as _:
            pass
    return session_name


if __name__ == '__main__':
    examine_MI(start_session())
