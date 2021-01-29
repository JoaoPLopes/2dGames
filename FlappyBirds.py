import pygame as pg
from pygame.compat import geterror
import random
import numpy as np
from LoadData import *

SCREEN_WIDHT = 525
SCREEN_HEIGHT = 700

base_image = "base.png"
BASE_YPOS = 600 #22

bird_image = "FlappyBird.png"
BIRD_WIDHT = 55
BIRD_HEIGHT = 45

background_imgae = "FlappyBirdBackground.png"

pipe_image = "pipe.png"
PIPE_WIDHT = 85
PIPE_HEIGHT = 500

FPS = 120 # Game Frame rate [fps]

class Pipe(pg.sprite.Sprite):
    def __init__(self, yPos, kind):
        pg.sprite.Sprite.__init__(self)   
        self.image, self.rect = load_image(pipe_image)
        self.image = pg.transform.scale(self.image, (PIPE_WIDHT,PIPE_HEIGHT))
        self.mask = pg.mask.from_surface(self.image)
        self.xvelocity = -2
        self.rect = self.image.get_rect()
        self.xPos = pg.display.get_surface().get_rect().width # define initial X position as the width of the screen
        self.overpast = 0
        if kind == "BOTTOM_PIPE":
            self.rect.topleft = (self.xPos, yPos) # initial position
        elif kind == "TOP_PIPE":
            rotate = pg.transform.rotate
            self.image = rotate(self.image, -180)
            self.rect.bottomleft = (self.xPos, yPos) # initial position

    def update(self):
        self.rect.move_ip(self.xvelocity,0) # moves tree pixeis in one frame
        if self.rect.right < 0:
            self.kill()
        self.move = 1


class Bird(pg.sprite.Sprite):
    def __init__(self, fps):
        pg.sprite.Sprite.__init__(self) # call Sprite initializar
        self.image, self.rect = load_image(bird_image,-1)
        self.initialRotation = 15 # Rotation when the bird jumps; 15 degrees upwards
        self.image = pg.transform.scale(self.image, (BIRD_WIDHT,BIRD_HEIGHT))
        rotate = pg.transform.rotate
        self.original = rotate(self.image, self.initialRotation)
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)
        self.area = pg.display.get_surface().get_rect() # get area of the game screen
        self.rect.topright = (self.area.width/2,200) # initial position
        self.samplingTime = 1/fps # update 120 times per second
        self.acceleartion = 1000 # pixeis/s^-2
        self.terminalVelocity = 400 # pixeis por segundo
        self.yvelocity = 0 # velocity of the bird
        self.jumping = 0
        self.jump = -600 # pixeis

    
    def update(self):
        if self.jumping > 0:
            self._jump()
        else:
            self._fall()

    def _fall(self):
        if self.yvelocity < self.terminalVelocity:
            self.yvelocity = self.yvelocity + self.samplingTime*self.acceleartion
            delta = 200 # to make te bird keep its orientation before starting to bilt
            if self.yvelocity < delta:
                pass
            else:
                rotate = pg.transform.rotate
                self.image = rotate(self.original, -(90+self.initialRotation)*(self.yvelocity-delta)/(self.terminalVelocity-delta))
            self.mask = pg.mask.from_surface(self.image) # A new mask needs to be recreated each time a sprite's image is changed
        self.rect.move_ip(0,self.samplingTime*self.yvelocity) # move x pixeis
        if self.rect.bottom > self.area.bottom:
            self.kill() # Kill removes sprit from all groups

    def _jump(self):
        self.image = self.original
        self.mask = pg.mask.from_surface(self.image) # new mask from new image     
        self.yvelocity = 0
        self.jumping = 0
        self.rect.move_ip(0,self.samplingTime*self.jump) # move x pixeis


