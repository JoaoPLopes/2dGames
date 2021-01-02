import os
import pygame as pg
from pygame.compat import geterror
import random

if not pg.font:
    print("Warning, fonts disabled")
if not pg.mixer:
    print("Warning, sound disabled")

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


def load_sound(name):
    class NoneSound:
        def play(self):
            pass

    if not pg.mixer or not pg.mixer.get_init():
        return NoneSound()
    fullname = os.path.join(data_dir, name)
    try:
        sound = pg.mixer.Sound(fullname)
    except pg.error:
        print("Cannot load sound: %s" % fullname)
        raise SystemExit(str(geterror()))
    return sound


# classes for our game objects
class Gun(pg.sprite.Sprite):
    """moves a clenched fist on the screen, following the mouse"""

    def __init__(self):
        pg.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.image, self.rect = load_image("shooting.png", -1)
        self.shooting = 0

    def update(self):
        """move the fist based on the mouse position"""
        pos = pg.mouse.get_pos()
        self.rect.midtop = pos
        if self.shooting: # anda para o lado caso esteja a dar um murro
            self.rect.move_ip(5, 10)

    def shoot(self, target):
        """returns true if the fist collides with the target"""
        if not self.shooting:
            self.shooting = 1
            hitbox_width = 10
            hitbox_height = 10
            hitbox_left = self.rect.left + self.rect.width/2 - hitbox_width/2
            hitbox_top = self.rect.top
            hitbox = pg.Rect(hitbox_left, hitbox_top, hitbox_width, hitbox_height )
            #hitbox = self.rect.inflate(-5, -5)
            return hitbox.colliderect(target.rect)

    def unshoot(self):
        """called to pull the fist back"""
        self.shooting = 0


class Alien(pg.sprite.Sprite):
    """moves a monkey critter across the screen. it can spin the
       monkey when it is punched."""

    def __init__(self):
        pg.sprite.Sprite.__init__(self)  # call Sprite intializer
        self.image, self.rect = load_image("alien1.png", -1)
        screen = pg.display.get_surface()
        self.area = screen.get_rect()
        self.rect.topleft = 10, 10 # initial position
        self.x_move = 0
        self.y_move = 0
        self.x_acc = 5
        self.y_acc = 5
        self.dizzy = 0
        self.direction = 0
        self.new_direction = 0
        self.max_velocity = 5

    def update(self):
        """walk or spin, depending on the alien state"""
        if self.dizzy:
            self._spin()
        else:
            self._walk()

    def _changeDirection(self):
        """spin the alien image"""
        self.new_direction = self.new_direction + 1
        if self.new_direction >= 5:
            self.new_direction = 0
            self.direction = random.randrange(3)

    def _acceleration(self): # applies acceleartion defines new velocity
        if abs(self.x_move) < self.max_velocity and self.direction == 0 :
            self.x_move = self.x_move + 0.1*self.x_acc #0.1 is smapling interval
        elif abs(self.y_move) < self.max_velocity and self.direction == 1:
            self.y_move = self.y_move + 0.1*self.y_acc #0.1 is smapling interval
        elif abs(self.x_move) < self.max_velocity and abs(self.y_move) < self.max_velocity and self.direction == 2:
            self.y_move = self.y_move + 0.1*self.y_acc #0.1 is smapling interval
            self.x_move = self.x_move + 0.1*self.x_acc #0.1 is smapling interval


    def _walk(self):
        """move the alien across the screen, and turn at the ends"""
        self._changeDirection() # change direction if it is the case
        self._acceleration() # computes new velocity given the acceleration
        self.rect = self.rect.move((self.x_move, self.y_move))

        if self.rect.left <= self.area.left or self.rect.right >= self.area.right:
            self.x_acc = -self.x_acc
            self.x_move = -self.x_move
            self.rect = self.rect.move((self.x_move, 0))
            self.x_move = 0
            self.image = pg.transform.flip(self.image, 1, 0)
            self.new_direction = 0

        if self.rect.top <= self.area.top or self.rect.bottom  >= self.area.bottom:
            self.y_acc = -self.y_acc
            self.y_move = -self.y_move
            self.rect = self.rect.move((0,self.y_move))
            self.y_move = 0
            #self.image = pg.transform.flip(self.image, 0, 0)
            self.new_direction = 0



    def _spin(self):
        """spin the alien image"""
        center = self.rect.center
        self.dizzy = self.dizzy + 12
        if self.dizzy >= 360:
            self.dizzy = 0
            self.image = self.original
        else:
            rotate = pg.transform.rotate
            self.image = rotate(self.original, self.dizzy)
        self.rect = self.image.get_rect(center=center)

    def punched(self):
        """this will cause the alien to start spinning"""
        if not self.dizzy:
            self.dizzy = 1
            self.original = self.image


