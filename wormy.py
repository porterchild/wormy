# Wormy (a Nibbles clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, pygame, sys
from pygame.locals import *

FPS = 6
WINDOWWIDTH = 720
WINDOWHEIGHT = 540
CELLSIZE = 20
NUM_APPLES = 3
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

    showStartScreen()
    while True:
        runGame()
        showGameOverScreen()


def runGame():
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
	apples.append(getRandomLocation())

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

        # check if the worm has hit itself, the other worm, or the edge
	# worm 1
	#edge
        if wormCoords[HEAD]['x'] == -1 or wormCoords[HEAD]['x'] == CELLWIDTH or wormCoords[HEAD]['y'] == -1 or wormCoords[HEAD]['y'] == CELLHEIGHT:
	    penalty(wormCoords)
            return # game over
	#itself
        for wormBody in wormCoords[1:]:
            if wormBody['x'] == wormCoords[HEAD]['x'] and wormBody['y'] == wormCoords[HEAD]['y']:
		penalty(wormCoords)
                return # game over
	    #check if worm 2 has hit it
            if wormBody['x'] == wormCoords2[HEAD]['x'] and wormBody['y'] == wormCoords2[HEAD]['y']:
	        penalty(wormCoords2)
                return # game over
	# worm 2
	#edge
        if wormCoords2[HEAD]['x'] == -1 or wormCoords2[HEAD]['x'] == CELLWIDTH or wormCoords2[HEAD]['y'] == -1 or wormCoords2[HEAD]['y'] == CELLHEIGHT:
	    penalty(wormCoords2)
            return # game over
	#itself
        for wormBody in wormCoords2[1:]:
            if wormBody['x'] == wormCoords2[HEAD]['x'] and wormBody['y'] == wormCoords2[HEAD]['y']:
	        penalty(wormCoords2)
                return # game over
	    #check if worm 1 has hit it
            if wormBody['x'] == wormCoords[HEAD]['x'] and wormBody['y'] == wormCoords[HEAD]['y']:
		penalty(wormCoords)
                return # game over


        # check if worm has eaten an apply
	apple_eaten = False
	apple_eaten2 = False
	for x, apple in enumerate(apples):
	    #worm1
	    if wormCoords[HEAD]['x'] == apple['x'] and wormCoords[HEAD]['y'] == apple['y']:
	        apples[x] = getRandomLocation() # set a new apple somewhere
	        apple_eaten = True
	    #worm2
	    if wormCoords2[HEAD]['x'] == apple['x'] and wormCoords2[HEAD]['y'] == apple['y']:
	        apples[x] = getRandomLocation() # set a new apple somewhere
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
	    drawApple(apple)
        drawScore(len(wormCoords) - 3, 1)
        drawScore(len(wormCoords2) - 3, 2)
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def penalty(worm):#take 2 off
	del worm[-1]
	del worm[-1]

def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Player 1-ASDW, Player 2-arrow keys. Press a key to play.', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 500, WINDOWHEIGHT - 30)
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


def getRandomLocation():
    return {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}


def showGameOverScreen():
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (WINDOWWIDTH / 2, 10)
    overRect.midtop = (WINDOWWIDTH / 2, gameRect.height + 10 + 25)

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress() # clear out any key presses in the event queue

    while True:
        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return

def drawScore(score, player):
    if player is 1:
	    scoreSurf = BASICFONT.render('Player 1: %s' % (score), True, WHITE)
	    scoreRect = scoreSurf.get_rect()
	    scoreRect.topleft = (120, 10)
	    DISPLAYSURF.blit(scoreSurf, scoreRect)
    elif player is 2:
	    scoreSurf = BASICFONT.render('Player 2: %s' % (score), True, WHITE)
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
