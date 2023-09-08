"""
Primary module for Alien Invaders

This module contains the main controller class for the Alien Invaders application. There 
is no need for any additional classes in this module.  If you need more classes, 99% of 
the time they belong in either the wave module or the models module. If you are unsure 
about where a new class should go, post a question on Piazza.

# YOUR NAME(S) AND NETID(S) HERE
# DATE COMPLETED HERE
"""
import cornell
from consts import *
from game2d import *
from wave import *


# PRIMARY RULE: Invaders can only access attributes in wave.py via getters/setters
# Invaders is NOT allowed to access anything in models.py

class Invaders(GameApp):
    """
    The primary controller class for the Alien Invaders application
    
    This class extends GameApp and implements the various methods necessary for processing 
    the player inputs and starting/running a game.
    
        Method start begins the application.
        
        Method update either changes the state or updates the Play object
        
        Method draw displays the Play object and any other elements on screen
    
    Because of some of the weird ways that Kivy works, you SHOULD NOT create an
    initializer __init__ for this class.  Any initialization should be done in
    the start method instead.  This is only for this class.  All other classes
    behave normally.
    
    Most of the work handling the game is actually provided in the class Wave.
    Wave should be modeled after subcontrollers.py from lecture, and will have
    its own update and draw method.
    
    The primary purpose of this class is to manage the game state: which is when the 
    game started, paused, completed, etc. It keeps track of that in an attribute
    called _state.
    
    INSTANCE ATTRIBUTES:
        view:   the game view, used in drawing (see examples from class)
                [instance of GView; it is inherited from GameApp]
        input:  the user input, used to control the ship and change state
                [instance of GInput; it is inherited from GameApp]
        _state: the current state of the game represented as a value from consts.py
                [one of STATE_INACTIVE, STATE_NEWWAVE, STATE_ACTIVE, STATE_PAUSED, STATE_CONTINUE, STATE_COMPLETE]
        _wave:  the subcontroller for a single wave, which manages the ships and aliens
                [Wave, or None if there is no wave currently active]
        _text:  the currently active message
                [GLabel, or None if there is no message to display]
    
    STATE SPECIFIC INVARIANTS: 
        Attribute _wave is only None if _state is STATE_INACTIVE.
        Attribute _text is only None if _state is STATE_ACTIVE.
    
    For a complete description of how the states work, see the specification for the
    method update.
    
    You may have more attributes if you wish (you might want an attribute to store
    any score across multiple waves). If you add new attributes, they need to be 
    documented here.
    
    LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY
        _lastinput: user input from previous frame
                    [instance of GInput; it is inherited from Gameup]
        _Welcome: welcome message
                    [instance of GLabel, at min a string with position]
        _Pause: pause message
                    [instance of GLabel, at min a string with position]
        _Congrats: message when player wins
                    [instance of GLabel, at min a string with position]
        _YouLose: message when player loses
                    [instance of GLabel, at min a string with position]
        _gameOver: message when the game has been completed
                    [instance of GLabel, at min a string with position]
        _stateTime: the number of frames that have passed in the current state
                    [int >= 0]
        _song:      the song played throughout the game, looped
                    [a Sound object]
        _menubuttons: buttons for the options screen
                    [a string of GLabel objects]
        _title:     game title
                    [a GImage object]
        _theme:     zero if default theme, theme number if theme chosen
                    [6>= int >= 0 ]
        _background: the image behind the text and all other in view objects
                    [GImage object]
    """
    
    # DO NOT MAKE A NEW INITIALIZER!
    
    # THREE MAIN GAMEAPP METHODS
    def start(self):
        """
        Initializes the application.
        
        This method is distinct from the built-in initializer __init__ (which you 
        should not override or change). This method is called once the game is running. 
        You should use it to initialize any game specific attributes.
        
        This method should make sure that all of the attributes satisfy the given 
        invariants. When done, it sets the _state to STATE_INACTIVE and create a message 
        (in attribute _text) saying that the user should press to play a game.
        """
        self._state = STATE_INACTIVE
        self._background = GImage(x=GAME_WIDTH//2,y=GAME_HEIGHT//2,source='background.gif',width=GAME_WIDTH,height=GAME_HEIGHT)
        self._wave = None
        self._title = GImage(x=GAME_WIDTH//2,y=GAME_HEIGHT//2,source='Title.png', height=300,width=700)
        self._Welcome = GLabel(text = "Press 's' to Play or 'o' for Options", x = GAME_WIDTH//2, y = GAME_HEIGHT//2-120, font_name = 'RetroGame.ttf', font_size = 20,linecolor='white') 
        self._Pause = GLabel(text = 'Press Space to Resume', x = GAME_WIDTH//2, y = GAME_HEIGHT//2, font_name = 'RetroGame.ttf', font_size = 25,linecolor='white')
        self._Congrats = GLabel(text = 'Nice job, you beat the aliens!', x = GAME_WIDTH//2, y = GAME_HEIGHT//2,font_name = 'RetroGame.ttf', font_size = 30,linecolor='white')
        self._YouLose = GLabel(text = "You've been invaded!", x = GAME_WIDTH//2, y = GAME_HEIGHT//2, font_name = 'RetroGame.ttf', font_size = 30,linecolor='white')
        self._gameOver = GLabel(text = "Game Over! Press r to Play Again", x = GAME_WIDTH//2, y = GAME_HEIGHT//2, font_name = 'RetroGame.ttf', font_size = 30,linecolor='white')
        self._text = self._Welcome
        self._lastinput = False
        self._stateTime = 0 
        self._song = Sound('8-bit-Arcade4.wav')
        self._song.play(loop=True)
        self._menubuttons = self._createmenu()
        self._theme = 0
            
    
    def update(self,dt):
        """
        Animates a single frame in the game.
        
        It is the method that does most of the work. It is NOT in charge of playing the
        game.  That is the purpose of the class Wave. The primary purpose of this
        game is to determine the current state, and -- if the game is active -- pass
        the input to the Wave object _wave to play the game.
        
        As part of the assignment, you are allowed to add your own states. However, at
        a minimum you must support the following states: STATE_INACTIVE, STATE_NEWWAVE,
        STATE_ACTIVE, STATE_PAUSED, STATE_CONTINUE, and STATE_COMPLETE.  Each one of these 
        does its own thing and might even needs its own helper.  We describe these below.
        
        STATE_INACTIVE: This is the state when the application first opens.  It is a 
        paused state, waiting for the player to start the game.  It displays a simple
        message on the screen. The application remains in this state so long as the 
        player never presses a key.  In addition, this is the state the application
        returns to when the game is over (all lives are lost or all aliens are dead).
        
        STATE_NEWWAVE: This is the state creates a new wave and shows it on the screen. 
        The application switches to this state if the state was STATE_INACTIVE in the 
        previous frame, and the player pressed a key. This state only lasts one animation 
        frame before switching to STATE_ACTIVE.
        
        STATE_ACTIVE: This is a session of normal gameplay.  The player can move the
        ship and fire laser bolts.  All of this should be handled inside of class Wave
        (NOT in this class).  Hence the Wave class should have an update() method, just
        like the subcontroller example in lecture.
        
        STATE_PAUSED: Like STATE_INACTIVE, this is a paused state. However, the game is
        still visible on the screen.
        
        STATE_CONTINUE: This state restores the ship after it was destroyed. The 
        application switches to this state if the state was STATE_PAUSED in the 
        previous frame, and the player pressed a key. This state only lasts one animation 
        frame before switching to STATE_ACTIVE.
        
        STATE_COMPLETE: The wave is over, and is either won or lost.
        
        You are allowed to add more states if you wish. Should you do so, you should 
        describe them here.
        
        STATE_MENU: Before the game start or during the game when the player can
        customize certain features of game play. 
        
        Parameter dt: The time in seconds since last update
        Precondition: dt is a number (int or float)
        """
        self._state == self._newstate()
        if self._state == STATE_INACTIVE:
            self._text = self._Welcome
        if self._state == STATE_MENU:
            self._text = GLabel(text='Options',left = 10, top = GAME_HEIGHT - 10,font_name='RetroGame.ttf',font_size=35)
            self._lastinput = False
        if self._state == STATE_NEWWAVE:
            self._text = None
            self._wave = Wave(self._theme)
            self._state = self._state + 1 
        if self._state == STATE_ACTIVE:
            self._lastinput = False
            self._text = None
            if self._wave.getShip() == None:
                if self._wave.getLives() > 0:
                    self._state = STATE_PAUSED
                if self._wave.getLives() == 0:
                    self._state = STATE_COMPLETE
            if self._wave.getAliens() == 'empty':
                self._state = STATE_COMPLETE
            self._wave.update(self.input, dt, self._theme)
        if self._state == STATE_PAUSED:
            self._lastinput = False
            self._text = self._Pause
        if self._state == STATE_CONTINUE:
            self._wave.restoreShip(self._theme)
            self._text = None
            self._state = STATE_ACTIVE
        if self._state == STATE_COMPLETE:
            self._stateTime = self._stateTime + 1 
            self._over()

        
    def draw(self):
        """
        Draws the game objects to the view.
        
        Every single thing you want to draw in this game is a GObject.  To draw a GObject 
        g, simply use the method g.draw(self.view).  It is that easy!
        
        Many of the GObjects (such as the ships, aliens, and bolts) are attributes in 
        Wave. In order to draw them, you either need to add getters for these attributes 
        or you need to add a draw method to class Wave.  We suggest the latter.  See 
        the example subcontroller.py from class.
        """
        if self._state == STATE_INACTIVE:
            self._background.draw(self.view)
            self._text.draw(self.view)
            self._title.draw(self.view)
        if self._state == STATE_NEWWAVE:
            self._background.draw(self.view)
            self._wave.draw(self.view)
        if self._state == STATE_ACTIVE:
            self._background.draw(self.view)
            self._wave.draw(self.view)
        if self._state == STATE_PAUSED:
            self._background.draw(self.view)
            self._text.draw(self.view)
        if self._state == STATE_COMPLETE:
            self._background.draw(self.view)
            self._text.draw(self.view)
        if self._state == STATE_MENU:
            self._background.draw(self.view)
            self._text.draw(self.view)
            for button in self._menubuttons:
                button.draw(self.view)
            
    
    
    # HELPER METHODS FOR THE STATES GO HERE
    def _newstate(self):
        """ WRITE THIS SPECIFICATION LATER """
        start = self.input.is_key_down('s')
        resume = self.input.is_key_down('spacebar')
        options = self.input.is_key_down('o')
        restart = self.input.is_key_down('r')
        themeselected = False
        if self.input.is_key_down('1') or self.input.is_key_down('2') or self.input.is_key_down('3') or self.input.is_key_down('4') or self.input.is_key_down('5') or self.input.is_key_down('6'):
            themeselected= True
        if self._lastinput == False and start == True and self._state == STATE_INACTIVE:
            self._state = STATE_NEWWAVE
        if self._lastinput == False and resume == True and self._state == STATE_PAUSED:
            self._state = STATE_CONTINUE
        if self._lastinput == False and options == True and (self._state == STATE_COMPLETE or self._state == STATE_INACTIVE):
            self._state = STATE_MENU
        if self._lastinput == False and restart == True and self._state == STATE_COMPLETE:
            self._state = STATE_INACTIVE
        if self._lastinput == False and themeselected and self._state == STATE_MENU:
            self._swapsong()
                
    def _swapsong(self):
        """Write Spec"""
        lasttheme = self._theme
        self._theme = int(self.input.keys[0])
        self._state=STATE_INACTIVE
        if self._theme == 6:
            Sound.stop(self._song)
            self._song = Sound('LastChristmas.wav')
            self._song.play(loop=True)
            self._background = GImage(x=GAME_WIDTH//2,y=GAME_HEIGHT//2,source='otherbackground.png',width=GAME_WIDTH,height=GAME_HEIGHT)
        if lasttheme == 6 and self._theme != 6:
            Sound.stop(self._song)
            self._song = Sound('8-bit-Arcade4.wav')
            self._song.play(loop = True)
            self._background = GImage(x=GAME_WIDTH//2,y=GAME_HEIGHT//2,source='background.gif',width=GAME_WIDTH,height=GAME_HEIGHT)
        
    def _over(self):
        """ WRITE SPECS """
        if self._wave.getLives() > 0:
            self._text = self._Congrats
        else:
            self._text = self._YouLose
        if self._stateTime >= 180:
            self._time = 0
            self._text = self._gameOver
    
    def _createmenu(self):
        theme1 = GLabel(text='Press 1: Blue Theme',left=300,top=GAME_HEIGHT-200,font_name='RetroGame.ttf',font_size=25,linecolor='blue')
        theme2 = GLabel(text='Press 2: Red Theme',left=300,top=GAME_HEIGHT-250,font_name='RetroGame.ttf',font_size=25, linecolor='red')
        theme3 = GLabel(text='Press 3: Purple Theme',left=300,top=GAME_HEIGHT-300,font_name='RetroGame.ttf',font_size=25,linecolor='purple')
        theme4 = GLabel(text='Press 4: Orange Theme',left=300,top=GAME_HEIGHT-350,font_name='RetroGame.ttf',font_size=25,linecolor='orange')
        theme5 = GLabel(text='Press 5: Green Theme',left=300,top=GAME_HEIGHT-400,font_name='RetroGame.ttf',font_size=25, linecolor='green')
        theme6 = GLabel(text='Press 6: Xmas Theme',left=300,top=GAME_HEIGHT-450,font_name='RetroGame.ttf',font_size=25,fillcolor='red',linecolor='white')
        return [theme1,theme2,theme3,theme4,theme5,theme6]