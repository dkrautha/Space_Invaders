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
   wave_length = 5

   enemy_vel = 2

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

       WINDOW.blit(lives_label, (10, 10))
       WINDOW.blit(level_label, (Width - level_label.get_width() - 10, 10))

       for enemy in enemies:
           enemy.draw(WINDOW)

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
            level += 1
            wave_length += 1
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, Width-100), random.randrange(-1500, -100),
                                random.choice(["smallgreen"]))
                enemies.append(enemy)

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

       player.move_lasers(-laser_vel, enemies)


def text_objects(text, font):
   textSurface = font.render(text, True, (0, 0, 0))
   return textSurface, textSurface.get_rect()

main()