# Frozen Jam by tgfcoder <https://twitter.com/tgfcoder> licensed under CC-BY-3
# Art from Kenney.nl
# https://pythonru.com/tag/pishem-igru-na-pygame


# TODO: Реализовть масштабирование
# TODO: функция выхода
# TODO: почистить код от повторений
# TODO: раскидать по модулям
# TODO: убрать глобалы
# TODO: паузы и эскейпы
# TODO: highscore
# TODO: переделать мышь


import pygame as pg
import os
import pyautogui
from random import randrange as rr, choice as rc, random as rnd
from pygame.locals import (
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
    K_SPACE,
    K_p
)


# Settings
monitor_width, monitor_height = pyautogui.size()
# RATIO = 0.75
# PROPORTION = 0.8
SIZE = WIDTH, HEIGHT = 800, 1000
CENTER = CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2
FPS = 60
MUSIC = True
SOUND = True
LIVES = 3
EXTRA_GUN_TIME = 5000
TEXT_SIZE = HEIGHT // 20

# Tools
pth = os.path
join_path = pth.join
colors = pg.Color
time = pg.time

# Source paths
SRC = join_path(pth.dirname(__file__), 'src')
IMG = join_path(SRC, 'img')
ENV_OBJS = join_path(IMG, 'Meteors')
BLASTS = join_path(IMG, 'blasts')
SND = join_path(SRC, 'snd')

# Inits
pg.init()
pg.mixer.init()
pg.display.set_caption("Stupid Plane")
screen = pg.display.set_mode(SIZE)
pg.mouse.set_visible(False)


