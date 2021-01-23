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
        self.image = pg.transform.scale(self.image, (80,600))
        self.xvelocity = -1
        self.rect = self.image.get_rect()
        self.area = pg.display.get_surface().get_rect() # get area of the game screen
        self.rect.topleft = (self.area.width, 200 + random.randrange(0,300)) # initial position

    def update(self):
        self.rect.move_ip(self.xvelocity,0)
        if self.rect.right < 0:
            self.kill()

class Bird(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self) # call Sprite initializar
        self.image, self.rect = load_image("FlappyBird.png",-1)
        self.image = pg.transform.scale(self.image, (50,50))
        rotate = pg.transform.rotate
        self.original = rotate(self.image, 45)
        self.rect = self.image.get_rect()
        self.area = pg.display.get_surface().get_rect() # get area of the game screen
        self.rect.topleft = (self.area.width/2-150,200) # initial position
        self.samplingTime = 1/60 # update 60 times per second
        self.acceleartion = 600 # pixeis/s^-2
        self.terminalVelocity = 400 # pixeis por segundo
        self.yvelocity = 0 # velocity of the bird
        self.jumping = 0
        self.jump = -10 # pixeis

    
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
        self.rect.move_ip(0,self.samplingTime*self.yvelocity) # move x pixeis
        if self.rect.bottom > self.area.bottom:
            self.kill() # Kill removes sprit from all groups

    def _jump(self):
        self.image = self.original
        self.yvelocity = 0
        self.jumping = 0
        #rotate = pg.transform.rotate
        #self.image = rotate(self.image, 0)
        self.rect.move_ip(0,self.jump) # move x pixeis


def draw_pause():

    # Create The Game Backgound
    background = pg.Surface((480,600))
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
        
def check_collision(pipes, bird):

    for pipe in pipes: # check colision between bird and all pipes
        if [] != pg.sprite.spritecollide(pipe, bird, True):
            pipe.kill() 

def main(): 
    """this function is called when the program starts.
       it initializes everything it needs, then runs in
       a loop until the function returns."""

    # Initialize Everything
    pg.init()
    screen = pg.display.set_mode((480,600)) # size of the screen; returns a surface object
    pg.display.set_caption("Flappy Birds")
    pg.mouse.set_visible(0)

    # Create The Game Backgound
    background = pg.Surface((480,600))
    background = background.convert()
    #background.fill((0,255,0))

    image, rect = load_image("FlappyBirdBackground.png")
    pos = image.get_rect(centerx=background.get_width() / 2, centery=background.get_height()/2)
    background.blit(image,pos)  

    # Display The Background
    screen.blit(background, (0, 0))
    pg.display.flip()


    # Prepare Game Objects
    clock = pg.time.Clock()

    bird = pg.sprite.RenderPlain(Bird())

    pipe = pg.sprite.RenderPlain(Pipe())

    pause = 0


    # Create Events
    newPipe = pg.USEREVENT + 1
    pg.time.set_timer(newPipe,4800) # 1000 miliseconds = 1 seconds

    going = True
    while(going):
        clock.tick(60)

        while(pause==1): # PAUSING MENU; After the bird being killed
            pauseBackground = draw_pause()
            
            for sprite in pipe.sprites():
                sprite.kill()
            
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pause = 0
                    going = False
                elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    pause = 0
                    going = False
                elif event.type == pg.KEYDOWN and event.key == pg.K_c: # press "c" to continue
                    bird.add(Bird())
                    pause = 0

            
            # Draw Everything
            screen.blit(pauseBackground, (0, 0)) # always draw background to "erase" previous frame
            pg.display.flip()

        # Handle Input Events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                going = False
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                going = False
            elif event.type == newPipe:
                pipe.add(Pipe())
            
        # To be able to move while pressing key continously seperate from new events loop  
        keys = pg.key.get_pressed()
        if keys[pg.K_SPACE]:
            bird.sprites()[0].jumping = 1

        # Update Sprites
        pipe.update()
        bird.update()

        check_collision(pipe,bird)

        if bird.sprites() == []:
            pause = 1

        # Draw Everything
        screen.blit(background, (0, 0)) # always draw background to "erase" previous frame

        pg.draw.rect(screen, (0,0,0), pipe.sprites()[0].rect)
        pg.draw.rect(screen, (0,0,0), bird.sprites()[0].rect)
        bird.draw(screen)
        pipe.draw(screen)

        pg.display.flip()
    
    pg.quit()



# this calls the 'main' function when this script is executed
if __name__ == "__main__":
    main()