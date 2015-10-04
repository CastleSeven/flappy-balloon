#! /usr/bin/env python3

import math
import os
from random import randint
from collections import deque
import pygame
from pygame.locals import *

FPS = 60;
ANIMATION_SPEED = 0.30
WIN_WIDTH = 1920;
WIN_HEIGHT = 1080;
ADD_INTERVAL = 5000

class Balloon(pygame.sprite.Sprite):
    """
    WIDTH: Pixel width of the balloon
    HEIGHT: Pixel height of the balloon
    SINK_SPEED: Speed in pixels/ms that the balloon descends while not climbing
    CLIMB_SPEED: Speed in p/ms that the balloon ascends while climbing (on average)
    CLIMB_DURATION: The # of ms for the balloon to make a complete ascent
    """

    WIDTH = 212
    HEIGHT = 300
    SINK_SPEED = 0.09
    CLIMB_SPEED = 0.15
    CLIMB_DURATION = 600.3

    def __init__(self, x, y, msec_to_climb, images):
        super(Balloon, self).__init__()
        self.x, self.y = x, y
        self.msec_to_climb = msec_to_climb
        self._img_flameoff, self._img_flameon = images
        self._mask_flameoff = pygame.mask.from_surface(self._img_flameoff)
        self._mask_flameon = pygame.mask.from_surface(self._img_flameon)

    def update(self, delta_frames=1):
        if self.msec_to_climb > 0:
            frac_climb_done = 1 - self.msec_to_climb/Balloon.CLIMB_DURATION
            self.y -= (Balloon.CLIMB_SPEED * frames_to_msec(delta_frames) * (1 - math.cos(frac_climb_done * math.pi)))
            self.msec_to_climb -= frames_to_msec(delta_frames)
        else:
            self.y += Balloon.SINK_SPEED * frames_to_msec(delta_frames)

    @property
    def image(self):
        if self.msec_to_climb > 0:
            return self._img_flameon
        else:
            return self._img_flameoff

    @property
    def rect(self):
        return Rect(self.x, self.y, Balloon.WIDTH, Balloon.HEIGHT)

class Bird(pygame.sprite.Sprite):
    WIDTH = 296
    HEIGHT = 260
    FLAP_SPEED = 100 # ms delay between flaps

    def __init__(self, images):
        self.old_flap_time = pygame.time.get_ticks()
        self.x = float(WIN_WIDTH - 1)
        self.score_counted = False
        self.y = randint(Bird.HEIGHT, WIN_HEIGHT - Bird.HEIGHT)
        self._img_up, self._img_down = images
        self._current_image = self._img_up
        self.mask = pygame.mask.from_surface(self.image)

        #self.image = pygame.Surface((Bird.WIDTH, Bird.HEIGHT), SRCALPHA)
        #self.image.convert()
        #self.image.fill((0,0,0,0))
        #balloon_pos = (0, self.y)
        #self.image.blit(balloon_obstacle_img, balloon_pos)

    @property
    def image(self):
        current_time = pygame.time.get_ticks()
        if (current_time - self.old_flap_time) > self.FLAP_SPEED:
            self.old_flap_time = current_time
            if self._current_image == self._img_up:
                self._current_image = self._img_down
                return self._img_down
            else:
                self._current_image = self._img_up
                return self._img_up
        return self._current_image

    @property
    def visible(self):
        return -Bird.WIDTH < self.x < WIN_WIDTH

    @property
    def rect(self):
        return Rect(self.x, self.y + 40, Bird.WIDTH, Bird.HEIGHT + 75)

    def update(self, delta_frames=1):
        self.x -= ANIMATION_SPEED * frames_to_msec(delta_frames)

    def collides_with(self, balloon):
        return pygame.sprite.collide_mask(self,balloon)


