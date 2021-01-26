import os
import pygame as pg
from pygame.compat import geterror
import random
import numpy as np

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, "data")

# functions to create our resources
def load_image(name, colorkey=None):
    fullname = os.path.join(data_dir, name)
    try:
        image = pg.image.load(fullname)
    except pg.error:
        print("Cannot load image:", fullname)
        raise SystemExit(str(geterror()))
    image = image.convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pg.RLEACCEL)
    return image, image.get_rect()

def load_font(name, size):
    fullname = os.path.join(data_dir, name)
    try:
        font = pg.font.Font(fullname, size)
    except:
        font = pg.font.Font(None, size)
    return font

class Pipe(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)   
        self.image, self.rect = load_image("pipe.png")
        self.image = pg.transform.scale(self.image, (85,500))
        self.mask = pg.mask.from_surface(self.image)
        self.xvelocity = -2
        self.rect = self.image.get_rect()
        self.area = pg.display.get_surface().get_rect() # get area of the game screen
        self.overpast = 0

    def update(self):
        self.rect.move_ip(self.xvelocity,0) # moves tree pixeis in one frame
        if self.rect.right < 0:
            self.kill()
        self.move = 1

class BottomPipe(Pipe):
    def __init__(self, yPos):
        Pipe.__init__(self)
        self.rect.topleft = (self.area.width, yPos) # initial position

class TopPipe(Pipe):
    def __init__(self, yPos):
        Pipe.__init__(self)
        rotate = pg.transform.rotate
        self.image = rotate(self.image, -180)
        self.rect.bottomleft = (self.area.width, yPos) # initial position

class Bird(pg.sprite.Sprite):
    def __init__(self, fps):
        pg.sprite.Sprite.__init__(self) # call Sprite initializar
        self.image, self.rect = load_image("FlappyBird.png",-1)
        self.initialRotation = 15 # Rotation when the bird jumps; 15 degrees upwards
        self.image = pg.transform.scale(self.image, (55,45))
        rotate = pg.transform.rotate
        self.original = rotate(self.image, self.initialRotation)
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)
        self.area = pg.display.get_surface().get_rect() # get area of the game screen
        self.rect.topright = (self.area.width/2,200) # initial position
        self.samplingTime = 1/fps # update 120 times per second
        self.acceleartion = 680 # pixeis/s^-2
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
        #rotate = pg.transform.rotate
        #self.image = rotate(self.image, 0)
        self.rect.move_ip(0,self.samplingTime*self.jump) # move x pixeis


class Game():
    def __init__(self):
        self.screen = pg.display.set_mode((525,700)) # size of the screen; returns a surface object
        pg.display.set_caption("Flappy Birds")
        pg.mouse.set_visible(0)

        # Create The Game Backgound
        self.background = pg.Surface((525,700))
        self.background = self.background.convert()
        #background.fill((0,255,0))

        image, rect = load_image("FlappyBirdBackground.png")
        pos = image.get_rect(top = 0 , left = 0)
        image = pg.transform.scale(image, (525,700))
        self.background.blit(image,pos)  

        # Display The Background
        self.screen.blit(self.background, (0, 0))
        pg.display.flip()


        # Prepare Game Objects
        self.clock = pg.time.Clock()
        self.fps = 120 # frames per second

        self.bird = pg.sprite.RenderPlain(Bird(self.fps))

        yPos =  200 + random.randrange(0,300)
        
        self.pipe = pg.sprite.RenderPlain(BottomPipe(yPos), TopPipe(yPos-150))

        self.pause = 0

        # Create Events
        self.newPipe = pg.USEREVENT + 1
        pg.time.set_timer(self.newPipe,1400) # 1000 miliseconds = 1 seconds

        self.going = True
        self.score = 0

    def run(self):

        while(self.going):
            self.clock.tick(self.fps)

            self.__check_collision()

            if self.bird.sprites() == []:
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
                    yPos =  random.randint(np.round(self.screen.get_rect().height/3), np.round(2*self.screen.get_rect().height/3))
                    self.pipe.add(BottomPipe(yPos), TopPipe(yPos-135))
                
            # To be able to move while pressing key continously seperate from new events loop  
            keys = pg.key.get_pressed()
            if keys[pg.K_SPACE]:
                self.bird.sprites()[0].jumping = 1

            # Update Sprites
            self.pipe.update()
            self.bird.update()

            # Draw Everything
            self.screen.blit(self.background, (0, 0)) # always draw background to "erase" previous frame

            self.bird.draw(self.screen)
            self.pipe.draw(self.screen)
            
            self.__draw_score()

            pg.display.flip()


    def __pause(self):
        self.score = 0
        while(self.pause==1): # PAUSING MENU; After the bird being killed
            self.pauseBackground = self.__draw_pause()
                
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
                
            # Draw Everything
            self.screen.blit(self.pauseBackground, (0, 0)) # always draw background to "erase" previous frame
            pg.display.flip()

    @staticmethod 
    def __draw_pause():

        # Create The Game Backgound
        background = pg.Surface((525,700))
        background = background.convert()

        image, rect = load_image("FlappyBirdBackground.png")
        image = pg.transform.scale(image, (525,700))
        pos = image.get_rect(top = 0 , left = 0)
        background.blit(image,pos)  

        # Put Text On The Background, Centered
        if pg.font:
            font = pg.font.Font(None, 36)
            text = font.render("Press c to restart", 1, (10, 10, 10)) #render(text, antialias, color, background=None)
            textpos = text.get_rect(centerx=background.get_width() / 2) # centra ao meio do ecra
            background.blit(text, textpos) # bilt Draws a source Surface onto this Surface.

        return background   

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

        x = self.background.get_rect().centerx
        y = 100

        font = load_font("FlappyBirdy.ttf", 106)
        score = str(self.score)
        text = font.render(score,  1, (255, 255, 255)) #render(text, antialias, color, background=None)
        textpos = text.get_rect(left = x , centery = y) # centra ao meio do ecra
        self.screen.blit(text, textpos) # bilt Draws a source Surface onto this Surface

     



# this calls the 'main' function when this script is executed
if __name__ == "__main__":
    pg.init()
    game = Game()
    game.run()
    pg.quit()