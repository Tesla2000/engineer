import pygame
from numpy.fft import fft, fftfreq
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

def examine_MI():
    pass


if __name__ == '__main__':
    main()
