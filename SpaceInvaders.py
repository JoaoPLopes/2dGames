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

def load_font(name, size):
    fullname = os.path.join(data_dir, name)
    try:
        font = pg.font.Font(fullname, size)
    except:
        font = pg.font.Font(None, size)
    return font

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
        self.lives = 3
        self.pontuation = 0

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
        self.area.width = self.area.height - 100
        self.area.topleft = (0,100)
        self.rect.bottom  = ypos
        self.rect.centerx = xpos
    
    def update(self):
        self.rect.move_ip(0,self.yvelocity)
        if not self.area.contains(self.rect):
            self.kill() # Kill removes sprit from all groups

class Monster(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self) # call Sprite initializar
        self.image, self.rect = load_image("monster.png", -1)
        self.image = pg.transform.scale(self.image, (50,50))
        self.rect = self.image.get_rect()
        self.yvelocity = 1 # velocity of the moster
        self.xvelocity = 0
        self.area = pg.display.get_surface().get_rect() # get area of the game screen
        self.area.height = self.area.height - 100
        self.area.topleft = (0,100)
        self.rect.topleft = random.randrange(0,self.area.right-50), 100 # Initial position ; x coordinate is random, y is 0
        self.hit = 0
    
    def update(self):
        self.rect.move_ip(0,self.yvelocity)


def draw_pontuation(surf, count, lives, x , y):
    
    font = pg.font.Font(None, 24)
    message = "Score < " + str(count) + " >"
    text = font.render(message, 1, (255, 255, 255), (0, 0, 255)) #render(text, antialias, color, background=None)
    textpos = text.get_rect(left = x , centery = y) # centra ao meio do ecra
    surf.blit(text, textpos) # bilt Draws a source Surface onto this Surface

    message = "Lives < " + str(lives) + " >"
    text = font.render(message, 1, (255, 255, 255), (0, 0, 255)) #render(text, antialias, color, background=None)
    textpos = text.get_rect(right = 468-90 , centery = y) # centra ao meio do ecra
    surf.blit(text, textpos) # bilt Draws a source Surface onto this Surface

def check_collision(invaders, ship, allshots):

    for monster in invaders: # check colision between shot an monster
        if not monster.area.contains(monster.rect): # if reaches final of the screen dies
            monster.kill() # Kill removes sprit from all groups
            ship.sprites()[0].lives -= 1
        if [] != pg.sprite.spritecollide(monster, allshots, True):
            monster.kill()
            ship.sprites()[0].pontuation += 1
        
    if [] != pg.sprite.spritecollide(ship.sprites()[0], invaders, True):
        ship.sprites()[0].lives -= 1



def main():
    """this function is called when the program starts.
       it initializes everything it needs, then runs in
       a loop until the function returns."""
    # Initialize Everything
    pg.init()
    screen = pg.display.set_mode((468,568)) # size of the screen; returns a surface object
    pg.display.set_caption("Space Invaders")
    pg.mouse.set_visible(0)

    # Create The Game Backgound
    background = pg.Surface((468,568))
    background = background.convert()
    background.fill((0, 0, 0)) #set color (rgb)
    
    # Display The Background
    screen.blit(background, (0, 0))
    pg.display.flip()

    # Put Text On The Background
    if pg.font:
        font = load_font("BigSpace.ttf", 36)
        text = font.render("Space Invaders", 1, (250, 255, 255), (0, 0, 0)) #render(text, antialias, color, background=None)
        textpos = text.get_rect(centerx=background.get_width() / 2, y=0) # centra ao meio do ecra
        background.blit(text, textpos) # bilt Draws a source Surface onto this Surface.

    pg.draw.rect(background, (0, 0, 255), pg.Rect(80, 40, background.get_width()-80*2, 40))

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

        check_collision(invaders, ship, allshots)

        if ship.sprites()[0].lives < 1: # End game
            going = 0

        draw_pontuation(background, ship.sprites()[0].pontuation, ship.sprites()[0].lives, 90, 60)

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