def main():
    """this function is called when the program starts.
       it initializes everything it needs, then runs in
       a loop until the function returns."""
    # Initialize Everything
    pg.init()
    screen = pg.display.set_mode((468,468)) # size of the screen; returns a surface object
    pg.display.set_caption("Save The Planet")
    pg.mouse.set_visible(0)

    # Create The Initial Backgound
    initialbackground = pg.Surface(screen.get_size())
    initialbackground = initialbackground.convert()
    initialbackground.fill((250, 250, 250)) #set color (rgb)

    # Press Space bar to start the game
    if pg.font:
        fontSize = 36
        font = pg.font.Font(None, fontSize)
        text = font.render("Press The Space Bar To", 1, (10, 10, 10)) #render(text, antialias, color, background=None)
        textpos = text.get_rect(centerx=initialbackground.get_width() / 2) # centra ao meio do ecra
        initialbackground.blit(text, textpos) # bilt Draws a source Surface onto this Surface.
        text = font.render("Start The Game", 1, (10, 10, 10)) #render(text, antialias, color, background=None)
        textpos = text.get_rect(centerx=initialbackground.get_width() / 2, centery=fontSize) # centra ao meio do ecra
        initialbackground.blit(text, textpos) # bilt Draws a source Surface onto this Surface.

    # Display The Initial Background
    screen.blit(initialbackground, (0, 0))
    pg.display.flip()

    # Game Starts With SpaceBar Being Pressed
    ready = False
    while not ready:
        for event in pg.event.get():
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                ready = True

    # Create The Game Backgound
    background = pg.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250)) #set color (rgb)

    # Add the planet to the background
    planet_image, planet_rect = load_image("planet.png", -1)
    planetpos = planet_image.get_rect(centerx=background.get_width() / 2, centery=background.get_height() + background.get_height()/8)
    background.blit(planet_image,planetpos)


    # Load missed gunshot image
    gunshot_image, gunshot_rect = load_image("gunshot.png", -1)
    

    # Put Text On The Background, Centered
    if pg.font:
        font = pg.font.Font(None, 36)
        text = font.render("Shoot The Alien To Save The Planet", 1, (10, 10, 10)) #render(text, antialias, color, background=None)
        textpos = text.get_rect(centerx=background.get_width() / 2) # centra ao meio do ecra
        background.blit(text, textpos) # bilt Draws a source Surface onto this Surface.

    # Display The Background
    screen.blit(background, (0, 0))
    pg.display.flip()

    # Prepare Game Objects
    clock = pg.time.Clock()
    whiff_sound = load_sound("missed.mp3")
    punch_sound = load_sound("gunshot.wav")
    alien = Alien()
    gun = Gun()
    allsprites = pg.sprite.RenderPlain((alien,gun))

    miss = 0

    # Main Loop
    going = True
    while going:
        clock.tick(60)

        # Handle Input Events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                going = False
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                going = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                if gun.shoot(alien):
                    punch_sound.play()  # punch
                    alien.punched()
                    miss = 0
                else:
                    whiff_sound.play()  # miss
                    miss = 1
                    pos = pg.mouse.get_pos()
            elif event.type == pg.MOUSEBUTTONUP:
                gun.unshoot()

        allsprites.update()

        # Draw Everything
        screen.blit(background, (0, 0)) # background é o espaço branco com o texto. Se não fizer não "apaga" os chim e fist anteriores
        # allsprites.clear(screen,background) # equivalent to the previous line "Erases the Sprites used in the last Group.draw() call. The destination Surface is cleared by filling the drawn Sprite positions with the background."

        if miss == 1:
            gunshotpos = gunshot_image.get_rect(centerx=pos[0], centery=pos[1] )
            screen.blit(gunshot_image,gunshotpos)

        allsprites.draw(screen) # desenha todos os Sprits (chimp and fist)
        pg.display.flip()

    pg.quit()


# Game Over


# this calls the 'main' function when this script is executed
if __name__ == "__main__":
    main()