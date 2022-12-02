from asyncio import FastChildWatcher
import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
test_font = pygame.font.Font('font/Pixeltype.ttf', 50)


SPEED = 60


class FlappyBirdAI:

    def __init__(self, w=700, h=800):
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h)) #set the display mode
        pygame.display.set_caption('Flappy')

        #IMAGES TO BE USED
        self.skySurface = pygame.image.load('graphics/city.png').convert()
        self.sky_surface = pygame.transform.scale(self.skySurface, (700,700))
        self.groundSurface = pygame.image.load('graphics/ground.png').convert()
        self.pipe_image = pygame.image.load('graphics/pipe.png').convert()
        self.pipe_image = pygame.transform.scale(self.pipe_image, (72, 500))
        self.pipe_image_flip = pygame.transform.flip(self.pipe_image, False, True)
        self.kirby_surface = pygame.image.load('graphics/player/kirby1.png').convert_alpha()
        self.kirby_surface1 = pygame.transform.scale(self.kirby_surface, (64, 84))
        self.kirby_surface2 = pygame.image.load('graphics/player/kirby2.png').convert_alpha()
        self.kirby_surface2  = pygame.transform.scale(self.kirby_surface2 , (64, 84))
        self.kirby_jump = pygame.image.load('graphics/player/kirby3.png').convert_alpha()
        self.kirby_jump = pygame.transform.scale(self.kirby_jump, (64, 84))

        #important stuff
        self.ground_rect = self.groundSurface.get_rect(topleft = (0,700)) #creates the rect for the ground
        self.clock = pygame.time.Clock()
        self.floor_rect = self.groundSurface.get_rect(topleft = (0,700))
        self.reset()



    def reset(self):
        # init game state
        self.frame_iteration = 0
        self.score = 0

        #info on the kirbs
        self.kirbY = 300 #intial position of kirby
        self.kirbGravity = 0

        #info on the pipe
        self.pipeX = 800
        self.pointsCollect = False

        self.heightOfBottom = 450
        self.pipeBotRet = self.pipe_image.get_rect(topleft = (self.pipeX,self.heightOfBottom)) 
        self.pipeTopRet = self.pipe_image_flip.get_rect(bottomleft = (self.pipeX,self.heightOfBottom - 300))
        self.kirbRect = self.kirby_surface1.get_rect(midbottom = (80,self.kirbY))


        
    def place_pipe(self):
        self.pipeX = 800
    


    def play_step(self, action):
        lock = 1
        
        while lock > 0:
            self.frame_iteration += 1
            # 1. collect user input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            
            # 2. move
            #moves the kirby
            if action[0] == 1:
                self.kirbGravity = -17
                self.kirbY += (self.kirbGravity/2)
                self.kirbRect.y = self.kirbY
                lock+= 9
                action[0] = 0
            else:
                
                self.kirbGravity += 0.8
                self.kirbY += self.kirbGravity
                self.kirbRect.y = self.kirbY
            
            # 3. check if game over
            #check if hit floor or pipe
            reward = 0
            game_over = False
            if self.kirbRect.colliderect(self.ground_rect) or self.kirbRect.colliderect(self.pipeBotRet) or self.kirbRect.colliderect(self.pipeTopRet):
                game_over = True
                reward = -1000
                return reward, game_over, self.frame_iteration
            #check if hit ceiling
            if self.kirbRect.y < -120:
                game_over = True
                reward = -1000
                return reward, game_over, self.frame_iteration

            # 4. place new food or just move
            self.pipeX -= 5
            self.pipeBotRet.x = self.pipeX
            self.pipeTopRet.x = self.pipeX

            if self.pipeBotRet.x + 72 < self.kirbRect.x and self.pointsCollect is False:
                self.score += 1
                reward = 50
                self.pointsCollect = True

            if self.pipeBotRet.x < -100:
                self.pipeX = 800
                self.pipeBotRet.x = self.pipeX
                self.pipeTopRet.x = self.pipeX
                self.pointsCollect = False
            

            
            # 5. update ui and clock
            self._update_ui()
            self.clock.tick(SPEED)
            lock -= 1
        
        # 6. return game over and score
        return reward, game_over, self.frame_iteration


    def is_collision(self, pt=None):
        print('collision')
        
        # hits floor
        
        # hits pipe


    def _update_ui(self):
        self.display.blit(self.sky_surface,(0,0))
        self.display.blit(self.groundSurface, self.ground_rect)
        self.display.blit(self.kirby_surface1,self.kirbRect)
        self.display.blit(self.pipe_image, self.pipeBotRet)
        self.display.blit(self.pipe_image_flip, self.pipeTopRet)

        score_surf = test_font.render(f'Score: {self.frame_iteration}',False,(64,64,64))
        score_rect = score_surf.get_rect(center = (350,50))
        self.display.blit(score_surf,score_rect)

        pygame.display.flip()


    def _move(self, action):
        print('move')