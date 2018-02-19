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
NUM_APPLES = 30
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
    autoOn = False
    greenWins = 0
    blueWins = 0
    global apple_mode, apple_quadrant
    apple_mode = 6
    apple_quadrant = 3

    showStartScreen()

    while True:
        runGame()
        showGameOverScreen()


def runGame():
    global apple_mode, apple_quadrant

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

    # Start the apples in a random place.
    apples = []
    for apple in range(0, NUM_APPLES):
	apples.append(Apple(apple_mode))

    while True: # main game loop
        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
		#worm 1
                if ((event.key == K_a) or (event.key == K_KP4)) and direction != RIGHT:
                    direction = LEFT
                elif ((event.key == K_d) or (event.key == K_KP6)) and direction != LEFT:
                    direction = RIGHT
                elif ((event.key == K_w) or (event.key == K_KP8)) and direction != DOWN:
                    direction = UP
                elif ((event.key == K_s) or (event.key == K_KP2)) and direction != UP:
                    direction = DOWN
		#worm 2
                if ((event.key == K_LEFT) or (event.key == K_KP4)) and direction2 != RIGHT:
                    direction2 = LEFT
                elif ((event.key == K_RIGHT) or (event.key == K_KP6)) and direction2 != LEFT:
                    direction2 = RIGHT
                elif ((event.key == K_UP) or (event.key == K_KP8)) and direction2 != DOWN:
                    direction2 = UP
                elif ((event.key == K_DOWN) or (event.key == K_KP2)) and direction2 != UP:
                    direction2 = DOWN
                elif event.key == K_ESCAPE:
                    terminate()
                elif event.key == K_k:
                    if autoOn is False:
			autoOn = True
		    elif autoOn is True:
			autoOn = False

        # check if the worm has hit itself, the other worm, or the edge
	# worm 1
	#edge
        if wormCoords[HEAD]['x'] == -1 or wormCoords[HEAD]['x'] == CELLWIDTH or wormCoords[HEAD]['y'] == -1 or wormCoords[HEAD]['y'] == CELLHEIGHT:
	    penalty(wormCoords, wormCoords2, 1)
            return # game over
	#itself
        for wormBody in wormCoords[1:]:
            if wormBody['x'] == wormCoords[HEAD]['x'] and wormBody['y'] == wormCoords[HEAD]['y']:
	        penalty(wormCoords, wormCoords2, 1)
                return # game over
	    #check if worm 2 has hit it
            if wormBody['x'] == wormCoords2[HEAD]['x'] and wormBody['y'] == wormCoords2[HEAD]['y']:
	        penalty(wormCoords2, wormCoords, 2)
                return # game over
	# worm 2
	#edge
        if wormCoords2[HEAD]['x'] == -1 or wormCoords2[HEAD]['x'] == CELLWIDTH or wormCoords2[HEAD]['y'] == -1 or wormCoords2[HEAD]['y'] == CELLHEIGHT:
	    penalty(wormCoords2, wormCoords, 2)
            return # game over
	#itself
        for wormBody in wormCoords2[1:]:
            if wormBody['x'] == wormCoords2[HEAD]['x'] and wormBody['y'] == wormCoords2[HEAD]['y']:
	        penalty(wormCoords2, wormCoords, 2)
                return # game over
	    #check if worm 1 has hit it
            if wormBody['x'] == wormCoords[HEAD]['x'] and wormBody['y'] == wormCoords[HEAD]['y']:
	        penalty(wormCoords, wormCoords2, 1)
                return # game over


        # check if worm has eaten an apple
	apple_eaten = False
	apple_eaten2 = False
	for x, apple in enumerate(apples):
	    #worm1
	    if wormCoords[HEAD]['x'] == apple.position['x'] and wormCoords[HEAD]['y'] == apple.position['y']:
	        #apples[x].position = getRandomLocation(apple_quadrant) # set a new apple somewhere
		apples[x] = Apple(apple_mode)
		#apples.append(Apple(apple_mode))
	        apple_eaten = True
	    #worm2
	    if wormCoords2[HEAD]['x'] == apple.position['x'] and wormCoords2[HEAD]['y'] == apple.position['y']:
	        #apples[x].position = getRandomLocation(apple_quadrant) # set a new apple somewhere
		apples[x] = Apple(apple_mode)
		#apples.append(Apple(apple_mode))
	        apple_eaten2 = True

        #modify tail if necessary
	#worm 1
	if apple_eaten is False:
	    del wormCoords[-1] # remove worm's tail segment
	#worm 2
	if apple_eaten2 is False:
	    del wormCoords2[-1] # remove worm's tail segment


        # move the worm by adding a segment in the direction it is moving
	#worm 1
	if autoOn is True:
		direction = getAutoDirection(wormCoords, direction)
        if direction == UP:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] - 1}
        elif direction == DOWN:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] + 1}
        elif direction == LEFT:
            newHead = {'x': wormCoords[HEAD]['x'] - 1, 'y': wormCoords[HEAD]['y']}
        elif direction == RIGHT:
            newHead = {'x': wormCoords[HEAD]['x'] + 1, 'y': wormCoords[HEAD]['y']}
        wormCoords.insert(0, newHead)
	#worm 2
	if autoOn is True:
		direction2 = getAutoDirection(wormCoords2, direction2)
        if direction2 == UP:
            newHead2 = {'x': wormCoords2[HEAD]['x'], 'y': wormCoords2[HEAD]['y'] - 1}
        elif direction2 == DOWN:
            newHead2 = {'x': wormCoords2[HEAD]['x'], 'y': wormCoords2[HEAD]['y'] + 1}
        elif direction2 == LEFT:
            newHead2 = {'x': wormCoords2[HEAD]['x'] - 1, 'y': wormCoords2[HEAD]['y']}
        elif direction2 == RIGHT:
            newHead2 = {'x': wormCoords2[HEAD]['x'] + 1, 'y': wormCoords2[HEAD]['y']}
        wormCoords2.insert(0, newHead2)
        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        drawWorm(wormCoords, 1)
        drawWorm(wormCoords2, 2)
	for apple in apples:
	    if apple.life is not 0:
		drawApple(apple.position)
	    apple_quadrant = apple.cycle(apple_quadrant)
        drawScore(len(wormCoords) - 3, 1)
        drawScore(len(wormCoords2) - 3, 2)
        pygame.display.update()
        FPSCLOCK.tick(FPS)