class Player(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = set_image(IMG, 'plane.png').convert()
        self.start_position = CENTER_X, HEIGHT - self.image.get_height() // 2
        self.rect = self.image.get_rect(center=self.start_position)
        self.image.set_colorkey(colors('black'))
        self.radius = self.rect.height // 2
        self.last_update = time.get_ticks()
        self.shoot_delay = 250
        self.shield = 100
        self.lives = LIVES if LIVES < 99 else 99
        self.hidden = False
        self.hide_time = time.get_ticks()
        self.gun = 1
        self.extra_gun_time = time.get_ticks()
        mouse_position = monitor_width // 2, \
                         monitor_height - (monitor_height - HEIGHT) // 2 - self.image.get_height() // 2
        pyautogui.moveTo(mouse_position)

    def update(self):
        if not self.hidden:
            self.rect.center = pg.mouse.get_pos()
        press_keys = pg.key.get_pressed()
        if press_keys[K_UP] and self.rect.top > 0:
            self.rect.move_ip(0, -9)
        if press_keys[K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.move_ip(0, 9)
        if press_keys[K_LEFT] and self.rect.left > -30:
            self.rect.move_ip(-9, 0)
        if press_keys[K_RIGHT] and self.rect.right < WIDTH + 30:
            self.rect.move_ip(9, 0)
        if not self.hidden:
            pg.mouse.set_pos(self.rect.center)

        if press_keys[K_SPACE] or pg.mouse.get_pressed(3)[0]:
            self.shoot()

        if self.hidden and time.get_ticks() - self.hide_time > 1000:
            self.hidden = False
            self.rect.center = self.start_position
            pg.mouse.set_pos(self.start_position)

        if self.gun >= 2 and time.get_ticks() - self.extra_gun_time > EXTRA_GUN_TIME:
            self.gun -= 1
            self.extra_gun_time = time.get_ticks()

    def shoot(self):
        now = time.get_ticks()
        if now - self.last_update > self.shoot_delay:
            if self.gun == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
            elif self.gun >= 2:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                left_bullet = Bullet(self.rect.x, self.rect.centery, left=True)
                right_bullet = Bullet(self.rect.x + self.rect.width, self.rect.centery, right=True)
                all_sprites.add(bullet, left_bullet, right_bullet)
                bullets.add(bullet, left_bullet, right_bullet)
            if SOUND:
                if self.gun == 1:
                    shoot_sound.play()
                else:
                    extra_gun_sound.play()
            self.last_update = now

    def hide(self):
        self.hidden = True
        self.hide_time = time.get_ticks()
        self.rect.center = CENTER_X, HEIGHT + 200
        pg.mouse.set_pos(WIDTH // 2, HEIGHT - self.image.get_height())

    def extra_gun(self):
        self.gun += 1
        self.extra_gun_time = time.get_ticks()


class Mob(pg.sprite.Sprite):
    def __init__(self, pics: list):
        super().__init__()
        self.image = set_image(IMG, rc(pics)).convert()
        self.image.set_colorkey(colors('black'), RLEACCEL)
        self.rect = self.image.get_rect(center=(rr(0, WIDTH), rr(-200, 50)))
        self.radius = self.rect.width * .85 // 2
        self.speed_y = rr(1, 8)
        self.speed_x = rr(-3, 3)
        self.shift = rr(1, 10)

    def update(self):
        self.rect.y += self.speed_y
        if not self.shift % 2: self.rect.x += self.speed_x
        if self.rect.top > HEIGHT + 10:
            self.rect.x = rr(WIDTH - self.rect.width)
            self.rect.y = rr(-100, -40)
            self.speed_y = rr(1, 8)


class Meteor(pg.sprite.Sprite):
    def __init__(self, pics: list):
        super().__init__()
        self.base_img = set_image(ENV_OBJS, rc(pics)).convert()
        self.base_img.set_colorkey(colors('black'), RLEACCEL)
        self.image = self.base_img.copy()
        self.rect = self.image.get_rect(center=(rr(0, WIDTH), rr(-200, 50)))
        self.radius = self.rect.width * .85 // 2
        self.speed_y = rr(1, 8)
        self.speed_x = rr(-3, 3)
        self.shift = rr(1, 10)
        self.rot = 0
        self.rot_speed = rr(-8, 8)
        self.last_update = time.get_ticks()

    def rotate(self):
        now = time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            rot_image = pg.transform.rotate(self.base_img, self.rot)
            prev_center = self.rect.center
            self.image = rot_image
            self.rect = self.image.get_rect()
            self.rect.center = prev_center

    def update(self):
        self.rotate()
        self.rect.y += self.speed_y
        if not self.shift % 2: self.rect.x += self.speed_x
        if self.rect.top > HEIGHT + 10:
            self.kill()
            add_sprites(all_sprites, meteors, Meteor, 1, meteors_imgs)


class Bullet(pg.sprite.Sprite):
    def __init__(self, x, y, left=False, right=False):
        super().__init__()
        self.image = set_image(IMG, 'laserGreen11.png')
        self.rect = self.image.get_rect()
        self.left = left
        self.right = right
        if left or right: self.additional_weapon()
        self.rect.x = x - self.image.get_width() / 2
        self.rect.y = y - self.image.get_height() / 2
        self.speed_y = -10

    def additional_weapon(self):
        self.image = set_image(IMG, 'laserRed01.png')
        if self.left:
            self.image = pg.transform.rotate(self.image, 10)
        if self.right:
            self.image = pg.transform.rotate(self.image, -10)

    def update(self):
        if self.left:
            self.rect.x -= 2
        if self.right:
            self.rect.x += 2
        self.rect.y += self.speed_y
        if self.rect.bottom < 0: self.kill()


class Explosion(pg.sprite.Sprite):
    def __init__(self, imgs, center, size=None):
        super().__init__()
        self.images = imgs
        self.image = self.images[0]
        if size:
            self.scaled_size = HEIGHT // size, HEIGHT // size
            self.change_size()
            self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = time.get_ticks()
        self.frame_rate = 100

    def change_size(self):
        self.images = [pg.transform.scale(img, self.scaled_size) for img in self.images]

    def update(self):
        now = time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(self.images):
                self.kill()
            else:
                center = self.rect.center
                self.image = self.images[self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


class PowerUp(pg.sprite.Sprite):
    def __init__(self, coordinates, image, name):
        super().__init__()
        self.name = name
        self.image = image
        self.rect = self.image.get_rect(center=coordinates)
        self.speed = 2

    def update(self):
        self.rect.y += self.speed
        if self.rect.y > HEIGHT:
            self.kill()


def set_image(src_path, image_name):
    return pg.image.load(join_path(src_path, image_name))


def add_sprites(sprites, name, obj, quantity, img):
    for _ in range(quantity):
        sprite = obj(img)
        name.add(sprite)
        sprites.add(sprite)


def draw_text(surf, text, size, center_x, center_y, color='White'):
    text_surface = pg.font.SysFont('Arial', size).render(text, True, colors(color))
    text_surface_rect = text_surface.get_rect()
    text_surface_rect.center = center_x, center_y
    surf.blit(text_surface, (text_surface_rect.x, text_surface_rect.y))


def get_pause():
    background_size = WIDTH / 1.3, TEXT_SIZE * 3
    background = pg.surface.Surface(background_size)
    background_rect = background.get_rect(center=CENTER)

    pause_text = 'PAUSE'
    pause_text_x = background.get_width() / 2
    pause_text_y = background.get_height() - background.get_height() / 4 * 3

    any_key_text = 'Press any key except "p"'
    any_key_text_x = background.get_width() / 2
    any_key_text_y = background.get_height() - background.get_height() / 4

    draw_text(background, pause_text, TEXT_SIZE, pause_text_x, pause_text_y, 'Red')
    draw_text(background, any_key_text, TEXT_SIZE, any_key_text_x, any_key_text_y, 'Red')
    screen.blit(background, background_rect)

    pg.display.update()


def show_kills(killed):
    score = f'{killed}'
    draw_text(surf=screen, text=score, size=TEXT_SIZE, center_x=CENTER_X, center_y=TEXT_SIZE)


def life(surf, sprite):
    life_bar_coordinates = WIDTH // 20, HEIGHT * 0.03

    # Shield
    if sprite.shield < 0:
        sprite.shield = 0
    bar_length = WIDTH // 6
    bar_height = HEIGHT * 0.03
    fill = sprite.shield / 100 * bar_length
    outline_rect = pg.Rect(*life_bar_coordinates, bar_length, bar_height)
    fill_rect = pg.Rect(*life_bar_coordinates, fill, bar_height)
    if sprite.shield > 50:
        pg.draw.rect(surf, colors('Green'), fill_rect)
        pg.draw.rect(surf, colors('White'), outline_rect, 2)
    elif 50 >= sprite.shield > 25:
        pg.draw.rect(surf, colors('Orange'), fill_rect)
        pg.draw.rect(surf, colors('Orange'), outline_rect, 2)
    else:
        pg.draw.rect(surf, colors('Red'), fill_rect)
        pg.draw.rect(surf, colors('Red'), outline_rect, 3)

    # Lives
    live_img = set_image(IMG, 'playerLife3_red.png')
    live_img_x = WIDTH - live_img.get_width() * 2
    live_img_y = TEXT_SIZE - live_img.get_height() / 2
    if sprite.lives <= 3:
        for _ in range(sprite.lives):
            screen.blit(live_img, (live_img_x, live_img_y))
            live_img_x -= live_img.get_width()
    else:
        screen.blit(live_img, (live_img_x, live_img_y))
        live_img_x -= live_img.get_width()
        amount_center_y = TEXT_SIZE
        draw_text(screen, f'{sprite.lives} x  ', TEXT_SIZE, live_img_x, amount_center_y)


def init_extra(xlife, xshield, xgun, coord):
    if rnd() >= 0.98:
        x_life = PowerUp(coordinates=coord, image=xlife, name='life')
        all_sprites.add(x_life)
        exrtas.add(x_life)
    elif rnd() >= 0.97:
        x_gun = PowerUp(coordinates=coord, image=xgun, name='gun')
        all_sprites.add(x_gun)
        exrtas.add(x_gun)
    elif rnd() >= 0.96:
        x_shield = PowerUp(coordinates=coord, image=xshield, name='shield')
        all_sprites.add(x_shield)
        exrtas.add(x_shield)


def captured_extra(name):
    if name == 'life':
        if player.lives < 99:
            player.lives += 1
        if SOUND: extra_life_sound.play()

    elif name == 'shield':
        player.shield += rr(20, 50)
        if SOUND: shield_sound.play()
        if player.shield > 100:
            player.shield = 100
    elif name == 'gun':
        if SOUND: improved_shoot_sound.play()
        player.extra_gun()


def death():
    global death_expl
    death_expl = Explosion(death_imgs, player.rect.center)
    all_sprites.add(death_expl)
    player.hide()
    if player.alive():
        return True
    else:
        return death_expl.alive()


def player_collide(*args, current_state=None):
    for sprite in args:
        collisions = pg.sprite.spritecollide(player, sprite, True, pg.sprite.collide_circle)
        for collision in collisions:
            if sprite == exrtas:
                captured_extra(collision.name)
                return current_state
            player.shield -= collision.radius
            all_sprites.add(Explosion(blast_imgs, collision.rect.center, size=16))
            if SOUND: rc(expl_sounds).play()
            if sprite == meteors:
                add_sprites(all_sprites, sprite, Meteor, 1, meteors_imgs)
            elif sprite == enemies:
                add_sprites(all_sprites, sprite, Mob, 1, enemies_imgs)
            if player.shield <= 0:
                if player.lives > 0:
                    player.lives -= 1
                    player.shield = 100
                    return death()
                else:
                    player.kill()
                    return death()

    return current_state


def hits():
    result = 0
    pg.sprite.groupcollide(bullets, meteors, True, False)
    hits_ = pg.sprite.groupcollide(bullets, enemies, True, True)
    for hit in hits_:
        result += 1
        if SOUND: rc(expl_sounds).play()
        add_sprites(all_sprites, enemies, Mob, 1, enemies_imgs)
        all_sprites.add(Explosion(blast_imgs, hit.rect.center, size=8))
        init_extra(xlife=life_extra, xshield=shield_extra, xgun=gun_extra, coord=hit.rect.center)
    return result


# def highscore(name, score):
#     with open(join_path(SRC, 'highscore.txt'), 'r+') as h_score:
#         print(h_score.readlines())
#         # for i in h_score.readlines():
#         #     print(i)
#
#
# highscore(345, 345)


# def show_highscore():
#     pass


def hello_screen():
    screen.blit(bkg, bkg.get_rect())
    draw_text(screen, "Stupid Plane", 64, WIDTH // 2, HEIGHT // 4, color='green')
    draw_text(screen, "Arrow keys move, Space to fire", 22, WIDTH // 2, HEIGHT // 2)
    draw_text(screen, "Press a key to begin, ESC to exit", 18, WIDTH // 2, HEIGHT * 3 // 4)
    pg.display.flip()
    while True:
        time.Clock().tick(FPS)
        for ev in pg.event.get():
            if ev.type == QUIT:
                return False
            elif ev.type == KEYDOWN and ev.key == K_ESCAPE:
                return False
            elif ev.type == KEYDOWN and not ev.key == K_ESCAPE:
                return True


# Images
bkg = set_image(IMG, 'bg.jpg').convert()
bkg = pg.transform.scale(bkg, SIZE)

blast_imgs = [set_image(BLASTS, img) for img in os.listdir(BLASTS) if 'regular' in img]
death_imgs = [set_image(BLASTS, img) for img in os.listdir(BLASTS) if 'sonic' in img]

life_extra = set_image(IMG, 'star_gold.png')
shield_extra = set_image(IMG, 'shield_gold.png')
gun_extra = set_image(IMG, 'bolt_gold.png')

# Sprites
all_sprites = pg.sprite.Group()

meteors = pg.sprite.Group()
meteors_imgs = [pic for pic in os.listdir(ENV_OBJS)]
add_sprites(all_sprites, meteors, Meteor, 5, meteors_imgs)

enemies = pg.sprite.Group()
enemies_imgs = ['enemy_smile.png']
add_sprites(all_sprites, enemies, Mob, 10, enemies_imgs)

bullets = pg.sprite.Group()

exrtas = pg.sprite.Group()

player = Player()
all_sprites.add(player)

death_expl = Explosion(death_imgs, player.rect.center)

# Sound
shoot_sound = pg.mixer.Sound(join_path(SND, 'pew.wav'))
improved_shoot_sound = pg.mixer.Sound(join_path(SND, 'gun.wav'))
shield_sound = pg.mixer.Sound(join_path(SND, 'shield.wav'))
extra_life_sound = pg.mixer.Sound(join_path(SND, 'extra_life.wav'))
extra_gun_sound = pg.mixer.Sound(join_path(SND, 'pu_sound.wav'))
expl_sounds = [pg.mixer.Sound(join_path(SND, x)) for x in os.listdir(SND) if 'expl' in x]
pg.mixer.music.load(join_path(SND, 'tgfcoder-FrozenJam-SeamlessLoop.ogg'))
pg.mixer.music.set_volume(0.2)
if MUSIC: pg.mixer.music.play(loops=-1)

# Game loop
running = True
pause = False
kills = 0
game = False

while running:
    time.Clock().tick(FPS + kills)
    if not game:
        running = hello_screen()
        game = True
        all_sprites = pg.sprite.Group()
        meteors = pg.sprite.Group()
        meteors_imgs = [pic for pic in os.listdir(ENV_OBJS)]
        add_sprites(all_sprites, meteors, Meteor, 5, meteors_imgs)
        enemies = pg.sprite.Group()
        enemies_imgs = ['enemy_smile.png']
        add_sprites(all_sprites, enemies, Mob, 10, enemies_imgs)
        bullets = pg.sprite.Group()
        exrtas = pg.sprite.Group()
        player = Player()
        all_sprites.add(player)
        kills = 0
        player.lives = LIVES
    for event in pg.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                game = False
            if event.key == K_p:
                pause = True
            else:
                pause = False
    if pause:
        get_pause()
        continue

    all_sprites.update()

    screen.blit(bkg, bkg.get_rect())

    all_sprites.draw(screen)

    show_kills(kills)
    if game:
        game = player_collide(enemies, meteors, exrtas, current_state=running)

    if not player.alive() and not death_expl.alive():
        game = False

    kills += hits()

    life(screen, player)

    pg.display.flip()

pg.quit()
