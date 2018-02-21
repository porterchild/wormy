# Wormy (a Nibbles clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, pygame, sys
from pygame.locals import *

FPS = 9
WINDOWWIDTH = 720
WINDOWHEIGHT = 540
CELLSIZE = 20
NUM_APPLES = 10
NUM_WORMS = 2
NEIGHBORHOOD = 20
TIME_LIMIT = 300
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

#             R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
BLUE      = (  0,   0, 255)
DARKBLUE  = (  0,   0, 155)
DARKGRAY  = ( 40,  40,  40)
BGCOLOR = BLACK

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0 # syntactic sugar: index of the worm's head

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT


    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('Worry')

    global autoOn, greenWins, blueWins
    autoOn = True
    greenWins = 0
    blueWins = 0
    global apple_mode, apple_quadrant
    apple_mode = 6
    apple_quadrant = 3
    global applesDisappeared, applesEaten, timeLapsed
    timeLapsed = 0
    applesEaten = 0
    applesDisappeared = 0

    showStartScreen()

    while True:
        runGame()
        showGameOverScreen()


def runGame():
    global apple_mode, apple_quadrant
    global applesDisappeared, applesEaten, timeLapsed
    applesDisappeared = 0
    applesEaten = 0
    timeLapsed = 0

    global autoOn, greenWins, blueWins
    print "green to blue"
    print greenWins
    print blueWins
    # Set a random start point.
    #startx = random.randint(5, CELLWIDTH - 6)
    #starty = random.randint(5, CELLHEIGHT - 6)

    #worm 1 (left side)
    startx = random.randint(5, CELLWIDTH/2 - 6)
    starty = random.randint(5, CELLHEIGHT - 6)
    #worm 2 (right side)
    startx2 = random.randint(CELLWIDTH/2 + 5, CELLWIDTH - 6)
    starty2 = random.randint(5, CELLHEIGHT - 6)

    #worm 1
    wormCoords = [{'x': startx,     'y': starty},
                  {'x': startx - 1, 'y': starty},
                  {'x': startx - 2, 'y': starty}]
    #worm2
    wormCoords2 = [{'x': startx2,     'y': starty2},
                   {'x': startx2 - 1, 'y': starty2},
                   {'x': startx2 - 2, 'y': starty2}]
    #worm 1
    direction = RIGHT
    #worm 2
    direction2 = RIGHT

    worms = []
    for worm in range(1, NUM_WORMS+1):
	coordinates = []
	if worm is 1:
            startx = random.randint(5, CELLWIDTH/2 - 6)
            starty = random.randint(5, CELLHEIGHT - 6)
	    coordinates = [{'x': startx,     'y': starty},
			  {'x': startx - 1, 'y': starty},
			  {'x': startx - 2, 'y': starty}]
	elif worm is 2:
    	    startx2 = random.randint(CELLWIDTH/2 + 5, CELLWIDTH - 6)
    	    starty2 = random.randint(5, CELLHEIGHT - 6)
	    coordinates = [{'x': startx2,     'y': starty2},
			  {'x': startx2 - 1, 'y': starty2},
			  {'x': startx2 - 2, 'y': starty2}]
	worms.append(Worm(coordinates, RIGHT))


    # Start the apples in a random place.
    apples = []
    for apple in range(0, NUM_APPLES):
	apples.append(Apple(apple_mode))

    while True: # main game loop
        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
    		for worm in worms:
		    if ((event.key == K_a) or (event.key == K_KP4)) and worm.direction != RIGHT:
			worm.direction = LEFT
		    elif ((event.key == K_d) or (event.key == K_KP6)) and worm.direction != LEFT:
			worm.direction = RIGHT
		    elif ((event.key == K_w) or (event.key == K_KP8)) and worm.direction != DOWN:
			worm.direction = UP
		    elif ((event.key == K_s) or (event.key == K_KP2)) and worm.direction != UP:
			worm.direction = DOWN
                if event.key == K_ESCAPE:
                    terminate()
                elif event.key == K_k:
                    if autoOn is False:
			autoOn = True
		    elif autoOn is True:
			autoOn = False

	for worm in worms:
	    if len(worm.coords) is 0:
		continue
            # check if the worm has hit itself, the other worm, or the edge

	    #edge
            if worm.coords[HEAD]['x'] == -1 or worm.coords[HEAD]['x'] == CELLWIDTH or worm.coords[HEAD]['y'] == -1 or worm.coords[HEAD]['y'] == CELLHEIGHT:
		print "deleted edge"
		worm.coords = []
		continue

	    #itself
            for wormBody in worm.coords[1:]:
	        if len(worm.coords) is 0:
		    continue
		#print "\n"
		#print "wormBody"
		#print wormBody
                if wormBody['x'] == worm.coords[HEAD]['x'] and wormBody['y'] == worm.coords[HEAD]['y']:
		    worm.coords = []
		    print "deleted1"
		    continue
	        #check if another has hit it
		for wormHead in worms:
	            if len(wormHead.coords) is 0:
		        continue
		    #print "\n"
		    #print "+++wormHead.coords"
		    #print wormHead.coords
                    if wormBody['x'] == wormHead.coords[HEAD]['x'] and wormBody['y'] == wormHead.coords[HEAD]['y']:
		        print "deleted2"
			if len(worm.coords) > len(wormHead.coords):#kill the longer worm
			    worm.coords = []
			else:
			    wormHead.coords = []

	#get rid of empty worms
	worms = [worm for worm in worms if len(worm.coords ) != 0]

	#check if worm has eaten an apple
	for worm in worms:
	    for x, apple in enumerate(apples):
		if worm.coords[HEAD]['x'] == apple.position['x'] and worm.coords[HEAD]['y'] == apple.position['y']:
		    applesEaten += 1
		    #apples[x].position = getRandomLocation(apple_quadrant) # set a new apple somewhere
		    apples[x] = Apple(apple_mode)
		    #apples.append(Apple(apple_mode))
		    worm.apple_eaten = True


        #modify tail if necessary
	for worm in worms:
	    if worm.apple_eaten is False:
		del worm.coords[-1] 		#remove worm's tail segment (not a penalty, just how movement works)
	    else:
		worm.apple_eaten = False 	#don't cut the tail, but reset the flag

	#get rid of empty worms
	worms = [worm for worm in worms if len(worm.coords ) != 0]
	if len(worms) is 0:#everyone died, game over
		return

        # move the worm by adding a segment in the direction it is moving
	for worm in worms:
	    if autoOn is True:
		worm.direction = getAutoDirection(worm.coords, worm.direction, apples)

            if worm.direction == UP:
                newHead = {'x': worm.coords[HEAD]['x'], 'y': worm.coords[HEAD]['y'] - 1}
            elif worm.direction == DOWN:
                newHead = {'x': worm.coords[HEAD]['x'], 'y': worm.coords[HEAD]['y'] + 1}
            elif worm.direction == LEFT:
                newHead = {'x': worm.coords[HEAD]['x'] - 1, 'y': worm.coords[HEAD]['y']}
            elif worm.direction == RIGHT:
                newHead = {'x': worm.coords[HEAD]['x'] + 1, 'y': worm.coords[HEAD]['y']}
            worm.coords.insert(0, newHead)

        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()

	for worm in worms:
	    if len(worm.coords) is 8:
		#split returns coordinates for posterior half of worm
		newCoords, newDirection = worm.split()
		worms.append(Worm(newCoords, newDirection))
	    drawWorm(worm.coords, 1)
	for apple in apples:
	    if apple.life == 0:
		applesDisappeared += 1
	    else:
		drawApple(apple.position)
	    apple_quadrant = apple.cycle(apple_quadrant)

	score = applesEaten - applesDisappeared
	timeLapsed +=1
	if timeLapsed == TIME_LIMIT:
	    return
	drawScore(score)
        pygame.display.update()
        FPSCLOCK.tick(FPS)

