# Wormy (a Nibbles clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, pygame, sys, math
from pygame.locals import *

FPS = 40
#FPS = 4
WINDOWWIDTH = 720
WINDOWHEIGHT = 540
CELLSIZE = 20
NUM_APPLES = 10
NUM_WORMS = 2
NEIGHBORHOOD = 7
TIME_LIMIT = 1000
CENTRALIZED = True
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

    global autoOn, total_score, total_runs
    autoOn = True
    total_score = 0
    total_runs = 0
    global apple_mode, apple_quadrant
    apple_mode = 7
    apple_quadrant = 3
    global applesDisappeared, applesEaten, timeLapsed
    timeLapsed = 0
    applesEaten = 0
    applesDisappeared = 0
    global central_destination, frenzy_remaining, CENTRALIZED
    central_destination = {}
    frenzy_remaining = 0

    showStartScreen()

    #while True:
    for app_mode in xrange(1, 8):#try all apple modes
	apple_mode = app_mode
	print "\n\napple mode:", apple_mode
	centralized_score = 0
	decentralized_score = 0
	for centralized in xrange(0,2):#try centralized and decentralized
	    if centralized is 0:
		CENTRALIZED = False
	    else:
		CENTRALIZED = True
	    print "Centralized:", CENTRALIZED
	    #for neighborhood in xrange(3,
	    for run in xrange(0,10):#trials
                runGame()
                showGameOverScreen()
	    if CENTRALIZED:
		centralized_score = total_score
	    else:
		decentralized_score = total_score
	    print "Average Score:", total_score/(total_runs * 1.0)
    	    total_score = 0
            total_runs = 0
	print "Centralized to Decentralized ratio:", centralized_score/(decentralized_score * 1.0)


def runGame():
    global apple_mode, apple_quadrant
    applesDisappeared = 0
    applesEaten = 0
    timeLapsed = 0

    global autoOn, total_score, total_runs
    global central_destination, frenzy_remaining, CENTRALIZED
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
		    continue
	        #check if another has hit it
		for wormHead in worms:
	            if len(wormHead.coords) is 0:
		        continue
		    #print "\n"
		    #print "+++wormHead.coords"
		    #print wormHead.coords
                    if wormBody['x'] == wormHead.coords[HEAD]['x'] and wormBody['y'] == wormHead.coords[HEAD]['y']:
			if len(worm.coords) > len(wormHead.coords):#kill the longer worm
			    worm.coords = []
			else:
			    wormHead.coords = []

	#get rid of empty worms
	worms = [worm for worm in worms if len(worm.coords) != 0]

	#check if worm has eaten an apple
	for worm in worms:
	    for x, apple in enumerate(apples):
		if worm.coords[HEAD]['x'] == apple.position['x'] and worm.coords[HEAD]['y'] == apple.position['y']:
		    applesEaten += 1
		    #apples[x].position = getRandomLocation(apple_quadrant) # set a new apple somewhere
		    apples[x] = Apple(apple_mode)
		    #apples.append(Apple(apple_mode))
		    worm.apple_eaten = True

	    #add code to increase probablity of entering frenzy mode (for centralized controller)
	    if CENTRALIZED:
	        if worm.frenzy_ratio > 0.5:
		    worm.frenzy_ratio *= 0.9 #decreases every cycle
	        if worm.apple_eaten is True: #increases if an apple was eaten
		    worm.frenzy_ratio *= 1.8
	        if worm.frenzy_ratio > len(apples)/len(apples): #high enough to be considered a frenzy
		    #set destination for other worms
		    central_destination = worm.coords[HEAD]
		    frenzy_remaining = len(worms) * 35
		elif frenzy_remaining > 0:
		    frenzy_remaining -= 1
		if frenzy_remaining is 0:
		    central_destination = {}


        #modify tail if necessary
	for worm in worms:
	    if worm.apple_eaten is False:
		del worm.coords[-1] 		#remove worm's tail segment (not a penalty, just how movement works)
	    else:
		worm.apple_eaten = False 	#don't cut the tail, but reset the flag
		worm.apple_destination = None

	#get rid of empty worms
	worms = [worm for worm in worms if len(worm.coords ) != 0]
	if len(worms) is 0:#everyone died
            startx = random.randint(5, CELLWIDTH - 5)
            starty = random.randint(5, CELLHEIGHT - 5)
    	    coordinates = [{'x': startx,     'y': starty},
                  	  {'x': startx - 1, 'y': starty},
                  	  {'x': startx - 2, 'y': starty}]
	    worms.append(Worm(coordinates, RIGHT))

        # move the worm by adding a segment in the direction it is moving
	for worm in worms:
	    if autoOn is True:
		worm.direction = getAutoDirection(worm.coords, worm.direction, apples, worm)

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
		drawApple(apple)
	    apple_quadrant = apple.cycle(apple_quadrant)

	#score = (applesEaten - applesDisappeared)/NUM_APPLES
	score = (applesEaten - applesDisappeared)
	timeLapsed +=1
	if timeLapsed == TIME_LIMIT:
	    total_runs += 1
	    total_score += score
	    print "Score:", score
	    return
	drawScore(score)
        pygame.display.update()
        FPSCLOCK.tick(FPS)

