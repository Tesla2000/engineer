import os
from enum import Enum
from time import sleep

import pygame

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

bird_images = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird" + str(x) + ".png"))) for x in
               range(1, 4)]
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)

class Bird:
    def __init__(self, y):
        self.y = y
        self.images = bird_images
        self.image = self.images[0]
        self.rotation_velocity = 20
        self.animation_time = 5
        self.speed = 10
        self.tilt = 0
        self.changes = 0
        self.max_tilt = 30

    def move(self, window, time):
        self.image = self.images.pop(0)
        self.images.append(self.image)
        self.y = (self.y + time * self.speed) % WINDOW_HEIGHT
        self.tilt += (-1) ** self.changes * self.rotation_velocity * time
        if abs(self.tilt) > self.max_tilt:
            self.changes += 1
        rotated_image = pygame.transform.rotate(self.image, self.tilt)
        new_rect = rotated_image.get_rect(center=self.image.get_rect(topleft=(WINDOW_WIDTH // 2 - 20, self.y)).center)
        window.blit(rotated_image, new_rect.topleft)


class Prompt:
    def __init__(self, image):
        self.image = pygame.transform.scale2x(pygame.image.load(image))
        self.counter = 0

    def move(self, window):
        window.blit(self.image, self.image.get_rect(center=self.image.get_rect(topleft=(0, 0)).center))


def display_concentration(window, bird, time, prompt=None):
    window.fill(black)
    if prompt is not None:
        prompt.move(window)
    bird.move(window, time)
    sleep(time)
    pygame.display.update()