class Worm:
    def __init__(self, coordinates, startDirection):
	self.coords = coordinates
	self.direction = startDirection
	self.apple_eaten = False
    def split(self):
	newWormCoords = self.coords[5:]
	del self.coords[4:]
	return newWormCoords, RIGHT

def getAutoDirection(wormCoords, currentDirection, apples):
	#corner cases first
	if wormCoords[HEAD]['x'] == 0 and wormCoords[HEAD]['y'] == 0:#top left
		if currentDirection is LEFT:
			return DOWN
		else:
			return RIGHT
	if wormCoords[HEAD]['x'] == 0 and wormCoords[HEAD]['y'] == CELLHEIGHT - 1:#bottom left
		if currentDirection is LEFT:
			return UP
		else:
			return RIGHT
	if wormCoords[HEAD]['x'] == CELLWIDTH - 1 and wormCoords[HEAD]['y'] == 0:#top right
		if currentDirection is RIGHT:
			return DOWN
		else:
			return LEFT
	if wormCoords[HEAD]['x'] == CELLWIDTH - 1 and wormCoords[HEAD]['y'] == CELLHEIGHT - 1:#bottom right
		if currentDirection is RIGHT:
			return UP
		else:
			return LEFT

	#left edge
	if wormCoords[HEAD]['x'] == 0 and currentDirection is LEFT:
		if random.randint(0, 100)%2 == 0:
			return UP
		else:
			return DOWN
	#right edge
	if wormCoords[HEAD]['x'] == CELLWIDTH - 1 and currentDirection is RIGHT:
		if random.randint(0, 100)%2 == 0:
			return UP
		else:
			return DOWN
	#top edge
	if wormCoords[HEAD]['y'] == 0 and currentDirection is UP:
		if random.randint(0, 100)%2 == 0:
			return RIGHT
		else:
			return LEFT
	#bottom edge
	if wormCoords[HEAD]['y'] == CELLHEIGHT - 1 and currentDirection is DOWN:
		if random.randint(0, 100)%2 == 0:
			return RIGHT
		else:
			return LEFT
	# #small chance of a random turn
	# if random.randint(0, 100)%7 == 0:#change of a random turn
	# 	if random.randint(0, 100)%2 == 0:#chance for a vertical or horizontal turn
	# 		if random.randint(0, 100)%2 == 0:
	# 			if currentDirection is not LEFT and wormCoords[HEAD]['x'] != CELLWIDTH - 1:
	# 				return RIGHT
	# 		else:
	# 			if currentDirection is not RIGHT and wormCoords[HEAD]['x'] != 0:
	# 				return LEFT
	# 	else:
	# 		if random.randint(0, 100)%2 == 0:
	# 			if currentDirection is not DOWN and wormCoords[HEAD]['y'] != 0:
	# 				return UP
	# 		else:
	# 			if currentDirection is not UP and wormCoords[HEAD]['y'] != CELLHEIGHT - 1:
	# 				return DOWN

	#test, make it turn left if it passes an apple one space to the left of it
	for apple in apples:
	    for offset in xrange(1, NEIGHBORHOOD+1):
		if wormCoords[HEAD]['x'] == apple.position['x'] + offset and wormCoords[HEAD]['y'] == apple.position['y']:
		    return LEFT
	    	if wormCoords[HEAD]['x'] == apple.position['x'] - offset and wormCoords[HEAD]['y'] == apple.position['y']:
		    return RIGHT
	    	if wormCoords[HEAD]['x'] == apple.position['x'] and wormCoords[HEAD]['y'] == apple.position['y'] + offset:
		    return UP
	    	if wormCoords[HEAD]['x'] == apple.position['x'] and wormCoords[HEAD]['y'] == apple.position['y'] - offset:
		    return DOWN
	return currentDirection

