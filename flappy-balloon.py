#! /usr/bin/env python3

import math
import os
import pygame
from pygame.locals import *

FPS = 60;

class Balloon(pygame.sprite.Sprite):
    
    """
    WIDTH: Pixel width of the balloon
    HEIGHT: Pixel height of the balloon
    SINK_SPEED: Speed in pixels/ms that the balloon descends while not climbing
    CLIMB_SPEED: Speed in p/ms that the balloon ascends while climbing (on average)
    CLIMB_DURATION: The # of ms for the balloon to make a complete ascent
    """

    WIDTH = HEIGHT = 32
    SINK_SPEED = 0.18
    CLIMB_SPEED = 0.25
    CLIMB_DURATION = 333.3

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


def load_images():

    def load_image(img_file_name):
	file_name = os.path.join('.', 'images', img_file_name)
	img = pygame.image.load(file_name)
	img.convert()
	return img

    return {'background': load_image('background.png'),
	    'balloon-flameon': load_image('balloon_flame_on.png'),
	    'balloon-flameoff': load_image('balloon_flame_off.png')}


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

    frame_clock = 0
    done = False

    while not done:
	clock.tick(FPS)


	for e in pygame.event.get():
	    if e.type == QUIT or (e.type == KEYUP and e.key == K_ESCAPE):
		done = True
		break
	    elif e.type == KEYUP and e.key in (K_UP, K_RETURN, K_SPACE):
		balloon.msec_to_climb = Balloon.CLIMB_DURATION

	for x in (0, screenInfo.current_w / 2):
	    screen.blit(images['background'], (x, 0))

	balloon.update()
	screen.blit(balloon.image, balloon.rect)

	pygame.display.flip()
	frame_clock += 1

    pygame.quit()



if __name__ == '__main__':
    main()
