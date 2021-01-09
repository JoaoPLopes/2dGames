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

class Ship(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.image, self.rect = load_image("spaceShip.png",-1)
        self.image = pg.transform.scale(self.image, (50,50)) # re-shape image 
        self.rect = self.image.get_rect() # get new rect
        self.xvelocity = 5 # velocity of the space ship
        self.direction = 0 # 1 - to move to the right; -1 - to move to the left; 0 - to stay in the same place
        self.area = pg.display.get_surface().get_rect() # get area of the game screen
        # initial position
        self.rect.bottom  = self.area.bottom
        self.rect.centerx = self.area.centerx

    def update(self):
        self.rect.move_ip(self.direction*self.xvelocity,0)
        if not self.area.contains(self.rect): # if the new position of the rect is not inside the screen area
            self.rect.move_ip(-self.direction*self.xvelocity,0)
        self.direction = 0

class Shot(pg.sprite.Sprite):
    def __init__(self, xpos, ypos):
        pg.sprite.Sprite.__init__(self) # call Sprite initializar
        self.image, self.rect = load_image("shot.png",-1)
        self.image = pg.transform.scale(self.image, (20,20))
        self.rect = self.image.get_rect()
        self.yvelocity = -5 # velocity of the shot
        self.xvelocity = 0 # 
        self.area = pg.display.get_surface().get_rect() # get area of the game screen
        self.rect.bottom  = ypos
        self.rect.centerx = xpos
    
    def update(self):
        self.rect.move_ip(0,self.yvelocity)
        if not self.area.contains(self.rect):
            self.kill() # Kill removes sprit from all groups

class Monster(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self) # call Sprite initializar
        self.image, self.rect = load_image("monster.jpg", -1)
        self.image = pg.transform.scale(self.image, (50,50))
        self.rect = self.image.get_rect()
        self.yvelocity = 1 # velocity of the moster
        self.xvelocity = 0
        self.area = pg.display.get_surface().get_rect() # get area of the game screen
        self.rect.topleft = random.randrange(0,self.area.right-50), 0 # Initial position ; x coordinate is random, y is 0
        self.hit = 0
    
    def update(self):
        self.rect.move_ip(0,self.yvelocity)
        if not self.area.contains(self.rect): # if reaches final of the screen dies
            self.kill() # Kill removes sprit from all groups
        if self.hit:
            self.kill() # removes monster


def main():
    """this function is called when the program starts.
       it initializes everything it needs, then runs in
       a loop until the function returns."""
    # Initialize Everything
    pg.init()
    screen = pg.display.set_mode((468,468)) # size of the screen; returns a surface object
    pg.display.set_caption("Space Invaders")
    pg.mouse.set_visible(0)

    # Create The Game Backgound
    background = pg.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250)) #set color (rgb)

    # Display The Background
    screen.blit(background, (0, 0))
    pg.display.flip()

    # Prepare Game Objects
    clock = pg.time.Clock()

    ship = pg.sprite.RenderPlain((Ship()))

    invaders = pg.sprite.RenderPlain((Monster()))

    allshots = pg.sprite.RenderPlain() # container that will store shots form ship

    # Create Events
    newInvader = pg.USEREVENT + 1
    pg.time.set_timer(newInvader,3000) # 1000 miliseconds = 1 seconds

    # Main loop
    going = True
    
    while(going):
        clock.tick(60)

        for monster in invaders:
            blocks_hit_list = pg.sprite.spritecollide(monster, allshots, True)
            if blocks_hit_list != []:
                monster.hit = 1

        # Handle Input Events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                going = False
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                going = False
            elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                allshots.add(Shot(xpos = ship.sprites()[0].rect.centerx, ypos = ship.sprites()[0].rect.top))
            elif event.type == newInvader:
                invaders.add(Monster())

        # To be able to move while pressing key continously seperate from new events loop  
        keys = pg.key.get_pressed()
        if keys[pg.K_RIGHT]:
            ship.sprites()[0].direction = 1
        elif keys[pg.K_LEFT]:
            ship.sprites()[0].direction = -1
     
        allshots.update()
        invaders.update()
        ship.update()

        # Draw Everything
        screen.blit(background, (0, 0))

        ship.draw(screen)
        allshots.draw(screen)
        invaders.draw(screen)

        pg.display.flip()

    pg.quit()

# this calls the 'main' function when this script is executed
if __name__ == "__main__":
    main()