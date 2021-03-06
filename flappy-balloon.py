#! /usr/bin/env python3

import math
import os
from random import randint
from collections import deque
import pygame
from pygame.locals import *

FPS = 60;
ANIMATION_SPEED = 0.30
CLOUD_SPEED = .10
WIN_WIDTH = 1820
WIN_HEIGHT = 980
ADD_INTERVAL = 7000
CLOUD_INTERVAL = 5000
OBSTACLE_GOAL = 10

GRAVITY = 2.81

class Balloon(pygame.sprite.Sprite):
    """
    WIDTH: Pixel width of the balloon
    HEIGHT: Pixel height of the balloon
    """

    WIDTH = 177
    HEIGHT = 250
    BURNER_SPEED = 10.0

    def __init__(self, x, y, images):
        pygame.sprite.Sprite.__init__(self)
        pygame.mixer.init()
        self.x, self.y = x, y
        self._img_flameoff, self._img_flameon = images
        self._mask_flameoff = pygame.mask.from_surface(self._img_flameoff)
        self._mask_flameon = pygame.mask.from_surface(self._img_flameon)

        try:
            self.burner = pygame.mixer.Sound("snd/burner.wav");
            self.burner.set_volume(0.2)
        except:
            print "Cannot load sound: burner.wav"
        self.dy = 0
        self.speed = Balloon.BURNER_SPEED

    def update(self, seconds):
        pressedkeys = pygame.key.get_pressed()
        self.ddy = 0.0

        if pressedkeys[pygame.K_UP]:
            self.burner.play()
            self.ddy = -1
        else:
            self.burner.stop()

        self.dy += (self.ddy * self.speed) + GRAVITY
        self.y += self.dy * seconds

	if self.y < (0 - Balloon.HEIGHT):
		self.y = WIN_HEIGHT
	elif (self.y > WIN_HEIGHT):
		self.y = 0 - Balloon.HEIGHT

    @property
    def image(self):
        pressedkeys = pygame.key.get_pressed()
        if pressedkeys[pygame.K_UP]:
            return self._img_flameon
        else:
            return self._img_flameoff

    @property
    def rect(self):
        return Rect(self.x, self.y, Balloon.WIDTH, Balloon.HEIGHT)

class Bird(pygame.sprite.Sprite):
    WIDTH = 237
    HEIGHT = 280
    FLAP_SPEED = 100 # ms delay between flaps

    def __init__(self, images):
        pygame.sprite.Sprite.__init__(self)
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

    def passed(self, x):
        return 0 < self.x < x

    @property
    def rect(self):
        return Rect(self.x, self.y + 40, Bird.WIDTH, Bird.HEIGHT + 75)

    def update(self, seconds):
        self.x -= ANIMATION_SPEED * (seconds * 1000)

    def collides_with(self, balloon):
        return pygame.sprite.collide_mask(self,balloon)


class Cloud(pygame.sprite.Sprite):
    WIDTH = 206
    HEIGHT = 130

    def __init__(self, clouds):
        pygame.sprite.Sprite.__init__(self)
        self.x = float(WIN_WIDTH - 1)
        self.y = randint(Cloud.HEIGHT, WIN_HEIGHT - Plane.HEIGHT)
        random_offset = randint(0, len(clouds) - 1)
        image_name = 'cloud-' + str(random_offset)
        self._img = clouds[image_name]
        self.mask = pygame.mask.from_surface(self._img)

    @property
    def image(self):
        return self._img

    @property
    def rect(self):
        return Rect(self.x, self.y, Cloud.WIDTH, Cloud.HEIGHT)

    @property
    def visible(self):
        return -300 < self.x < (WIN_WIDTH + 2)

    def update(self, seconds):
        self.x -= CLOUD_SPEED * (seconds * 1000)

class Plane(pygame.sprite.Sprite):
    WIDTH = 235
    HEIGHT = 144

    def __init__(self, image):
        pygame.sprite.Sprite.__init__(self)
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

    def passed(self, x):
        return 0 < self.x < x

    @property
    def rect(self):
        return Rect(self.x, self.y, Plane.WIDTH, Plane.HEIGHT)

    def update(self, seconds):
        self.x -= ANIMATION_SPEED * (seconds * 1000)

    def collides_with(self, balloon):
        return pygame.sprite.collide_mask(self,balloon)

