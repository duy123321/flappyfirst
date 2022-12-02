from xml.etree.ElementTree import TreeBuilder
import pygame
from sys import exit
from random import randint, choice

from pyparsing import White

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        player_walk_1 = pygame.image.load('graphics/player/kirby1.png').convert_alpha()#64 84
        player_walk_1 = pygame.transform.scale(player_walk_1, (64, 84))
        player_walk_2 = pygame.image.load('graphics/player/kirby2.png').convert_alpha()
        player_walk_2 = pygame.transform.scale(player_walk_2, (64, 84))
        self.player_walk = [player_walk_1,player_walk_2]
        self.player_index = 0
        self.player_jump = pygame.image.load('graphics/player/kirby3.png').convert_alpha()
        self.player_jump = pygame.transform.scale(self.player_jump, (64, 84))

        self.image = self.player_walk[self.player_index]
        self.rect = self.image.get_rect(midbottom = (80,300))
        self.gravity = 0

        self.jump_sound = pygame.mixer.Sound('audio/sfx_wing.mp3')
        self.jump_sound.set_volume(0.5)

        self.jumpLock = 0

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.jumpLock <= 0:
            self.gravity = -17
            self.jump_sound.play()
            self.jumpLock = 10

    def apply_gravity(self):
        self.gravity += 0.8
        self.rect.y += self.gravity
        if self.rect.bottom >= 700:
            return True

    def animation_state(self):
        if self.rect.bottom < 300: 
            self.image = self.player_jump
        else:
            self.player_index += 0.1
            if self.player_index >= len(self.player_walk):self.player_index = 0
            self.image = self.player_walk[int(self.player_index)]

    def update(self):
        self.player_input()
        self.animation_state()
        self.jumpLock -= 1
        self.apply_gravity()

    def reset(self):
        self.rect = self.image.get_rect(midbottom = (80,300))

class BotPipe(pygame.sprite.Sprite):
    def __init__(self,height):
        super().__init__()

        self.image = pygame.image.load('graphics/pipe.png').convert()
        self.image = pygame.transform.scale(self.image, (72, 500))
        self.rect = self.image.get_rect(topleft = (800,height))

    def destroy(self):
        if self.rect.x <= -100: 
            self.kill()

    def update(self):
        self.rect.x -= 5
        self.destroy()

class UpPipe(pygame.sprite.Sprite):
    def __init__(self,height):
        super().__init__()

        self.image = pygame.image.load('graphics/pipe.png').convert()
        self.image = pygame.transform.scale(self.image, (72, 500))
        self.image = pygame.transform.flip(self.image, False, True)

        self.rect = self.image.get_rect(bottomleft = (800,height - 300))
    def destroy(self):
        if self.rect.x <= -100: 
            self.kill()

    def update(self):
        self.rect.x -= 5
        self.destroy()



class Floor(pygame.sprite.Sprite):
     def __init__(self):
        super().__init__()

        self.image = pygame.image.load('graphics/ground.png').convert()
        self.rect = self.image.get_rect(topleft = (0,700))


def display_score():
    current_time = int(pygame.time.get_ticks() / 1000) - start_time
    score_surf = test_font.render(f'Score: {current_time}',False,(64,64,64))
    score_rect = score_surf.get_rect(center = (350,50))
    screen.blit(score_surf,score_rect)
    return current_time


pygame.init()
screen = pygame.display.set_mode((700,800))
pygame.display.set_caption('Runner')
clock = pygame.time.Clock()
test_font = pygame.font.Font('font/Pixeltype.ttf', 50)
game_active = False
start_time = 0
score = 0

#Groups
player = pygame.sprite.GroupSingle()
player.add(Player())

obstacle_group = pygame.sprite.Group()
floor = pygame.sprite.Group()
floor.add(Floor())

sky_surface = pygame.image.load('graphics/city.png').convert()
sky_surface = pygame.transform.scale(sky_surface, (700,700))
ground_surface = pygame.image.load('graphics/ground.png').convert()
ground_rect = ground_surface.get_rect(topleft = (0,700))

# Intro screen
player_stand = pygame.image.load('graphics/player/kirby1.png').convert_alpha()
player_stand_rect = player_stand.get_rect(center = (350,200))

game_name = test_font.render('Machine Learning Flappy Bird',False,(111,196,169))
game_name_rect = game_name.get_rect(center = (350,80))

game_message = test_font.render('Press space to Start',False,(111,196,169))
game_message_rect = game_message.get_rect(center = (350,330))

# Timer 
obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer,2500)

def collision_sprite():
    if pygame.sprite.spritecollide(player.sprite,obstacle_group,False):
        obstacle_group.empty()
        return False
    if pygame.sprite.spritecollide(player.sprite, floor, False):
        obstacle_group.empty()
        return False
    else: return True

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if game_active:
            if event.type == obstacle_timer:
                pipeY = randint(350, 650)
                obstacle_group.add(BotPipe(pipeY))
                obstacle_group.add(UpPipe(pipeY))

        
        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_active = True
                start_time = int(pygame.time.get_ticks() / 1000)

    if game_active:
        screen.blit(sky_surface,(0,0))
        # screen.blit(ground_surface,ground_rect)
        
        player.draw(screen)
        obstacle_group.draw(screen)
        floor.draw(screen)
        player.update()

        #screen.blit(obs.pipeDraw,(500,500))
        obstacle_group.update()

        game_active = collision_sprite()
        score = display_score()
        
    else:
        screen.fill("white")
        screen.blit(player_stand,player_stand_rect)

        score_message = test_font.render(f'Your score: {score}',False,(111,196,169))
        score_message_rect = score_message.get_rect(center = (350,330))
        screen.blit(game_name,game_name_rect)

        player.sprites()[0].reset()

        if score == 0: screen.blit(game_message,game_message_rect)
        else: screen.blit(score_message,score_message_rect)

    pygame.display.update()
    clock.tick(60)