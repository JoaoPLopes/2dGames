import pygame as pg
from pygame.compat import geterror
import random
import numpy as np
from LoadData import *
import pickle
import Controller as cnt

SCREEN_WIDHT = 525
SCREEN_HEIGHT = 700

base_image = "base.png"
BASE_YPOS = 600 

bird_image = "FlappyBird.png"
BIRD_WIDHT = 55
BIRD_HEIGHT = 45

background_imgae = "FlappyBirdBackground.png"

pipe_image = "pipe.png"
PIPE_WIDHT = 85
PIPE_HEIGHT = 500
GAP = 130

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
        if self.rect.bottom > BASE_YPOS:
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

        # Load Image Of The Base And Set Its Inital Position
        self.baseImage = load_image(base_image)[0]
        self.baseImage = pg.transform.scale(self.baseImage, (SCREEN_WIDHT,112))
        self.basePos = 0


        # Prepare Game Objects
        self.font = load_font("FlappyBirdy.ttf",36)
        self.scoreFont = load_font("FlappyBirdy.ttf",106)


        self.clock = pg.time.Clock()
        self.fps = FPS # frames per second

        self.bird = pg.sprite.RenderPlain(Bird(self.fps))

        self.pipe = pg.sprite.RenderPlain()

        # Create Events
        # NEW PIPE EVENT (A NEW PIPE COMES EVERY X MILLISECONDS)
        self.newPipe = pg.USEREVENT + 1
        self.pipeTimer = 0 # milliseconds (Initialized with zero to only trigger the interruption after the player starts playing (see __pause() , the game starts there))
        pg.time.set_timer(self.newPipe,self.pipeTimer) # 1000 miliseconds = 1 seconds

        # Create Game stats and flags
        self.going = True
        self.score = 0
        self.pause = 1
        self.playing = 1
        
        # Controller Variables
        self.ref = SCREEN_HEIGHT/2
        self.pos = self.bird.sprites()[0].rect.centery
        self.controller = cnt.Controller(-1)

        try:
            self.bestScore = pickle.load(open("bestScore.pickle", "rb"))["best"]
        except:
            self.bestScore = 0
            pickle.dump({"best": self.bestScore}, open("bestScore.pickle", "wb"))

    def run(self):

        while(self.going):
            self.clock.tick(self.fps)

            self.__check_collision()

            if self.bird.sprites() == []: # If bird dies after collision enter pause menu
                self.pause = 1
            
            if self.pause == 1:
                self.__pause()

            # Handle Input Events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.going = False
                elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    self.going = False
                elif event.type == self.newPipe:
                    yPos =  random.randint(np.round(SCREEN_HEIGHT/3), np.round(2*SCREEN_HEIGHT/3)) # places middle of the pipe between 1/3 and 2/3 of the screen
                    self.pipe.add(Pipe(yPos, "BOTTOM_PIPE"), Pipe(yPos-GAP, "TOP_PIPE"))
                    if self.pipeTimer == 3000: # First pipe come after 3 seconds. But after the firt all come after 1.4 seconds
                        self.pipeTimer = 1400 #  millisenconds (changing the timer after the first pipe was released)
                        pg.time.set_timer(self.newPipe,self.pipeTimer) # 1000 miliseconds = 1 seconds
                        self.ref = self.pipe.sprites()[0].rect.top - GAP/2 
                elif event.type == pg.KEYDOWN and event.key == pg.K_q and self.playing == 0: # I 'q' is pressed with the controller playing go to the pause menu
                    self.pause = 1

            if self.playing == 1: # Check if it playing time or if the user chose the controller to play
                # To be able to move while pressing key continously seperate from new events loop  
                keys = pg.key.get_pressed()
                if keys[pg.K_SPACE]: # If space bar is pressed activate jumping flag used in the update method
                    self.bird.sprites()[0].jumping = 1
            else:
                self.pos = self.bird.sprites()[0].rect.centery # "Measure" bird position   
                if self.controller.control(self.ref, self.pos) > 0:
                    self.bird.sprites()[0].jumping = 1

            

            # Update Sprites
            self.bird.update()
            self.pipe.update()

            # Draw Everything
            self.screen.blit(self.background, (0, 0)) # always draw background to "erase" previous frame

            self.bird.draw(self.screen)
            self.pipe.draw(self.screen)
            
            self.__draw_base()
            if self.playing == 0:
                self.__write_text((SCREEN_WIDHT / 2, BASE_YPOS + 50), "Press 'q' to quit!", (10, 10, 10), self.font)
            self.__draw_score()

            pg.display.flip()


    def __pause(self):
        if self.score > self.bestScore:
            self.bestScore = self.score
            pickle.dump({"best": self.bestScore}, open("bestScore.pickle", "wb"))
        
        self.score = 0
        self.basePos = 0 # Reset position of the base to zero

        # Draw Everything
        self.screen.blit(self.background, (0, 0)) # always draw background to "erase" previous frame

        self.__write_text((SCREEN_WIDHT / 2, SCREEN_HEIGHT / 2 - 50), "Press 'c' and let the controller play!", (10, 10, 10), self.font)

        self.__write_text((SCREEN_WIDHT / 2, SCREEN_HEIGHT / 2 - 25), "or", (10, 10, 10), self.font)

        self.__write_text((SCREEN_WIDHT / 2, SCREEN_HEIGHT / 2), "Press 'p' to play!", (10, 10, 10), self.font)

        self.__write_text((SCREEN_WIDHT / 2, SCREEN_HEIGHT / 2 + 50), "Best = "+ str(self.bestScore), (10, 10, 10), self.font)

        self.__draw_base()
            
        pg.display.flip()
        while(self.pause==1): # PAUSING MENU; After the bird being killed                
            for sprite in self.pipe.sprites(): # Kill existing pipes
                sprite.kill()
            
            for sprite in self.bird.sprites(): # Kill exinsting bird
                sprite.kill()
                
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.pause = 0
                    self.going = False
                elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    self.pause = 0
                    self.going = False
                elif event.type == pg.KEYDOWN and event.key == pg.K_p: # press "p" to continue
                    self.pipeTimer = 3000 #  millisenconds
                    pg.time.set_timer(self.newPipe,self.pipeTimer) # 1000 miliseconds = 1 seconds
                    self.pause = 0
                    self.playing = 1
                elif event.type == pg.KEYDOWN and event.key == pg.K_c:
                    self.pause = 0
                    self.playing = 0
                    self.pipeTimer = 3000 #  millisenconds
                    pg.time.set_timer(self.newPipe,self.pipeTimer) # 1000 miliseconds = 1 seconds
                elif event.type == self.newPipe:
                    pass
        
        self.bird.add(Bird(self.fps)) # Create new bird before going to the game


    def __check_collision(self):

        for p in self.pipe: # check colision between bird and all pipes
            if [] != pg.sprite.spritecollide(p, self.bird, True, pg.sprite.collide_mask):
                p.kill()


    def __draw_score(self):
        if self.pipe.sprites() != [] and self.bird != []:
            if self.pipe.sprites()[0].overpast == 0:
                if self.pipe.sprites()[0].rect.right < self.bird.sprites()[0].rect.left:
                    self.score +=1
                    self.pipe.sprites()[0].overpast = 1
                    self.ref = self.pipe.sprites()[2].rect.top - GAP/2 # Since a pipe is past new reference is computed
        

        self.__write_text((SCREEN_WIDHT/2, 100), str(self.score),(255,255,255), self.scoreFont)

    def __draw_base(self):
        """ private method that draws the moving base in the screen;
            the moving efect is achieved by moving the place where the figure is 
            drawn every frame. To have a base covering the entire screen game 
            two images are placed one after the other. When the position of the first reaches 
            2 times the screen width then starts drawing again at zero
        Parameters
        ----------
        """
        self.basePos -= 2
        pos = self.baseImage.get_rect(top = BASE_YPOS , left = self.basePos)
        if pos[0] < -SCREEN_WIDHT:
            pos[0] = 0
            self.basePos = 0
        
        self.screen.blit(self.baseImage,pos)

        pos = self.baseImage.get_rect(top = BASE_YPOS , left = self.basePos + SCREEN_WIDHT) 
        self.screen.blit(self.baseImage,pos)


    def __write_text(self, pos, text, color, font):
        """ private method intended to write text on the screen
        pos = (x, y)  Is the central coordinates to place the text
        
        Parameters
        ----------
        pos : (int,int)
            The central coordinates where to place the text
        text : str
            The text to write; must be a single line
        color: (int,int,int)
            The color of the text in RGB
        font: pg.Font
            The font with wich the text is written 
        """
        text = font.render(text, 1, color) #render(text, antialias, color, background=None)
        textpos = text.get_rect(centerx=pos[0], centery = pos[1] ) # centra ao meio do ecra
        self.screen.blit(text, textpos) # bilt Draws a source Surface onto this Surface.s




# this calls the 'main' function when this script is executed
if __name__ == "__main__":
    pg.init()
    game = Game()
    game.run()
    pg.quit()