class Worm:
    def __init__(self, coordinates, startDirection):
	self.coords = coordinates
	self.direction = startDirection
	self.apple_eaten = False
	self.apple_destination = None
	self.frenzy_ratio = 1 #whether I'm  eating a lot of apples at the moment - this is for the centralized controller
    def split(self):
	newWormCoords = self.coords[6:]
	del self.coords[4:]
	return newWormCoords, RIGHT

def getAutoDirection(wormCoords, currentDirection, apples, worm):
	#collisions
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

	#if centralized control is activated, go in the direction of the frenzy if there is one
	if CENTRALIZED:
	    #if random.randint(0, 2000)%8 == 0:#artificial limitation - simulates communication latency
		#return currentDirection

	    # if 'x' in central_destination:
		# if abs(wormCoords[HEAD]['x'] - destination['x']) > abs(wormCoords[HEAD]['y'] - destination['y']):#priority to lateral movement
	    # 	    if wormCoords[HEAD]['x'] < central_destination['x'] and currentDirection is not LEFT:
		#         return RIGHT
	    # 	    if wormCoords[HEAD]['x'] > central_destination['x'] and currentDirection is not RIGHT:
		#         return LEFT
		# else:#priority to longitudinal movement
	    # 	    if wormCoords[HEAD]['y'] < central_destination['y'] and currentDirection is not UP:
		#         return DOWN
	    # 	    if wormCoords[HEAD]['y'] > central_destination['y'] and currentDirection is not DOWN:
		#         return UP
	
	    if worm.apple_destination is not None:#make sure the claimed apple still exists
		if worm.apple_destination in apples:
		    pass
		else:
		    worm.apple_destination = None

	    #scan through apples, chase the closest one
	    if worm.apple_destination is None:
		closest_euclid = 1000
		destination = {}
		final_apple_choice = None;
		for apple in apples:
		    dist = math.sqrt(abs((wormCoords[HEAD]['x'] - apple.position['x'])**2) + abs((wormCoords[HEAD]['y'] - apple.position['y'])**2))
		    if dist < closest_euclid and apple.claimed is False:
			closest_euclid = dist
			final_apple_choice = apple
	        worm.apple_destination = final_apple_choice			
	
	    if worm.apple_destination is not None:
	    	worm.apple_destination.claimed = True
	   	worm.apple_destination.still_claimed = 10
	    	destination = worm.apple_destination.position


	    if 'x' in destination:
		if abs(wormCoords[HEAD]['x'] - destination['x']) > abs(wormCoords[HEAD]['y'] - destination['y']):#priority to lateral movement
	    	    if wormCoords[HEAD]['x'] < destination['x']:
			if currentDirection is not LEFT:
		            return RIGHT
			else:#otherwise it will keep going left and never turn around until it hits a wall
			    return UP
	    	    if wormCoords[HEAD]['x'] > destination['x']:
			if currentDirection is not RIGHT:
		            return LEFT
			else:
			    return UP
		else:#priority to longitudinal movement
	    	    if wormCoords[HEAD]['y'] < destination['y']:
			if currentDirection is not UP:
		            return DOWN
			else:
			    return RIGHT
	    	    if wormCoords[HEAD]['y'] > destination['y']:
			if currentDirection is not DOWN:
		            return UP
			else:
			    return RIGHT

    	    #collisions continued
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
    	    return currentDirection


	# make it turn left if it passes an apple on the left, etc
	for apple in apples:
	    for offset in xrange(1, NEIGHBORHOOD+1):
		if wormCoords[HEAD]['x'] == apple.position['x'] + offset and wormCoords[HEAD]['y'] == apple.position['y'] and currentDirection is not RIGHT:
		    return LEFT
	    	if wormCoords[HEAD]['x'] == apple.position['x'] - offset and wormCoords[HEAD]['y'] == apple.position['y'] and currentDirection is not LEFT:
		    return RIGHT
	    	if wormCoords[HEAD]['x'] == apple.position['x'] and wormCoords[HEAD]['y'] == apple.position['y'] + offset and currentDirection is not DOWN:
		    return UP
	    	if wormCoords[HEAD]['x'] == apple.position['x'] and wormCoords[HEAD]['y'] == apple.position['y'] - offset and currentDirection is not UP:
		    return DOWN
	#collisions continued
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
	if random.randint(0, 100)%11 == 0:#change of a random turn
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
	    self.position = getRandomLocation()
	    self.life = random.randint(30, 1500) #1500 is effectively infinite
	if apple_mode is 5:#appear in single quadrant
	    self.position = getRandomLocation(apple_quadrant)
	    self.life = 1
	if apple_mode is 6:#appear in changing quadrant
	    self.position = getRandomLocation(apple_quadrant)
	    self.life = 1
	if apple_mode is 7:#appear in one small "tree" location
	    self.position = getRandomLocation(5)
	    self.life = 1
	self.claimed = False
	self.still_claimed = 10
    def cycle(self, apple_quad):
	self.still_claimed -= 1
	if self.still_claimed is 0:
	    self.claimed = False
	    self.still_claimed = 10
	if apple_mode is 2 or apple_mode is 3 or apple_mode is 4:# finite life
            self.life -= 1
	if self.life is -1:
	    self.position = getRandomLocation()
	    if apple_mode is 2 or apple_mode is 3 or apple_mode is 4:#assign new lifetimes
		if apple_mode is 2:
		    self.life = 50
		elif apple_mode is 3:#apple_mode is 3 - range of lifetimes possible
		    self.life = random.randint(30, 150)
		elif apple_mode is 4:
		    self.life = random.randint(30, 1500)
	if apple_mode is 6:
	    if random.randint(0, 2000000)%2011 is 0:
		apple_quad = random.randint(1, 2000000)%5
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
    elif quadrant is 5:#only spawn in a small "tree" area (hardcoded location)
	return {'x': random.randint((CELLWIDTH - 1)/4, (CELLWIDTH - 1)/2), 'y': random.randint((CELLHEIGHT - 1)/4, (CELLHEIGHT - 1)/2)}

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


def drawApple(apple):
    coord = apple.position
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    if apple.claimed:
        pygame.draw.rect(DISPLAYSURF, BLUE, appleRect)
    else:	
        pygame.draw.rect(DISPLAYSURF, RED, appleRect)


def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))


if __name__ == '__main__':
    main()
