# Frozen Jam by tgfcoder <https://twitter.com/tgfcoder> licensed under CC-BY-3
# Art from Kenney.nl
# https://pythonru.com/tag/pishem-igru-na-pygame

import pygame
import os
from random import randrange as rr, choice as rc, random
from pygame.locals import (
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
    K_SPACE
)

# Settings
WIDTH = 480
HEIGHT = 600
FPS = 60
POWER_UP_TIME = 5000

# Source paths
img_dir = os.path.join(os.path.dirname(__file__), 'src/img')
meteors_dir = os.path.join(img_dir, 'Meteors')
snd_dir = os.path.join(os.path.dirname(__file__), 'src/snd')
expl_dir = os.path.join(img_dir, 'blasts')

# Inits
pygame.init()
pygame.mixer.init()
colors = pygame.Color
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()
font_name = pygame.font.match_font('arial')

# Pictures
bkg = pygame.image.load(os.path.join(img_dir, 'bg.jpg')).convert()
bkg = pygame.transform.scale(bkg, (WIDTH, HEIGHT))
bkg_rect = bkg.get_rect()

player_img = pygame.image.load(os.path.join(img_dir, "playerShip1_green.png"))
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(colors('black'))

meteor_imgs = tuple(pygame.image.load(os.path.join(meteors_dir, img)) for img in os.listdir(meteors_dir))
bullet_img = pygame.image.load(os.path.join(img_dir, "laserRed16.png"))

explosion_anim = {'lg': [], 'sm': [], 'player': []}
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(os.path.join(expl_dir, filename)).convert()
    img.set_colorkey(colors('black'))
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)
    filename = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(os.path.join(expl_dir, filename)).convert()
    img.set_colorkey(colors('black'))
    explosion_anim['player'].append(img)

power_up_images = {'shield': pygame.image.load(os.path.join(img_dir, 'shield_gold.png')),
                   'gun': pygame.image.load(os.path.join(img_dir, 'bolt_gold.png'))}

# Sounds
shoot_sound = pygame.mixer.Sound(os.path.join(snd_dir, 'pew.wav'))
improved_shoot_sound = pygame.mixer.Sound(os.path.join(snd_dir, 'pu_sound.wav'))
extra_gun_sound = pygame.mixer.Sound(os.path.join(snd_dir, 'gun.wav'))
shield_sound = pygame.mixer.Sound(os.path.join(snd_dir, 'shield.wav'))
expl_sounds = [pygame.mixer.Sound(os.path.join(snd_dir, x)) for x in os.listdir(snd_dir) if 'expl' in x]
pygame.mixer.music.load(os.path.join(snd_dir, 'tgfcoder-FrozenJam-SeamlessLoop.ogg'))
pygame.mixer.music.set_volume(0.2)


def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, colors('White'))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def new_mob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)


def draw_shield_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    bar_length = 100
    bar_height = 10
    fill = (pct / 100) * bar_length
    outline_rect = pygame.Rect(x, y, bar_length, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    pygame.draw.rect(surf, colors('Green'), fill_rect)
    pygame.draw.rect(surf, colors('White'), outline_rect, 2)


def draw_lives(surf, x, y, lives, img):
    for index in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * index
        img_rect.y = y
        surf.blit(img, img_rect)


def show_go_screen():
    screen.blit(bkg, bkg_rect)
    draw_text(screen, 'SOMETHING', 64, WIDTH // 2, HEIGHT // 4)
    draw_text(screen, "Arrow keys move, Space to fire", 22, WIDTH // 2, HEIGHT // 2)
    draw_text(screen, "Press a key to begin", 18, WIDTH // 2, HEIGHT * 3 // 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
            if ev.type == pygame.KEYUP:
                waiting = False


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(colors('black'))
        self.rect = self.image.get_rect()
        self.radius = self.rect.height // 2
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speed_x = 0
        self.shield = 100
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 1
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_time = pygame.time.get_ticks()

    def update(self):
        key_state = pygame.key.get_pressed()
        if key_state[K_LEFT] and self.rect.left > 0:
            player.speed_x = -8
        elif key_state[K_RIGHT] and self.rect.right < WIDTH:
            player.speed_x = 8
        elif key_state[K_SPACE]:
            self.shoot()
        self.rect.x += self.speed_x
        self.speed_x = 0
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10
        if self.power > 1 and pygame.time.get_ticks() - self.power_time > POWER_UP_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            elif self.power >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1, bullet2)
                bullets.add(bullet1, bullet2)
                improved_shoot_sound.play()

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)

    def power_up(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()


class Mob(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image_orig = rc(meteor_imgs).convert()
        self.image_orig.set_colorkey(colors('black'))
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = self.rect.width * .85 // 2
        self.rect.x = rr(WIDTH - self.rect.width)
        self.rect.y = rr(-100, -40)
        self.speed_y = rr(1, 8)
        self.speed_x = rr(-3, 3)
        self.rect = self.image.get_rect()
        self.rot = 0
        self.rot_speed = rr(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            self.image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        if self.rect.top > HEIGHT + 10:
            self.rect.x = rr(WIDTH - self.rect.width)
            self.rect.y = rr(-100, -40)
            self.speed_y = rr(1, 8)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_img.convert()
        self.image.set_colorkey(colors('black'))
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speed_y = -10

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.bottom < 0:
            self.kill()


class PowerUp(Bullet):
    def __init__(self, x, y, pics):
        super().__init__(x, y)
        self.prize = rc([k for k, v in pics.items()])
        self.image = pics[self.prize]
        self.speed_y = 2

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > HEIGHT:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        super().__init__()
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 100

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
for _ in range(8):
    new_mob()
bullets = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
power_ups = pygame.sprite.Group()

score = 0
# pygame.mixer.music.play(loops=-1)
game_over = True
running = True

while running:
    clock.tick(FPS)
    if game_over:
        show_go_screen()
        game_over = False
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        power_ups = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        score = 0
        for i in range(8):
            new_mob()

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False

    all_sprites.update()

    collisions = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    for collision in collisions:
        rc(expl_sounds).play()
        player.shield -= collision.radius * 2
        expl = Explosion(collision.rect.center, 'sm')
        all_sprites.add(expl)
        new_mob()
        if player.shield <= 0:
            death_expl = Explosion(player.rect.center, 'player')

            all_sprites.add(death_expl)
            player.hide()
            player.lives -= 1
            player.shield = 100

    if player.lives == 0 and not death_expl.alive():
        # running = False
        game_over = True
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        score += int(50 - hit.radius)
        rc(expl_sounds).play()
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        if random() > 0.9:
            power_up = PowerUp(*hit.rect.center, pics=power_up_images)
            all_sprites.add(power_up)
            power_ups.add(power_up)
        new_mob()

    power_up_hits = pygame.sprite.spritecollide(player, power_ups, True)
    for p_hit in power_up_hits:
        if p_hit.prize == 'shield':
            player.shield += rr(10, 30)
            shield_sound.play()
            if player.shield >= 100:
                player.shield = 100
        if p_hit.prize == 'gun':
            extra_gun_sound.play()
            player.power_up()

    screen.fill(colors('black'))
    screen.blit(bkg, bkg_rect)
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, WIDTH / 2, 10)
    draw_shield_bar(screen, 5, 5, player.shield)
    draw_lives(screen, WIDTH - 100, 5, player.lives, player_mini_img)
    pygame.display.flip()

pygame.quit()
