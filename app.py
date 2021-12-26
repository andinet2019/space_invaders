import pygame, random
from pygame import mixer
from alien import Aliens
from explosion import Explosion

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

# pixel speed per second
clock = pygame.time.Clock()
fps = 60

# setting game display size
screen_width = 600
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Space Invaders by Andinet')

# font size for text
font_30 = pygame.font.SysFont('Constantia', 30)
font_40 = pygame.font.SysFont('Constantia', 40)
font_50 = pygame.font.SysFont('Constantia', 50)

# game start sound
starting_sound = pygame.mixer.Sound("img/alienstart.wav")
starting_sound.set_volume(0.75)

# game won sound
won_sound = pygame.mixer.Sound("img/won.wav")
won_sound.set_volume(1.0)

# setting colors to use it later
orange = (255, 69, 0)
red = (255, 0, 0)
green = (0, 255, 0)
dark_green = (0, 100, 0)
white = (255, 255, 255)
# game end sound
game_end_sound = pygame.mixer.Sound("img/gameover.wav")
game_end_sound.set_volume(0.75)

# saving the sound files in variables
explosion_bullet = pygame.mixer.Sound("img/explosion.wav")
explosion_bullet.set_volume(0.75)

explosion2_alien = pygame.mixer.Sound("img/explosion2.wav")
explosion2_alien.set_volume(0.75)

spaceship_laser = pygame.mixer.Sound("img/laser.wav")
spaceship_laser.set_volume(0.75)

# define variables for later use
rows = 5
cols = 5

alien_cooldown = 1000  # bullet cooldown in milliseconds
countdown = 3

last_alien_shot = pygame.time.get_ticks()
last_count = pygame.time.get_ticks()

# game over = 0 means game is not over, 1 is player has won, -1 to mean player has lost
game_over = 0

# setting game background image
bg = pygame.image.load("img/bg2.png")


def draw_bg():
    """
    method to draw background image
    :return:
    """
    screen.blit(bg, (0, 0))


def draw_text(text, font, text_col, x, y):
    """
    method to draw text on game screen
    :return:
    """
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


class Spaceship(pygame.sprite.Sprite):
    """
    class for creating spaceship
    """

    def __init__(self, x, y, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/spaceship.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        # setting speed
        speed = 8
        # a variable to create a time interval between successive shots
        cooldown = 500  # milliseconds
        game_over = 0

        # get key press
        key = pygame.key.get_pressed()
        # left movement
        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= speed
            # right movement
        if key[pygame.K_RIGHT] and self.rect.right < screen_width:
            self.rect.x += speed

        now = pygame.time.get_ticks()  # current time
        # shoot
        if key[pygame.K_SPACE] and now - self.last_shot > cooldown:
            spaceship_laser.play()
            bullet = Bullets(self.rect.centerx, self.rect.top)
            bullet_group.add(bullet)
            self.last_shot = now

        # update mask
        self.mask = pygame.mask.from_surface(self.image)

        # health bar for spaceship
        pygame.draw.rect(screen, red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 15))
        if self.health_remaining > 0:
            pygame.draw.rect(screen, green, (
                self.rect.x, (self.rect.bottom + 10),
                int(self.rect.width * (self.health_remaining / self.health_start)),
                15))
        elif self.health_remaining <= 0:
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            self.kill()
            game_over = -1

        return game_over


class Bullets(pygame.sprite.Sprite):
    """
    class for creating the bullet
    """

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y -= 5
        # when reach bottom bullet disappear
        if self.rect.bottom < 0:
            self.kill()
        if pygame.sprite.spritecollide(self, alien_group, True):
            self.kill()
            explosion_bullet.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)


class Alien_Bullets(pygame.sprite.Sprite):
    """
    class for creating alien bulet
    """

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/alien_bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y += 2
        if self.rect.top > screen_height:
            self.kill()
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            self.kill()
            explosion2_alien.play()

            spaceship.health_remaining -= 1
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)


# create sprite groups
spaceship_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()


def create_aliens():
    #creating  aliens using for loop in rows and columns
    for row in range(rows):
        for item in range(cols):
            alien = Aliens(100 + item * 100, 100 + row * 70)
            alien_group.add(alien)


create_aliens()

# creating spaceship player ,3 is the max life
spaceship = Spaceship(int(screen_width / 2), screen_height - 100, 3)
spaceship_group.add(spaceship)

run = True
while run:

    clock.tick(fps)

    # draw background image for the game
    draw_bg()

    if countdown == 0:
        # create random alien bullets
        # record current time
        now = pygame.time.get_ticks()
        # shoot
        if now - last_alien_shot > alien_cooldown and len(alien_bullet_group) < 5 and len(alien_group) > 0:
            attacking_alien = random.choice(alien_group.sprites())
            alien_bullet = Alien_Bullets(attacking_alien.rect.centerx, attacking_alien.rect.bottom)
            alien_bullet_group.add(alien_bullet)
            last_alien_shot = now

        # check if all the aliens have been killed
        if len(alien_group) == 0:
            game_over = 1

        if game_over == 0:
            # update spaceship
            game_over = spaceship.update()

            # update sprite groups
            bullet_group.update()
            alien_group.update()
            alien_bullet_group.update()
        else:
            if game_over == -1:
                draw_text('GAME OVER LOOSER!', font_40, red, int(screen_width / 2 - 100), int(screen_height / 2 + 50))
                game_end_sound.play()

            if game_over == 1:
                draw_text('YOU WON!', font_40, green, int(screen_width / 2 - 100), int(screen_height / 2 + 50))
                won_sound.play()

    if countdown > 0:
        starting_sound.play()
        draw_text('READY!', font_40, dark_green, int(screen_width / 2 - 10), int(screen_height / 2 + 50))
        draw_text(str(countdown), font_50, orange, int(screen_width / 2 - 10), int(screen_height / 2 + 100))
        count_timer = pygame.time.get_ticks()
        if count_timer - last_count > 1000:
            countdown -= 1
            last_count = count_timer

    # update explosion group
    explosion_group.update()

    # draw sprite groups
    spaceship_group.draw(screen)
    bullet_group.draw(screen)
    alien_group.draw(screen)
    alien_bullet_group.draw(screen)
    explosion_group.draw(screen)

    # handling game events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