class Apple:
    def __init__(self, apple_mode):
	if apple_mode is 1:#uniformly distributed, infinite lifetime
	    self.position = getRandomLocation()
	    self.life = 1
	if apple_mode is 2:#uniformly distributed, short lifetime
	    self.position = getRandomLocation()
	    self.life = 50 #will last this many frames
	if apple_mode is 3:#uniformly distributed, range of lifetimes
	    self.position = getRandomLocation()
	    self.life = random.randint(30, 150) #will last this many frames
	if apple_mode is 4:#change between modes 1, 2, and 3
	    self.position = getRandomLocation(apple_quadrant)
	    self.life = random.randint(30, 150) #will last this many frames
	if apple_mode is 5:#appear in single quadrant
	    self.position = getRandomLocation(apple_quadrant)
	    self.life = 1
	if apple_mode is 6:#appear in changing quadrant
	    self.position = getRandomLocation(apple_quadrant)
	    self.life = 1
    def cycle(self, apple_quad):
	if apple_mode is 2 or apple_mode is 3:# finite life
            self.life -= 1
	if self.life is -1:
	    self.position = getRandomLocation()
	    if apple_mode is 2 or apple_mode is 3:#assign new lifetimes
		if apple_mode is 2:
		    self.life = 50
		else:#apple_mode is 3 - range of lifetimes possible
		    self.life = random.randint(30, 150)
	if apple_mode is 6:
	    if random.randint(0, 2000000)%2011 is 0:
		print apple_quad
		print "randomly changing apple spawing quadrant"
		print apple_quad
		apple_quad = random.randint(0, 2000000)%5
	return apple_quad

