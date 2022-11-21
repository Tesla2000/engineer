import os
import random
import threading
import time
from datetime import datetime

import pygame
from numpy.fft import fft, fftfreq
from pylsl import resolve_stream, StreamInlet

from filters import bandpass, notch
from connection import filter_sample, Stream, take_data_amplitude
import cv2
from gui import Bird, WINDOW_HEIGHT, WINDOW_WIDTH, display_concentration


def examine_concentration():
    bird = Bird(WINDOW_HEIGHT)
    bird.rotation_velocity = 100
    bird.speed = 100
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
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


def examine_concentration(session):
    pass


def collect_amplitude(write_to, wait_before_display=2000, display_time=2000, break_time=2000):
    start = time.time()
    n_channels = 8
    streams = resolve_stream('type', 'EEG')
    amplitude_stream = StreamInlet(streams[Stream.AMPLITUDE])
    while time.time() - wait_before_display > start:
        take_data_amplitude(amplitude_stream, n_channels)
    while time.time() - wait_before_display - display_time > start:
        with open(write_to, 'a') as file:
            file.write(','.join(take_data_amplitude(amplitude_stream, n_channels)))
    while time.time() - wait_before_display - display_time - break_time > start:
        take_data_amplitude(amplitude_stream, n_channels)


def start_session():
    now = str(datetime.now()).split('.')[0]
    session_name = f'data/session_{now}'
    os.makedirs(session_name)
    for paradigm in ('MI_right_hand', 'MI_left_hand', 'SS_yes', 'SS_no', 'IS_yes', 'IS_no', 'concentration', 'relax'):
        with open(f'data/session_{now}/{paradigm}.csv', 'w') as _:
            pass
    return session_name


if __name__ == '__main__':
    examine_MI(start_session())
