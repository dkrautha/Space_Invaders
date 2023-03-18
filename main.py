# Gabriel Costa: E-115-LK
# Cesar Espejo: E-115-LE
# E-115 Introduction to Programming Final Project
# We pledge our honor that we have abided by the Stevens Honor Code
# Built upon initially source of inspiration: https://www.youtube.com/watch?v=Q-__8Xw9KTM
#Need to import pygame in order to run code


import pygame
import os
import random
pygame.font.init()

Width, Height = 750, 750
WINDOW = pygame.display.set_mode((Width, Height))
pygame.display.set_caption("Space Invaders")

# Load images
Green_Spaceship = pygame.image.load(os.path.join("Images", "Enemy_Spaceship.png"))
Small_Green_Spaceship = pygame.image.load(os.path.join("Images", "Small_Enemy.png"))

# Player player
Main_Rocket = pygame.image.load(os.path.join("Images", "Main_Rocket.png"))

# Lasers
Rocket_Bullet = pygame.image.load(os.path.join("Images", "Rocket_Bullet.png"))
Big_Blast = pygame.image.load(os.path.join("Images", "Big_Blast.png"))
Small_Spaceship_Laser = pygame.image.load(os.path.join("Images", "Laser_Beam.png"))

# Background
Background = pygame.transform.scale(pygame.image.load(os.path.join("Images", "Background.png")), (Width, Height))


class Laser:
   def __init__(self, x, y, img):
       self.x = x
       self.y = y
       self.img = img
       self.mask = pygame.mask.from_surface(self.img)

   def draw(self, window):
       window.blit(self.img, (self.x, self.y))

   def move(self, vel):
       self.y += vel

   def off_screen(self, height):
       return not(height >= self.y >= 0)

   def collision(self, obj):
       return collide(self, obj)


class Blast:
   def __init__(self, x, y, img):
       self.x = x
       self.y = y
       self.img = img
       self.mask = pygame.mask.from_surface(self.img)

   def draw(self, window):
       window.blit(self.img, (self.x, self.y))

   def move(self, big_vel):
       self.y += big_vel

   def off_screen(self, height):
       return not(height >= self.y >= 0)

   def collision(self, obj):
       return collide(self, obj)


class Ship:
   COOLDOWN = 30

   def __init__(self, x, y, health=100):
       self.x = x
       self.y = y
       self.health = health
       self.ship_img = None
       self.laser_img = None
       self.lasers = []
       self.cool_down_counter = 0

   def draw(self, window):
       window.blit(self.ship_img, (self.x, self.y))
       for laser in self.lasers:
           laser.draw(window)

   def move_lasers(self, vel, obj):
       self.cooldown()
       for laser in self.lasers:
           laser.move(vel)
           if laser.off_screen(Height):
               self.lasers.remove(laser)
           elif laser.collision(obj):
               obj.health -= 10
               self.lasers.remove(laser)

   def cooldown(self):
       if self.cool_down_counter >= self.COOLDOWN:
           self.cool_down_counter = 0
       elif self.cool_down_counter > 0:
           self.cool_down_counter += 1

   def shoot(self):
       if self.cool_down_counter == 0:
           laser = Laser(self.x, self.y, self.laser_img)
           self.lasers.append(laser)
           self.cool_down_counter = 1

   def get_width(self):
       return self.ship_img.get_width()

   def get_height(self):
       return self.ship_img.get_height()