def getRandomLocation(quadrant=0):
    if quadrant is 0:
    	return {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}
    elif quadrant is 1:
	return {'x': random.randint(0, (CELLWIDTH - 1)/2), 'y': random.randint(0, (CELLHEIGHT - 1)/2)}
    elif quadrant is 2:
	return {'x': random.randint((CELLWIDTH - 1)/2, CELLWIDTH - 1), 'y': random.randint(0, (CELLHEIGHT - 1)/2)}
    elif quadrant is 3:
	return {'x': random.randint(0, (CELLWIDTH - 1)/2), 'y': random.randint((CELLHEIGHT - 1)/2, CELLHEIGHT - 1)}
    elif quadrant is 4:
	return {'x': random.randint((CELLWIDTH - 1)/2, CELLWIDTH - 1), 'y': random.randint((CELLHEIGHT - 1)/2, CELLHEIGHT - 1)}

def penalty(penalty_worm, free_worm, penalty_player):#take 2 off first argument worm
    print "penalty on ", penalty_player
    del penalty_worm[-1]
    del penalty_worm[-1]
    DISPLAYSURF.fill((  0,   0,   0))
    drawGrid()
    if penalty_player is 1:
	    p1Score = len(penalty_worm) -3
	    p2Score = len(free_worm) - 3
	    drawScore(p1Score, 1)
	    drawScore(p2Score, 2)
    	    updateScores(p1Score, p2Score)
    elif penalty_player is 2:
	    p2Score = len(penalty_worm) -3
	    p1Score = len(free_worm) - 3
	    drawScore(p2Score, 2)
	    drawScore(p1Score, 1)
    	    updateScores(p1Score, p2Score)
    pygame.display.update()

def updateScores(p1, p2):
        global greenWins, blueWins
	if p1 > p2:
		greenWins += 1
	elif p2 > p1:
		blueWins += 1


def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Press k in-game for manual control', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 700, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)


def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key


def showStartScreen():
    titleFont = pygame.font.Font('freesansbold.ttf', 100)
    titleSurf1 = titleFont.render('Worry!', True, BLACK, RED)
    titleSurf2 = titleFont.render('Worry!', True, (33,54,122))

    degrees1 = 0
    degrees2 = 0
    while True:
        DISPLAYSURF.fill(BGCOLOR)
        rotatedSurf1 = pygame.transform.rotate(titleSurf1, degrees1)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf1, rotatedRect1)

        rotatedSurf2 = pygame.transform.rotate(titleSurf2, degrees2)
        rotatedRect2 = rotatedSurf2.get_rect()
        rotatedRect2.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf2, rotatedRect2)

        drawPressKeyMsg()

        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        degrees1 += 3 # rotate by 3 degrees each frame
        degrees2 += 7 # rotate by 7 degrees each frame


def terminate():
    pygame.quit()
    sys.exit()



def showGameOverScreen():
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (WINDOWWIDTH / 2, 30)
    overRect.midtop = (WINDOWWIDTH / 2, gameRect.height + 10 + 25)

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress() # clear out any key presses in the event queue

    return
    while True:
        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return

def drawScore(score):
    scoreSurf = BASICFONT.render('Score: %s' % (score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (120, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)


def drawWorm(wormCoords, player=1):
    for coord in wormCoords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
	if player is 1:
            pygame.draw.rect(DISPLAYSURF, DARKGREEN, wormSegmentRect)
            pygame.draw.rect(DISPLAYSURF, GREEN, wormInnerSegmentRect)
	#elif player is 2:
            #pygame.draw.rect(DISPLAYSURF, DARKBLUE, wormSegmentRect)
            #pygame.draw.rect(DISPLAYSURF, BLUE, wormInnerSegmentRect)


def drawApple(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, RED, appleRect)


def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))


if __name__ == '__main__':
    main()
