"""
Subcontroller module for Alien Invaders

This module contains the subcontroller to manage a single level or wave in the Alien
Invaders game.  Instances of Wave represent a single wave.  Whenever you move to a
new level, you are expected to make a new instance of the class.

The subcontroller Wave manages the ship, the aliens and any laser bolts on screen.  
These are model objects.  Their classes are defined in models.py.

Most of your work on this assignment will be in either this module or models.py.
Whether a helper method belongs in this module or models.py is often a complicated
issue.  If you do not know, ask on Piazza and we will answer.

# YOUR NAME(S) AND NETID(S) HERE
# DATE COMPLETED HERE
"""
from game2d import *
from consts import *
from models import *
import random

# PRIMARY RULE: Wave can only access attributes in models.py via getters/setters
# Wave is NOT allowed to access anything in app.py (Subcontrollers are not permitted 
# to access anything in their parent. To see why, take CS 3152)


class Wave(object):
    """
    This class controls a single level or wave of Alien Invaders.
    
    This subcontroller has a reference to the ship, aliens, and any laser bolts on screen. 
    It animates the laser bolts, removing any aliens as necessary. It also marches the
    aliens back and forth across the screen until they are all destroyed or they reach
    the defense line (at which point the player loses). When the wave is complete, you 
    should create a NEW instance of Wave (in Invaders) if you want to make a new wave of 
    aliens.
    
    If you want to pause the game, tell this controller to draw, but do not update.  See 
    subcontrollers.py from Lecture 24 for an example.  This class will be similar to
    that one in how it interacts with the main class Invaders.
    
    #UPDATE ME LATER
    INSTANCE ATTRIBUTES:
        _ship:   the player ship to control [Ship]
        _aliens: the 2d list of aliens in the wave [rectangular 2d list of Alien or None] 
        _bolts:  the laser bolts currently on screen [list of Bolt, possibly empty]
        _dline:  the defensive line being protected [GPath]
        _lives:  the number of lives left  [int >= 0]
        _time:   The amount of time since the last Alien "step" [number >= 0]
    
    As you can see, all of these attributes are hidden.  You may find that you want to
    access an attribute in class Invaders. It is okay if you do, but you MAY NOT ACCESS 
    THE ATTRIBUTES DIRECTLY. You must use a getter and/or setter for any attribute that 
    you need to access in Invaders.  Only add the getters and setters that you need for 
    Invaders. You can keep everything else hidden.
    
    You may change any of the attributes above as you see fit. For example, may want to 
    keep track of the score.  You also might want some label objects to display the score
    and number of lives. If you make changes, please list the changes with the invariants.
    
    LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY
        _direction:     whether the invading aliens are moving right or left [string 'right' or 'left']
        _firerate:      how often a bolt will be produced by the aliens
        _steps:         how many times the aliens have moved since the last bolt [int>=0]
        _score:         keeps track of the score in the upper left corner [GLabel object]
        _lifecounter:   keeps track of lives in the upper right corner [GLabel object]
    """
    
    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)
    def getShip(self):
        """Returns: ship if ship object and None if Nonetype"""
        return self._ship
    
    def getLives(self):
        """Returns: the number of lives the player has remaining"""
        return self._lives
    
    def getAliens(self):
        """Returns: 'empty' if all items in self._alien are None and 'active' if
        there are still aliens in the list"""
        a = 'empty'
        for row in self._aliens:
            for item in row:
                if item != None:
                    a = 'active'
        return a
        
    
    # INITIALIZER (standard form) TO CREATE SHIP AND ALIENS
    def __init__(self,theme):
        """spec here"""
        self._aliens = self._create_wave(theme)
        self._ship = Ship(theme)
        self._dline = GPath(points=[0,DEFENSE_LINE,GAME_WIDTH,DEFENSE_LINE],linecolor='white')
        self._lives = SHIP_LIVES
        self._time = 0
        self._direction = 'right'
        self._bolts = []
        self._firerate = random.randrange(1,BOLT_RATE)
        self._steps = 0
        self._scorenum = 0
        self._score = GLabel(text='Score: '+str(self._scorenum),left=10,top=GAME_HEIGHT-10, font_name = 'RetroGame.ttf', font_size = 20,linecolor='white')
        self._lifecount = GLabel(text='Lives: '+str(self._lives),left=GAME_WIDTH-130,top=GAME_HEIGHT-10, font_name = 'RetroGame.ttf', font_size = 20,linecolor='white')
    
    
    # UPDATE METHOD TO MOVE THE SHIP, ALIENS, AND LASER BOLTS
    def update(self, press, dt, theme):
        """spec here"""
        self._time += .017
        if self._time >= ALIEN_SPEED:
            self._invade()
            self._time = 0
            self._steps += 1 
        self._fire(press,theme)
        self._move_bolts()
        self._remove_bolts()
        if self._steps == self._firerate:
            self._alien_fire()
        if self._ship != None and self._ship.collides(self._bolts):
            self._ship = None
            self._lives = self._lives - 1
            self._lifecount = GLabel(text='Lives: '+str(self._lives),left=GAME_WIDTH-130,top=GAME_HEIGHT-10, font_name = 'RetroGame.ttf', font_size = 20,linecolor='white')
        for row in self._aliens:
            for item in row:
                if item != None and item.collides(self._bolts):
                    a = self._aliens.index(row)
                    b = row.index(item)
                    self._aliens[a][b] = None
                    self._scorenum += 10
                    self._score = GLabel(text='Score: '+str(self._scorenum),left=10,top=GAME_HEIGHT-10, font_name = 'RetroGame.ttf', font_size = 20,linecolor='white')
        if self.belowDefenseLine():
            self._ship = None
            self._lives = 0 

    
    # DRAW METHOD TO DRAW THE SHIP, ALIENS, DEFENSIVE LINE AND BOLTS
    def draw(self,view):
        """Spec here"""
        for row in self._aliens:
            for alien in row:
                if alien != None:
                    alien.draw(view)
        if self._ship != None:
            self._ship.draw(view)
        self._dline.draw(view)
        for item in self._bolts:
            item.draw(view)
        self._score.draw(view)
        self._lifecount.draw(view)
        
    
    # HELPER METHODS FOR COLLISION DETECTION
    def _create_wave(self,theme):
        """spec here"""
        newlist = []
        prevtype = ''
        alientype = 'a'
        xpos = ALIEN_H_SEP + ALIEN_WIDTH/2
        ypos = GAME_HEIGHT -ALIEN_ROWS*ALIEN_V_SEP - (ALIEN_ROWS-0.5)*ALIEN_HEIGHT - TOP_TEXT_HEIGHT
        for row in range(ALIEN_ROWS):
            alist = []
            for item in range(ALIENS_IN_ROW):
                alist.append(Alien(alientype,xpos,ypos,theme))
                xpos = xpos + ALIEN_H_SEP + ALIEN_WIDTH
            xpos = ALIEN_H_SEP + ALIEN_WIDTH/2
            prevtype = prevtype + alientype
            newlist.append(alist)    
            ypos = ypos + ALIEN_V_SEP + ALIEN_HEIGHT
            if prevtype == 'aa':
                alientype = 'b'
                prevtype = ''
            if prevtype == 'bb':
                alientype = 'c'
                prevtype = ''
            if prevtype == 'cc':
                alientype = 'a'
                prevtype = ''
        return newlist
    
    def _move_ship(self,press):
        """spec"""
        if press.is_key_down('left') and self._ship != None:
            self._ship.x = max(SHIP_WIDTH/2,self._ship.x - SHIP_MOVEMENT)
        if press.is_key_down('right') and self._ship != None:
            self._ship.x = min(GAME_WIDTH-SHIP_WIDTH/2,self._ship.x + SHIP_MOVEMENT)
    
    def _invade(self):
        """spec"""
        right = 0
        left = GAME_WIDTH
        for row in self._aliens:
            for alien in row:
                if alien != None and alien.right > right:
                    right = alien.right
                if alien != None and alien.left < left:
                    left = alien.left
        if GAME_WIDTH-right < ALIEN_H_SEP:
            self._direction = 'left'
            for row in self._aliens:
                for alien in row:
                    if alien != None:
                        alien.y = alien.y - ALIEN_V_SEP
        if left < ALIEN_H_SEP:
            self._direction = 'right'
            for row in self._aliens:
                for alien in row:
                    if alien != None:
                        alien.y = alien.y - ALIEN_V_SEP
        if self._direction == 'right':
            for row in self._aliens:
                for alien in row:
                    if alien != None:
                        alien.x = alien.x + ALIEN_H_WALK
        if self._direction == 'left':
            for row in self._aliens:
                for alien in row:
                    if alien != None:
                        alien.x = alien.x - ALIEN_H_WALK
                    
    def _fire(self,press,theme):
        """spec"""
        noplayerbolt = True
        for item in self._bolts:
            if item._isPlayerBolt:
                noplayerbolt = False
        pressed = (press.is_key_down('up') or press.is_key_down('spacebar'))
        if pressed and noplayerbolt and self._ship != None:
            self._bolts.append (Bolt(self._ship.x,SHIP_BOTTOM+SHIP_HEIGHT,True))
            if theme ==6:
                self._song = Sound('Ding.wav')
                self._song.volume = 0.5
            else:
                self._song = Sound('pew2.wav')
            self._song.play()

        
    def _move_bolts(self):
        """spec"""
        for item in self._bolts:
            item.y = item.y + item._velocity
    
    def _remove_bolts(self):
        """spec"""
        for item in self._bolts:
            if item.bottom >= GAME_HEIGHT or item.top <= 0:
                self._bolts.remove(item)
    
    def _alien_fire(self):
        """spec"""
        columns = []
        for col in range(ALIENS_IN_ROW):
            column = []
            for row in self._aliens:
                if row != None:
                    column.append(row)
            if column != []:
                columns.append(col)
        print(columns)
        chosen = random.choice(columns)
        fired = False
        for row in self._aliens:
            if row[chosen] != None and fired == False:
                angry_alien = row[chosen]
                self._bolts.append(Bolt(angry_alien.x,angry_alien.bottom,False))
                fired = True
                self._steps = 0
                self._firerate = random.randrange(1,BOLT_RATE)
    
    def restoreShip(self,theme):
        """spec"""
        self._ship = Ship(theme)
        
    def belowDefenseLine(self):
        for row in self._aliens:
            for item in row:
                if item != None and item.bottom <= DEFENSE_LINE:
                    return True
        return False
                    
            