class Jet(pygame.sprite.Sprite):
    WIDTH = 292
    HEIGHT = 160

    def __init__(self, image):
        pygame.sprite.Sprite.__init__(self)
        self.x = float(WIN_WIDTH - 1)
        self.score_counted = False
        self.y = randint(Jet.HEIGHT, WIN_HEIGHT - Jet.HEIGHT)
        self._img = image
        self.mask = pygame.mask.from_surface(self.image)

    @property
    def image(self):
        return self._img

    @property
    def visible(self):
        return -Jet.WIDTH < self.x < WIN_WIDTH

    def passed(self, x):
        return 0 < self.x < x

    @property
    def rect(self):
        return Rect(self.x, self.y, Jet.WIDTH, Jet.HEIGHT)

    def update(self, seconds):
        self.x -= ANIMATION_SPEED * (seconds * 1000)

    def collides_with(self, balloon):
        return pygame.sprite.collide_mask(self,balloon)

class Saucer(pygame.sprite.Sprite):
    WIDTH = 200
    HEIGHT = 160

    def __init__(self, image):
        pygame.sprite.Sprite.__init__(self)
        self.x = float(WIN_WIDTH - 1)
        self.score_counted = False
        self.y = randint(Saucer.HEIGHT, WIN_HEIGHT - Saucer.HEIGHT)
        self._img = image
        self.mask = pygame.mask.from_surface(self.image)

    @property
    def image(self):
        return self._img

    @property
    def visible(self):
        return -Saucer.WIDTH < self.x < WIN_WIDTH

    def passed(self, x):
        return 0 < self.x < x

    @property
    def rect(self):
        return Rect(self.x, self.y, Saucer.WIDTH, Saucer.HEIGHT)

    def update(self, seconds):
        self.x -= ANIMATION_SPEED * (seconds * 1000)

    def collides_with(self, balloon):
        return pygame.sprite.collide_mask(self,balloon)

def load_images():

    def load_image(img_file_name):
        file_name = os.path.join('.', 'images', img_file_name)
        img = pygame.image.load(file_name)
        img.convert_alpha()
        return img

    return {'balloon-flameon': load_image('player_flame_on_small.png'),
            'bird-up': load_image('bird_up.png'),
            'bird-down': load_image('bird_down.png'),
            'plane': load_image('plane.png'),
            'jet': load_image('fighter-jet.png'),
            'saucer': load_image('saucer.png'),
            'instructions': load_image('flappy-instructions.png'),
            'balloon-flameoff': load_image('player_flame_off_small.png')}


def load_clouds():

    def load_image(img_file_name):
        file_name = os.path.join('.', 'images', img_file_name)
        img = pygame.image.load(file_name)
        img.convert_alpha()
        return img

    return {'cloud-0': load_image('_cloud-0.png'),
            'cloud-1': load_image('_cloud-1.png'),
            'cloud-2': load_image('_cloud-2.png'),
            'cloud-3': load_image('_cloud-3.png'),
            'cloud-4': load_image('_cloud-4.png'),
            'cloud-5': load_image('_cloud-5.png')}

def msec_to_frames(milliseconds, fps=FPS):
    return fps * milliseconds / 1000.0