class Big_Ship:
   COOLDOWN = 60

   def __init__(self, x, y, health=100):
       self.x = x
       self.y = y
       self.health = health
       self.ship_img = None
       self.blast_img = None
       self.blast = []
       self.cool_down_counter = 0

   def draw(self, window):
       window.blit(self.ship_img, (self.x, self.y))
       for blast in self.blast:
           blast.draw(window)

   def move_blast(self, big_vel, obj):
       self.cooldown()
       for blast in self.blast:
           blast.move(big_vel)
           if blast.off_screen(Height):
               self.blast.remove(blast)
           elif blast.collision(obj):
               obj.health -= 30
               self.blast.remove(blast)

   def cooldown(self):
       if self.cool_down_counter >= self.COOLDOWN:
           self.cool_down_counter = 0
       elif self.cool_down_counter > 0:
           self.cool_down_counter += 1

   def shoot(self):
       if self.cool_down_counter == 0:
           blast = Blast(self.x, self.y, self.blast_img)
           self.blast.append(blast)
           self.cool_down_counter = 1

   def get_width(self):
       return self.ship_img.get_width()

   def get_height(self):
       return self.ship_img.get_height()


class Player(Ship):
   def __init__(self, x, y, health=100):
       super().__init__(x, y, health)
       self.ship_img = Main_Rocket
       self.laser_img = Rocket_Bullet
       self.mask = pygame.mask.from_surface(self.ship_img)
       self.max_health = health

   def move_lasers(self, vel, objs):
       self.cooldown()
       for laser in self.lasers:
           laser.move(vel)
           if laser.off_screen(Height):
               self.lasers.remove(laser)
           else:
               for obj in objs:
                   if laser.collision(obj):
                       objs.remove(obj)
                       if laser in self.lasers:
                           self.lasers.remove(laser)

   def draw(self, window):
       super().draw(window)
       self.healthbar(window)

   def healthbar(self, window):
       pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10,
                                              self.ship_img.get_width(), 10))
       pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10,
                                              self.ship_img.get_width() * (self.health/self.max_health), 10))


class Enemy(Ship):
   ENEMY_MAP = {
       "smallgreen": (Small_Green_Spaceship, Small_Spaceship_Laser)
   }

   def __init__(self, x, y, shiptype, health=100):
       super().__init__(x, y, health)
       self.ship_img, self.laser_img = self.ENEMY_MAP[shiptype]
       self.mask = pygame.mask.from_surface(self.ship_img)

   def move(self, vel):
       self.y += vel

   def shoot(self):
       if self.cool_down_counter == 0:
           laser = Laser(self.x+14, self.y, self.laser_img)
           self.lasers.append(laser)
           self.cool_down_counter = 1


class Big_Enemy(Big_Ship):
   ENEMY_MAP = {
       "green": (Green_Spaceship, Big_Blast),
   }

   def __init__(self, x, y, shiptype, health=100):
       super().__init__(x, y, health)
       self.ship_img, self.blast_img = self.ENEMY_MAP[shiptype]
       self.mask = pygame.mask.from_surface(self.ship_img)

   def move(self, big_vel):
       self.y += big_vel

   def shoot(self):
       if self.cool_down_counter == 0:
           blast = Blast(self.x+14, self.y, self.blast_img)
           self.blast.append(blast)
           self.cool_down_counter = 1


def collide(obj1, obj2):
   offset_x = obj2.x - obj1.x
   offset_y = obj2.y - obj1.y
   return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None  # (x,y)