class Worm:
    def __init__(self, coordinates):
	self.coords = coordinates
    	

def getAutoDirection(wormCoords, currentDirection):
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
	#small chance of a random turn
	if random.randint(0, 100)%7 == 0:#change of a random turn
		if random.randint(0, 100)%2 == 0:#chance for a vertical or horizontal turn
			if random.randint(0, 100)%2 == 0:
				if currentDirection is not LEFT and wormCoords[HEAD]['x'] != CELLWIDTH - 1:
					return RIGHT
			else:
				if currentDirection is not RIGHT and wormCoords[HEAD]['x'] != 0:
					return LEFT
		else:
			if random.randint(0, 100)%2 == 0:
				if currentDirection is not DOWN and wormCoords[HEAD]['y'] != 0:
					return UP
			else:
				if currentDirection is not UP and wormCoords[HEAD]['y'] != CELLHEIGHT - 1:
					return DOWN
	return currentDirection


def penalty(penalty_worm, free_worm, penalty_player):#take 2 off first argument worm
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
    pressKeySurf = BASICFONT.render('Green-ASDW, Blue-arrow keys. Press k in game for autopilot blue', True, DARKGRAY)
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
	    print self.life
            self.life -= 1
	if self.life is 0:
	    self.position = getRandomLocation()
	    if apple_mode is 2 or apple_mode is 3:#assign new lifetimes
		if apple_mode is 2:
		    self.life = 50
		else:#apple_mode is 3 - range of lifetimes possible
		    self.life = random.randint(30, 150)
	if apple_mode is 6:
	    if random.randint(0, 2000000)%2011 is 0:
		print apple_quad
		print "awefasdvwevawvasfwefasfe"
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

def drawScore(score, player):
    if player is 1:
	    scoreSurf = BASICFONT.render('Green: %s' % (score), True, WHITE)
	    scoreRect = scoreSurf.get_rect()
	    scoreRect.topleft = (120, 10)
	    DISPLAYSURF.blit(scoreSurf, scoreRect)
    elif player is 2:
	    scoreSurf = BASICFONT.render('Blue: %s' % (score), True, WHITE)
	    scoreRect = scoreSurf.get_rect()
	    scoreRect.topright = (WINDOWWIDTH - 120, 10)
	    DISPLAYSURF.blit(scoreSurf, scoreRect)


def drawWorm(wormCoords, player):
    for coord in wormCoords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
	if player is 1:
            pygame.draw.rect(DISPLAYSURF, DARKGREEN, wormSegmentRect)
            pygame.draw.rect(DISPLAYSURF, GREEN, wormInnerSegmentRect)
	elif player is 2:
            pygame.draw.rect(DISPLAYSURF, DARKBLUE, wormSegmentRect)
            pygame.draw.rect(DISPLAYSURF, BLUE, wormInnerSegmentRect)


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
