import numpy as np
import pygame
from matplotlib import pyplot as plt
from scipy.fft import fft
from scipy.fftpack import fftfreq
from filters import bandpass, notch
from connection import filter_sample
from gui import Bird, WINDOW_HEIGHT, WINDOW_WIDTH, draw_window


def main():
    bird = Bird(WINDOW_HEIGHT)
    bird.rotation_velocity = 100
    bird.speed = 100
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        draw_window(window, bird, 0.01)


if __name__ == '__main__':
    # main()
    sampling_rate = 120
    sample = 100 * np.sin(50 * np.linspace(0, 1, sampling_rate)) + 10 * (np.sin(20 * np.linspace(0, 1, sampling_rate)) + np.sin(
        30 * np.linspace(0, 1, sampling_rate)) + np.sin(10 * np.linspace(0, 1, sampling_rate)) + np.sin(40 * np.linspace(0, 1, sampling_rate)))
    plt.plot(fftfreq(120//2), fft(sample)[:sampling_rate//2])
    plt.show()
    # n = notch(50, sampling_rate)
    # plt.plot(filter_sample(fft(sample), n))
    # plt.show()