def main():
   run = True
   FPS = 60
   level = 0
   lives = 5
   main_font = pygame.font.SysFont("comicsans", 50)
   lost_font = pygame.font.SysFont("comicsans", 60)

   enemies = []
   big_enemies = []
   wave_length = 5

   enemy_vel = 2
   big_enemy_vel = 1

   player_vel = 5
   laser_vel = 5
   blast_vel = 3

   player = Player(300, 650)

   clock = pygame.time.Clock()

   lost = False
   lost_count = 0

   def redraw_window():
       smallest_font = pygame.font.SysFont("comicsans", 20)
       WINDOW.blit(Background, (0, 0))
       # draw text
       lives_label = main_font.render(f"Lives: {lives}", True, (0, 0, 255))
       level_label = main_font.render(f"Level: {level}", True, (0, 0, 255))
       top_line = smallest_font.render("Press 'P' to go back to main menu", True, (255, 255, 255))

       WINDOW.blit(top_line, (Width / 2 - top_line.get_width() / 2, 30))
       WINDOW.blit(lives_label, (10, 10))
       WINDOW.blit(level_label, (Width - level_label.get_width() - 10, 10))

       for enemy in enemies:
           enemy.draw(WINDOW)
       for big_enemy in big_enemies:
           big_enemy.draw(WINDOW)

       player.draw(WINDOW)

       if lost:
           lost_label = lost_font.render("Game Over", True, (255, 255, 255))
           WINDOW.blit(lost_label, (Width/2 - lost_label.get_width()/2, 350))

       pygame.display.update()

   while run:
       clock.tick(FPS)
       redraw_window()

       if lives <= 0:
           lost = True
           lost_count += 1

       if player.health <= 0:
           player.health = 100
           lives -= 1

       if lost:
           if lost_count > FPS * 3:
               run = False
           else:
               continue

       if len(enemies) == 0:
           if len(big_enemies) == 0:
               level += 1
               wave_length += 1
               for i in range(wave_length):
                   enemy = Enemy(random.randrange(50, Width-100), random.randrange(-1500, -100),
                                 random.choice(["smallgreen"]))
                   enemies.append(enemy)
                   big_enemy = Big_Enemy(random.randrange(50, Width-100), random.randrange(-1500, -100),
                                         random.choice(["green"]))
                   big_enemies.append(big_enemy)

       for event in pygame.event.get():
           if event.type == pygame.QUIT:
               run = False

       keys = pygame.key.get_pressed()
       # left
       if keys[pygame.K_a] and player.x - player_vel > 0:
           player.x -= player_vel
       # right
       if keys[pygame.K_d] and player.x + player_vel + player.get_width() < Width:
           player.x += player_vel
       # up
       if keys[pygame.K_w] and player.y - player_vel > 550:
           player.y -= player_vel
       # down
       if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 20 < Height:
           player.y += player_vel
       # shoot
       if keys[pygame.K_SPACE]:
           player.shoot()
       # go back to main menu
       if keys[pygame.K_p]:
           main_menu()

       for enemy in enemies[:]:
           enemy.move(enemy_vel)
           enemy.move_lasers(laser_vel, player)

           if random.randrange(0, 2*60) == 1:
               enemy.shoot()

           if collide(enemy, player):
               player.health -= 10
               enemies.remove(enemy)

           elif enemy.y + enemy.get_height() > Height:
               lives -= 1
               enemies.remove(enemy)

       for big_enemy in big_enemies[:]:
           big_enemy.move(big_enemy_vel)
           big_enemy.move_blast(blast_vel, player)

           if random.randrange(0, 2*60) == 1:
               big_enemy.shoot()

           if collide(big_enemy, player):
               player.health -= 30
               big_enemies.remove(big_enemy)

           elif big_enemy.y + big_enemy.get_height() > Height:
               lives -= 1
               big_enemies.remove(big_enemy)

       player.move_lasers(-laser_vel, enemies)
       player.move_lasers(-laser_vel, big_enemies)


def text_objects(text, font):
   textSurface = font.render(text, True, (0, 0, 0))
   return textSurface, textSurface.get_rect()


def button(message, x, y, width, height, initcolor, actcolor, action=None):
   mouse = pygame.mouse.get_pos()
   click = pygame.mouse.get_pressed()

   if x + width > mouse[0] > x and y + height > mouse[1] > y:
       pygame.draw.rect(WINDOW, actcolor, (x, y, width, height))
       if click[0] == 1 and action != None:
           if action == "play":
               main()
           elif action == "control":
               how_to_play_menu()
           else:
               pass
   else:
       pygame.draw.rect(WINDOW, initcolor, (x, y, width, height))

   button_font = pygame.font.SysFont("comicsans", 40)
   textSurf, textRect = text_objects(message, button_font)
   textRect.center = ((x + (width/2)), (y + (height/2)))
   WINDOW.blit(textSurf, textRect)