class Plane(pygame.sprite.Sprite):
    WIDTH = 235
    HEIGHT = 144

    def __init__(self, image):
        self.x = float(WIN_WIDTH - 1)
        self.score_counted = False
        self.y = randint(Plane.HEIGHT, WIN_HEIGHT - Plane.HEIGHT)
        self._img = image
        self.mask = pygame.mask.from_surface(self.image)

    @property
    def image(self):
        return self._img

    @property
    def visible(self):
        return -Plane.WIDTH < self.x < WIN_WIDTH

    @property
    def rect(self):
        return Rect(self.x, self.y, Plane.WIDTH, Plane.HEIGHT)

    def update(self, delta_frames=1):
        self.x -= ANIMATION_SPEED * frames_to_msec(delta_frames)

    def collides_with(self, balloon):
        return pygame.sprite.collide_mask(self,balloon)

def load_images():

    def load_image(img_file_name):
        file_name = os.path.join('.', 'images', img_file_name)
        img = pygame.image.load(file_name)
        img.convert_alpha()
        return img

    return {'background': load_image('background.png'),
            'balloon-flameon': load_image('player_flame_on.png'),
            'bird-up': load_image('bird_up.png'),
            'bird-down': load_image('bird_down.png'),
            'plane': load_image('plane.png'),
            'balloon-flameoff': load_image('player_flame_off.png')}


def frames_to_msec(frames, fps=FPS):
    return 1000.0 * frames / fps

def msec_to_frames(milliseconds, fps=FPS):
    return fps * milliseconds / 1000.0

def main():
    # Set up pygame and the screen
    pygame.init()
    screenInfo = pygame.display.Info()
    screen = pygame.display.set_mode((screenInfo.current_w, screenInfo.current_h), pygame.FULLSCREEN);
    pygame.display.set_caption('Flappy Balloon')
    screen.set_alpha(None)

    clock = pygame.time.Clock()
    images = load_images()

    images['background'] = pygame.transform.scale(images['background'], (screenInfo.current_w, screenInfo.current_h))
    screen.blit(images['background'], (0,0))

    balloon = Balloon(50, int(screenInfo.current_h/2 - Balloon.HEIGHT/2), 2, (images['balloon-flameoff'], images['balloon-flameon']))

    obstacles = deque()

    frame_clock = 0
    done = False

    while not done:
        clock.tick(FPS)

        if not(frame_clock % msec_to_frames(ADD_INTERVAL)):
            rand = randint(1,2)
            if rand == 1:
                obstacle = Bird((images['bird-up'], images['bird-down']))
            elif rand == 2:
                obstacle = Plane(images['plane'])

            obstacles.append(obstacle)

        for e in pygame.event.get():
            if e.type == QUIT or (e.type == KEYUP and e.key == K_ESCAPE):
                done = True
                break
            elif e.type == KEYUP and e.key in (K_UP, K_RETURN, K_SPACE):
                balloon.msec_to_climb = Balloon.CLIMB_DURATION


        balloon_collision = any(b.collides_with(balloon) for b in obstacles)
        if balloon_collision or 0 >= balloon.y or balloon.y >= WIN_HEIGHT - Balloon.HEIGHT:
            done = True

        while obstacles and not obstacles[0].visible:
            obstacles.popleft()

        balloon.update()
        # Redraw only the portion of the background where the balloon is
        screen.blit(images['background'], (balloon.rect.x, balloon.rect.y - 2), (balloon.rect.x, balloon.rect.y, balloon.rect.width, balloon.rect.height + 7))
        # Redraw the balloon
        screen.blit(balloon.image, balloon.rect)

        for b in obstacles:
            b.update()
            screen.blit(balloon.image, (b.rect.x, b.rect.y), Rect(b.rect.x, b.rect.y, b.rect.width, b.rect.height))
            screen.blit(images['background'], (b.rect.x, b.rect.y), Rect(b.rect.x, b.rect.y, b.rect.width + 5, b.rect.height))
            screen.blit(b.image, b.rect)



        pygame.display.flip()
        frame_clock += 1



    pygame.quit()



if __name__ == '__main__':
    main()
