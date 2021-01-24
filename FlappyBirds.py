import os
import pygame as pg
from pygame.compat import geterror
import random

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


class Pipe(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)   
        self.image, self.rect = load_image("pipe.png",-1)
        self.image = pg.transform.scale(self.image, (85,500))
        self.mask = pg.mask.from_surface(self.image)
        self.xvelocity = -1
        self.rect = self.image.get_rect()
        self.area = pg.display.get_surface().get_rect() # get area of the game screen

    def update(self):
        self.rect.move_ip(self.xvelocity,0)
        if self.rect.right < 0:
            self.kill()

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
    def __init__(self):
        pg.sprite.Sprite.__init__(self) # call Sprite initializar
        self.image, self.rect = load_image("FlappyBird.png",-1)
        self.image = pg.transform.scale(self.image, (45,45))
        rotate = pg.transform.rotate
        self.original = rotate(self.image, 45)
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)
        self.area = pg.display.get_surface().get_rect() # get area of the game screen
        self.rect.topleft = (self.area.width/2-150,200) # initial position
        self.samplingTime = 1/120 # update 60 times per second
        self.acceleartion = 480 # pixeis/s^-2
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
            rotate = pg.transform.rotate
            self.image = rotate(self.original, -135*self.yvelocity/self.terminalVelocity)
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
        self.screen = pg.display.set_mode((480,650)) # size of the screen; returns a surface object
        pg.display.set_caption("Flappy Birds")
        pg.mouse.set_visible(0)

        # Create The Game Backgound
        self.background = pg.Surface((480,650))
        self.background = self.background.convert()
        #background.fill((0,255,0))

        image, rect = load_image("FlappyBirdBackground.png")
        pos = image.get_rect(centerx=self.background.get_width() / 2, centery=self.background.get_height()/2)
        self.background.blit(image,pos)  

        # Display The Background
        self.screen.blit(self.background, (0, 0))
        pg.display.flip()


        # Prepare Game Objects
        self.clock = pg.time.Clock()

        self.bird = pg.sprite.RenderPlain(Bird())

        yPos =  200 + random.randrange(0,300)
        
        self.pipe = pg.sprite.RenderPlain(BottomPipe(yPos), TopPipe(yPos-150))

        self.pause = 0

        # Create Events
        self.newPipe = pg.USEREVENT + 1
        pg.time.set_timer(self.newPipe,4800) # 1000 miliseconds = 1 seconds

        self.going = True

    def run(self):

        while(self.going):
            self.clock.tick(120)

            if self.pause == 1:
                self.__pause()

            # Handle Input Events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.going = False
                elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    self.going = False
                elif event.type == self.newPipe:
                    yPos =  200 + random.randrange(0,300)
                    self.pipe.add(BottomPipe(yPos), TopPipe(yPos-135))
                
            # To be able to move while pressing key continously seperate from new events loop  
            keys = pg.key.get_pressed()
            if keys[pg.K_SPACE]:
                self.bird.sprites()[0].jumping = 1

            # Update Sprites
            self.pipe.update()
            self.bird.update()

            self.__check_collision()

            if self.bird.sprites() == []:
                self.pause = 1

            # Draw Everything
            self.screen.blit(self.background, (0, 0)) # always draw background to "erase" previous frame

            self.bird.draw(self.screen)
            self.pipe.draw(self.screen)

            pg.display.flip()


    def __pause(self):
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
                    self.bird.add(Bird())
                    self.pause = 0

                
            # Draw Everything
            self.screen.blit(self.pauseBackground, (0, 0)) # always draw background to "erase" previous frame
            pg.display.flip()

    @staticmethod 
    def __draw_pause():

        # Create The Game Backgound
        background = pg.Surface((480,650))
        background = background.convert()

        image, rect = load_image("FlappyBirdBackground.png")
        pos = image.get_rect(centerx=background.get_width() / 2, centery=background.get_height()/2)
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
     



# this calls the 'main' function when this script is executed
if __name__ == "__main__":
    pg.init()
    game = Game()
    game.run()
    pg.quit()