def how_to_play_menu():
   font = pygame.font.SysFont("comicsans", 70)
   small_font = pygame.font.SysFont("comicsans", 30)
   smallest_font = pygame.font.SysFont("comicsans", 20)
   running = True
   while running:
       WINDOW.blit(Background, (0, 0))
       keys = pygame.key.get_pressed()
       first_line = font.render("How to Play", True, (255, 255, 255))
       WINDOW.blit(first_line, (Width / 2 - first_line.get_width() / 2, 150))
       second_line = small_font.render("'W' to move up", True, (255, 255, 255))
       WINDOW.blit(second_line, (Width / 2 - second_line.get_width() / 2, 300))
       third_line = small_font.render("'A' to move left", True, (255, 255, 255))
       WINDOW.blit(third_line, (Width / 2 - third_line.get_width() / 2, 325))
       fourth_line = small_font.render("'S' to move down", True, (255, 255, 255))
       WINDOW.blit(fourth_line, (Width / 2 - fourth_line.get_width() / 2, 350))
       fifth_line = small_font.render("'D' to move right", True, (255, 255, 255))
       WINDOW.blit(fifth_line, (Width / 2 - fifth_line.get_width() / 2, 375))
       sixth_line = small_font.render("'SPACE' to shoot", True, (255, 255, 255))
       WINDOW.blit(sixth_line, (Width / 2 - sixth_line.get_width() / 2, 400))
       seventh_line = small_font.render("If an enemy ship reaches the bottom of the screen, you lose a life", True,
                                        (255, 255, 255))
       WINDOW.blit(seventh_line, (Width / 2 - seventh_line.get_width() / 2, 450))
       eighth_line = small_font.render("If you lose all your health, you lose a life", True, (255, 255, 255))
       WINDOW.blit(eighth_line, (Width / 2 - eighth_line.get_width() / 2, 475))
       ninth_line = small_font.render("Lose all 5 lives and game is over", True, (255, 255, 255))
       WINDOW.blit(ninth_line, (Width / 2 - ninth_line.get_width() / 2, 500))
       tenth_line = small_font.render("Good luck and have fun :)", True, (255, 255, 255))
       WINDOW.blit(tenth_line, (Width / 2 - tenth_line.get_width() / 2, 550))
       bottom_line = smallest_font.render("Press esc to go back to main menu", True, (255, 255, 255))
       WINDOW.blit(bottom_line, (Width / 2 - bottom_line.get_width() / 2, 650))

       pygame.display.update()

       for event in pygame.event.get():
           if event.type == pygame.QUIT:
               running = False
           if keys[pygame.K_ESCAPE]:
               running = False
               main_menu()
   pygame.quit()


def main_menu():
   title_font = pygame.font.SysFont("System", 70)
   smallest_font = pygame.font.SysFont("comicsans", 20)
   run = True
   while run:
       WINDOW.blit(Background, (0, 0))
       keys = pygame.key.get_pressed()
       title_label = title_font.render("SPACE INVADERS", True, (255, 255, 255))
       WINDOW.blit(title_label, (Width/2 - title_label.get_width()/2, 150))
       bottom_line = smallest_font.render("Press esc to quit the game", True, (255, 255, 255))
       WINDOW.blit(bottom_line, (Width / 2 - bottom_line.get_width() / 2, 650))

       button("Start Game", 275, 300, 200, 50, (200, 200, 200), (255, 255, 255), "play")
       button("How to Play", 275, 450, 200, 50, (200, 200, 200), (255, 255, 255), "control")

       pygame.display.update()

       for event in pygame.event.get():
           if event.type == pygame.QUIT:
               run = False
           if keys[pygame.K_ESCAPE]:
               run = False
   pygame.quit()


main_menu()