class Game():
    def __init__(self):
        self.screen = pg.display.set_mode((SCREEN_WIDHT,SCREEN_HEIGHT)) # size of the screen; returns a surface object
        pg.display.set_caption("Flappy Birds")
        pg.mouse.set_visible(0)

        # Create The Game Backgound
        self.background = pg.Surface((SCREEN_WIDHT,SCREEN_HEIGHT))
        self.background = self.background.convert()

        image = load_image(background_imgae)[0] # get first output -> image, rect = load_image()
        pos = image.get_rect(top = 0 , left = 0)
        image = pg.transform.scale(image, (SCREEN_WIDHT,SCREEN_HEIGHT))
        self.background.blit(image,pos) 

        # Display The Background
        self.screen.blit(self.background, (0, 0))
        pg.display.flip()


        # Prepare Game Objects
        self.font = load_font("FlappyBirdy.ttf",36)
        self.scoreFont = load_font("FlappyBirdy.ttf",106)


        self.clock = pg.time.Clock()
        self.fps = FPS # frames per second

        self.bird = pg.sprite.RenderPlain(Bird(self.fps))

        yPos =  random.randint(np.round(SCREEN_HEIGHT/3), np.round(2*SCREEN_HEIGHT/3)) # places middle of the pipe between 1/3 and 2/3 of the screen
        self.pipe = pg.sprite.RenderPlain(Pipe(yPos, "BOTTOM_PIPE"), Pipe(yPos-135, "TOP_PIPE"))

        self.pause = 0

        # Create Events
        # NEW PIPE EVENT (A NEW PIPE COMES EVERY X MILLISECONDS)
        self.newPipe = pg.USEREVENT + 1
        pg.time.set_timer(self.newPipe,1400) # 1000 miliseconds = 1 seconds

        # Create Game stats and flags
        self.going = True
        self.score = 0

    def run(self):

        while(self.going):
            self.clock.tick(self.fps)

            self.__check_collision()

            if self.bird.sprites() == []: # If bird dies after collision enter pause menu
                self.pause = 1
                self.__pause()

            # Handle Input Events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.going = False
                elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    self.going = False
                elif event.type == self.newPipe:
                    yPos =  random.randint(np.round(SCREEN_HEIGHT/3), np.round(2*SCREEN_HEIGHT/3)) # places middle of the pipe between 1/3 and 2/3 of the screen
                    self.pipe.add(Pipe(yPos, "BOTTOM_PIPE"), Pipe(yPos-135, "TOP_PIPE"))

            # To be able to move while pressing key continously seperate from new events loop  
            keys = pg.key.get_pressed()
            if keys[pg.K_SPACE]: # If space bar is pressed activate jumping flag used in the update method
                self.bird.sprites()[0].jumping = 1

            # Update Sprites
            self.pipe.update()
            self.bird.update()

            # Draw Everything
            self.screen.blit(self.background, (0, 0)) # always draw background to "erase" previous frame

            self.bird.draw(self.screen)
            self.pipe.draw(self.screen)
            
            self.__draw_score()
            self.__draw_base()

            pg.display.flip()


    def __pause(self):
        self.score = 0
            
        # Draw Everything
        self.screen.blit(self.background, (0, 0)) # always draw background to "erase" previous frame
            
        text = self.font.render("Press c to restart", 1, (10, 10, 10)) #render(text, antialias, color, background=None)
        textpos = text.get_rect(centerx=SCREEN_WIDHT / 2, centery = SCREEN_HEIGHT / 2 ) # centra ao meio do ecra
        self.screen.blit(text, textpos) # bilt Draws a source Surface onto this Surface.    
            
        self.__draw_base()
            
        pg.display.flip()
        while(self.pause==1): # PAUSING MENU; After the bird being killed                
            for sprite in self.pipe.sprites():
                sprite.kill()
                
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.pause = 0
                    self.going = False
                elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    self.pause = 0
                    self.going = False
                elif event.type == pg.KEYDOWN and event.key == pg.K_c: # press "c" to continue
                    self.bird.add(Bird(self.fps))
                    self.pause = 0

    def __check_collision(self):

        for p in self.pipe: # check colision between bird and all pipes
            if [] != pg.sprite.spritecollide(p, self.bird, True, pg.sprite.collide_mask):
                p.kill()


    def __draw_score(self):
        if self.pipe.sprites() != []:
            if self.pipe.sprites()[0].overpast == 0:
                if self.pipe.sprites()[0].rect.right < self.bird.sprites()[0].rect.left:
                    self.score +=1
                    self.pipe.sprites()[0].overpast = 1

        x = SCREEN_WIDHT/2
        y = 100

        score = str(self.score)
        text = self.scoreFont.render(score,  1, (255, 255, 255)) # render(text, antialias, color, background=None)
        textpos = text.get_rect(left = x , centery = y) # centra ao meio do ecra
        self.screen.blit(text, textpos) # bilt Draws a source Surface onto this Surface

    def __draw_base(self):
        image = load_image(base_image)[0]
        image = pg.transform.scale(image, (SCREEN_WIDHT,112))
        pos = image.get_rect(top = BASE_YPOS , left = 0)
        self.screen.blit(image,pos)



# this calls the 'main' function when this script is executed
if __name__ == "__main__":
    pg.init()
    game = Game()
    game.run()
    pg.quit()