def main():
    # Set up pygame and the screen
    pygame.init()
    pygame.mixer.init()
    try:
        explosion = pygame.mixer.Sound("snd/explosion.wav");
    except:
        print "Cannot load sound: explosion.wav"
    screenInfo = pygame.display.Info()
    screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT), pygame.FULLSCREEN);
    pygame.display.set_caption('Flappy Balloon')
    screen.set_alpha(None)
    count = OBSTACLE_GOAL
    win = False
    pygame.mouse.set_visible(0)

    # initialize font; must be called after 'pygame.init()' to avoid 'Font not Initialized' error
    score_font = pygame.font.SysFont("monospace", 25, bold=True)
    result_font = pygame.font.SysFont("monospace", 50, bold=True)
    attribute_font = pygame.font.SysFont("monospace", 12, bold=False)

    images = load_images()
    clouds = load_clouds()


    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((51, 102, 153))
    screen.blit(background, (0, 0))

    screen.blit(images['instructions'], (410,0))

    pygame.display.flip()

    menu_clock = pygame.time.Clock()
    menu_frame_clock = 0
    menu_sprites = pygame.sprite.RenderPlain()
    menu_clouds = deque()

    start = False

    while not start:
        menu_milliseconds = menu_clock.tick(FPS)
        menu_seconds = menu_milliseconds / 1000.0

        for e in pygame.event.get():
            if e.type == KEYDOWN:
                start = True

        if not(menu_frame_clock % msec_to_frames(CLOUD_INTERVAL)):
            menu_cloud = Cloud(clouds)
            menu_sprites.add(menu_cloud)
            menu_clouds.append(menu_cloud)

        while menu_clouds and not menu_clouds[0].visible:
            menu_sprites.remove(menu_clouds[0])
            menu_clouds.popleft()

        menu_sprites.update(menu_seconds)
        screen.blit(background, (0,0))
        screen.blit(images['instructions'], (410,0))
        menu_sprites.draw(screen)

        pygame.display.flip()
        menu_frame_clock += 1

    balloon = Balloon(50, int(screenInfo.current_h/2 - Balloon.HEIGHT/2), (images['balloon-flameoff'], images['balloon-flameon']))
    clock = pygame.time.Clock()
    frame_clock = 0
    done = False
    exit = False
    obstacles = deque()

    allsprites = pygame.sprite.RenderPlain((balloon))
    pygame.mixer.music.load("snd/Jumpshot.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1, randint(0,90))

    while not done:
        milliseconds = clock.tick(FPS)
        seconds = milliseconds / 1000.0

        if not(frame_clock % msec_to_frames(ADD_INTERVAL)):
            rand = randint(1,4)
            if rand == 1:
                obstacle = Bird((images['bird-up'], images['bird-down']))
            elif rand == 2:
                obstacle = Plane(images['plane'])
            elif rand == 3:
                obstacle = Jet(images['jet'])
            elif rand == 4:
                obstacle = Saucer(images['saucer'])

            allsprites.add(obstacle)
            obstacles.append(obstacle)

        if not(frame_clock % msec_to_frames(CLOUD_INTERVAL)):
            cloud = Cloud(clouds)
            allsprites.add(cloud)

        for e in pygame.event.get():
            if e.type == QUIT or (e.type == KEYUP and e.key == K_ESCAPE):
                done = True
                exit = True
                break

        balloon_collision = any(b.collides_with(balloon) for b in obstacles)
        if balloon_collision:
            explosion.play()
            win = False
            done = True

        while obstacles and not obstacles[0].visible:
            allsprites.remove(obstacles[0])
            obstacles.popleft()

        for b in obstacles:
            if b.passed(balloon.rect.x) and b.score_counted == False:
                count -= 1
                b.score_counted = True
            if count == 0:
                done = True
                win = True


        allsprites.update(seconds)
        screen.blit(background, (0,0))
        allsprites.draw(screen)
        score_surface = score_font.render("Obstacles Left: %02d" % count, True, (255, 255, 255))
        score_x = WIN_WIDTH/2 - score_surface.get_width()/2
        screen.blit(score_surface, (score_x, 10))


        pygame.display.flip()
        frame_clock += 1


    pygame.mixer.music.stop()
    screen.blit(background,(0,0))

    if win:
        score_surface = result_font.render("YOU WIN!", True, (148, 242, 116))
        score_x = WIN_WIDTH/2 - score_surface.get_width()/2
        screen.blit(score_surface, (score_x, WIN_HEIGHT/2))
    else:
        score_surface = result_font.render("GAME OVER", True, (255, 255, 153))
        score_x = WIN_WIDTH/2 - score_surface.get_width()/2
        objects_left_surface = result_font.render("%02d Obstacles Remaining!" % count, True, (255, 255, 153))
        objects_left_x = WIN_WIDTH/2 - objects_left_surface.get_width()/2
        screen.blit(score_surface, (score_x, WIN_HEIGHT/2))
        screen.blit(objects_left_surface, (objects_left_x, WIN_HEIGHT/2 + 5 + score_surface.get_height()))



    attribute1_surface = attribute_font.render("Music: \"Jumpshot\" by Eric Skiff", True, (25, 50, 75))
    attribute1_y = WIN_HEIGHT - attribute1_surface.get_height() - 30
    attribute1_x = WIN_WIDTH - attribute1_surface.get_width() - 10
    screen.blit(attribute1_surface, (attribute1_x, attribute1_y))

    attribute2_surface = attribute_font.render("FX: \"Explosion 3\" by killkahn", True, (25, 50, 75))
    attribute2_y = WIN_HEIGHT - attribute2_surface.get_height() - 20
    attribute2_x = WIN_WIDTH - attribute2_surface.get_width() - 10
    screen.blit(attribute2_surface, (attribute2_x, attribute2_y))

    attribute3_surface = attribute_font.render("Developed by Enomalies", True, (25, 50, 75))
    attribute3_y = WIN_HEIGHT - attribute3_surface.get_height() - 10
    attribute3_x = WIN_WIDTH - attribute3_surface.get_width() - 10
    screen.blit(attribute3_surface, (attribute3_x, attribute3_y))


    pygame.display.update()
    if exit:
        pygame.mixer.quit()
        pygame.quit()
    else:
        pygame.time.wait(5000)
        pygame.mixer.quit()
        main()



if __name__ == '__main__':
    main()
