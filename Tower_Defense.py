import pygame
import random
pygame.init()

#Window parameters
windowX = 1200
windowY = 600

#Create game window
win = pygame.display.set_mode((windowX, windowY))
pygame.display.set_caption("Tower Defense")

#Start game timer
clock = pygame.time.Clock()

#File directories
imageDirect = "C:\Python27\PygameAssets\Tower_Defense\Images"
fileDirect = "C:\Python27\PygameAssets\Tower_Defense\Files"

#Load images
mm = pygame.image.load(imageDirect + "\mainMenu.jpg")
bg = pygame.image.load(imageDirect + "\map.jpg")
go = pygame.image.load(imageDirect + "\gameOver.jpg")
newGameBtn = pygame.image.load(imageDirect + "\NewGameBtn.png")
loadGameBtn = pygame.image.load(imageDirect + "\LoadGameBtn.png")
onWaveBtn = pygame.image.load(imageDirect + "\onWaveBtn.png")
offWaveBtn = pygame.image.load(imageDirect + "\offWaveBtn.png")
onSaveBtn = pygame.image.load(imageDirect + "\SaveBtn.png")
onUpgradeBtn = pygame.image.load(imageDirect + "\UpgradeBtn.png")
offUpgradeBtn = pygame.image.load(imageDirect + "\offUpgradeBtn.png")
fireBtn = pygame.image.load(imageDirect + "\FireBtn.png")
waterBtn = pygame.image.load(imageDirect + "\WaterBtn.png")
grassBtn = pygame.image.load(imageDirect + "\GrassBtn.png")
rockBtn = pygame.image.load(imageDirect + "\RockBtn.png")
offBtn = pygame.image.load(imageDirect + "\OffBtn.png")

#Tower list
towers = []

#Enemy list
enemies = []

#Button list
buttons = []

#Read tower stats file
towerFile = open(fileDirect + "\TowerStats.txt",'r')
if towerFile.mode == 'r':
    towerStats = []
    towerFile.readline()
    content = towerFile.readline()
    while content != "":
        towerStats.append(content.split("\t"))
        content = towerFile.readline()
    towerFile.close()

#Read enemy stats file
enemyFile = open(fileDirect + "\EnemyStats.txt",'r')
if enemyFile.mode == 'r':
    enemyStats = []
    enemyFile.readline()
    content = enemyFile.readline()
    while content != "":
        enemyStats.append(content.split("\t"))
        content = enemyFile.readline()
    enemyFile.close()


#Tower class
class good(object):
    def __init__(self,x,y,towerID):
        self.id = towerID                           # tower type ID
        self.x = x                                  # x position
        self.y = y                                  # y position
        self.width = 80                             # image width
        self.height = 80                            # image height
        self.damage = int(towerStats[towerID][1])   # tower damage per hit
        self.speed = int(towerStats[towerID][2])    # tower shoot speed (lower = faster)
        self.shootCount = self.speed                # shooting cooldown timer
        self.range = int(towerStats[towerID][3])    # tower range
        self.selected = False                       # current tower selected status
        self.rangeColor = (0,128,255)               # range color
        self.target = 0                             # target enemy
        self.live = False                           # tower activated status
        self.ground = int(towerStats[towerID][5])   # can/can't target ground enemies
        self.air = int(towerStats[towerID][6])      # can/can't target flying enemies
        self.cost = int(towerStats[towerID][4])     # price of tower

        #Load tower image
        self.graphic = pygame.image.load(imageDirect + towerStats[towerID][7])

    #Draw tower on the screen
    def draw(self,win):
        win.blit(self.graphic, (self.x,self.y))

        if self.selected:
            pygame.draw.circle(win, self.rangeColor, (self.x + self.width//2,self.y + self.height//2), self.range, 10)
            win.blit(self.graphic, (1050,50))

    
    #Return the index number of the furthest enemy in range
    def findEnemy(self,enemies):
        maxLife = 0
        enemyIndex = 0
        
        for enemy in enemies:
            if enemy.inRange(self) and enemy.lifeTime > maxLife:
                enemyIndex = enemies.index(enemy)
                maxLife = enemy.lifeTime
        return enemyIndex

    #Return true if tower was clicked with the mouse
    def isPressed(self):
        if pygame.mouse.get_pos()[0] > self.x and pygame.mouse.get_pos()[0] < self.x + self.width:
            if pygame.mouse.get_pos()[1] > self.y and pygame.mouse.get_pos()[1] < self.y + self.height:
                return True
        return False

    #Return true if locaion of new tower placement is valid
    def isValidLocation(self,towers):
        for tower in towers: 
            if towers.index(tower) != len(towers)-1 and self.y < tower.y + tower.height and self.y + self.height > tower.y:
                if self.x + self.width > tower.x and self.x < tower.x + tower.width:
                    return False
        if self.y < 118 and self.y + self.height > 63:
            if self.x < 412:
                return False
        if self.y < 349 and self.y + self.height > 118:
            if self.x + self.width > 346 and self.x < 412:
                return False
        if self.y < 349 and self.y + self.height > 292:
            if self.x + self.width > 232 and self.x < 346:
                return False
        if self.y < 530 and self.y + self.height > 349:
            if self.x + self.width > 232 and self.x < 295:
                return False
        if self.y < 530 and self.y + self.height > 461:
            if self.x + self.width > 295 and self.x < 638:
                return False
        if self.y < 461 and self.y + self.height > 57:
            if self.x + self.width > 563 and self.x < 638:
                return False
        if self.y < 124 and self.y + self.height > 57:
            if self.x + self.width > 638 and self.x < 830:
                return False
        if self.y < 280 and self.y + self.height > 124:
            if self.x + self.width > 766 and self.x < 829:
                return False
        if self.y < 280 and self.y + self.height > 225:
            if self.x + self.width > 829:
                return False
        if self.x + self.width >= 1000:
            return False
        return True


#Enemy class
class bad(object):
    def __init__(self,enemyID):
        self.id = enemyID                               # enemy type ID
        self.x = 0                                      # x position
        self.y = 68                                     # y position
        self.path = 350                                 # furthest point until new path
        self.turns = 0                                  # number of turns made
        self.width = 48                                 # image width
        self.height = 48                                # image height
        self.vel = int(enemyStats[enemyID][1])          # movement speed
        self.maxhealth = int(enemyStats[enemyID][2])    # max health
        self.health = self.maxhealth                    # health remaining
        self.isVertical = False                         # determines if movement is along x or y axis
        self.live = True                                # life status
        self.flying = int(enemyStats[enemyID][4])       # ground/air enemy status
        self.lifeTime = 0                               # how far throught the track the enemy has gone
        self.reward = int(enemyStats[enemyID][3])       # money gained from killing the enemy

        #Load enemy image
        self.graphic = pygame.image.load(imageDirect + enemyStats[enemyID][5])

    #Draw enemy on the screen
    def draw(self, win):
        if self.live:
            win.blit(self.graphic, (self.x,self.y))
            pygame.draw.rect(win, (255,0,0), (self.x, self.y - 20, 50, 10))
            pygame.draw.rect(win, (0,128,0), (self.x, self.y - 20, 50 * (float(self.health)/float(self.maxhealth)), 10))

    #Move enemy
    def move(self):
        if not self.isVertical:
            if self.vel > 0:
                if self.x < self.path + self.vel:
                    self.x += self.vel
                else:
                    self.changePath()
            if self.vel < 0:
                if self.x > self.path - self.vel:
                    self.x += self.vel
                else:
                    self.changePath()
        else:
            if self.vel > 0:
                if self.y < self.path + self.vel:
                    self.y += self.vel
                else:
                    self.changePath()
            if self.vel < 0:
                if self.y > self.path - self.vel:
                    self.y += self.vel
                else:
                    self.changePath()
        self.lifeTime += self.vel

    #Keep enemy on the path
    def changePath(self):
        if self.turns == 0:  
            self.isVertical = True
            self.path = 293
        elif self.turns == 1:
            self.isVertical = False
            self.path = 236
            self.vel *= -1
        elif self.turns == 2:
            self.isVertical = True
            self.path = 467
            self.vel *= -1
        elif self.turns == 3:
            self.isVertical = False
            self.path = 572
        elif self.turns == 4:
            self.isVertical = True
            self.path = 65
            self.vel *= -1
        elif self.turns == 5:
            self.isVertical = False
            self.path = 770
            self.vel *= -1
        elif self.turns == 6:
            self.isVertical = True
            self.path = 220
        elif self.turns == 7:
            self.isVertical = False
            self.path = 940

        else:
            self.vel = 0
            self.x = 500
            self.live = False
        self.turns += 1

    #Return true if an enemy is in range of a tower     
    def inRange(self,tower):
        if (self.flying and tower.air) or (not self.flying and tower.ground):
            if (((tower.x + tower.width//2)-(self.x + self.width//2))**2+((tower.y + tower.height//2)-(self.y + enemy.height//2))**2)**0.5 <= tower.range and self.live:
                return True
            else:
                return False
        else:
            return False

    #Exectuted when enemy is hit by a tower
    def hit(self,tower):
        #Damage enemy if health is above 0
        if self.health > tower.damage:
            self.health -= tower.damage

        #Kill enemy if health is below 0
        else:
            self.live = False

#Button class
class button(object):
    def __init__(self,x,y,width,height,onGraphic,offGraphic):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.on = True
        self.onGraphic = onGraphic
        self.offGraphic = offGraphic

    #Draw button on the screen
    def draw(self,win):
        if self.on:
            win.blit(self.onGraphic, (self.x,self.y))
        else:
            win.blit(self.offGraphic, (self.x,self.y))

    #Return true if button is clicked on with mouse
    def isPressed(self):
        if pygame.mouse.get_pos()[0] > self.x and pygame.mouse.get_pos()[0] < self.x + self.width:
            if pygame.mouse.get_pos()[1] > self.y and pygame.mouse.get_pos()[1] < self.y + self.height:
                return True
        return False


#Create new enemies, types depend on wave number
def spawnEnemy(waves):
    if waves <= 3:
        enemies.append(bad(0))
    elif waves <= 8:
        enemies.append(bad(random.randint(0,1)))
    elif waves <= 12:
        enemies.append(bad(random.randint(0,2)))
    else:
        enemies.append(bad(random.randint(0,len(enemyStats)-1)))

#Update game window display
def redrawGameWindow():
    win.blit(bg, (0,0))
    startWaveBtn.draw(win)
    saveBtn.draw(win)
    upgradeBtn.draw(win)
    for btn in buttons:
        btn.draw(win)
    for enemy in enemies:
        enemy.draw(win)
    for tower in towers:
        tower.draw(win)
    livesText = font.render("Lives: " + str(playerLives), 1, (0,0,0))
    moneyText = font.render("Money: " + str(money), 1, (0,0,0))
    wavesText = font.render("Wave: " + str(waves), 1, (0,0,0))
    if selectedTower != len(towers):
        infoText = font.render(str(towerStats[towers[selectedTower].id][8].rstrip("\n")), 1, (0,0,0))
        upgradeText = infoFont.render(str(towerStats[towers[selectedTower].id][9].rstrip("\n")), 1, (0,0,0))
        win.blit(infoText,(1050,18))
        win.blit(upgradeText,(1025,200))
    win.blit(livesText,(10,10))
    win.blit(moneyText,(10,30))
    win.blit(wavesText,(150,10))
    pygame.display.update()


#Define mouse states
mouseState = False
prevMouseState = False

#Create menu buttons
newBtn = button(800,300,200,50,newGameBtn,newGameBtn)
loadBtn = button(800,360,200,50,loadGameBtn,loadGameBtn)

spawnTimer = 0      # delay counter for spawning enemies       
money = 150         # player's money
playerLives = 10    # player's remaining lives
waves = 0           # current wave number
maxEnemies = 0      # maximum enemies spawned per wave

#Game loop booleans
run = True
runMM = True
runGO = True

#Main Menu
while runMM:

    #Update menu display
    win.blit(mm, (0,0))
    newBtn.draw(win)
    loadBtn.draw(win)
    pygame.display.update()

    #End menu loop if window is closed
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            runMM = False
            run = False
            runGO = False

    #Check for mouse clicks
    if pygame.mouse.get_pressed()[0]:
        mouseState = True
    else:
        mouseState = False

    #Check for button presses
    if prevMouseState != mouseState and mouseState:
        #Start new game
        if newBtn.isPressed():
            runMM = False
        #Read saved data and load from saved state
        elif loadBtn.isPressed():
            saveFile = open(fileDirect + "\SavedState.txt",'r')
            waves = int(saveFile.readline())
            money = int(saveFile.readline())
            health = int(saveFile.readline())
            content = saveFile.readline()
            while content != "":
                content = content.split("\t")
                towers.append(good(int(content[1]),int(content[2]),int(content[0])))
                content = saveFile.readline()
            saveFile.close()

            for tower in towers:
                tower.live = True

            runMM = False

    #Update mouse status
    prevMouseState = mouseState
    
  
attacking = False
addingTower = False

selectedTower = len(towers)

font = pygame.font.SysFont("comicsans", 30, True)
infoFont = pygame.font.SysFont("comicsans", 20, False)

#Add all buttons to the menu
startWaveBtn = button(1040,500,120,40,onWaveBtn,offWaveBtn)
saveBtn = button(1040,540,120,40,onSaveBtn,offWaveBtn)
upgradeBtn = button(1025,220,150,35,onUpgradeBtn,offUpgradeBtn)
buttons.append(button(1055,300,40,40,fireBtn,offBtn))
buttons.append(button(1105,300,40,40,waterBtn,offBtn))
buttons.append(button(1055,350,40,40,grassBtn,offBtn))
buttons.append(button(1105,350,40,40,rockBtn,offBtn))

#Game Loop
while run:
    #Frame delay
    clock.tick(27)

    #End game loop if window is closed
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            runGO = False

    #Check for mouse clicks
    if pygame.mouse.get_pressed()[0]:
        mouseState = True
    else:
        mouseState = False

    #When mouse click is released check for actions
    if not addingTower and prevMouseState != mouseState and not mouseState:

        #Show range of a tower when it is pressed
        for tower in towers:
            if tower.isPressed():
                if tower.selected:
                    selectedTower = len(towers)
                else:
                    selectedTower = towers.index(tower)

        #Start wave if button is pressed
        if startWaveBtn.isPressed() and not attacking:
            waves += 1
            maxEnemies = (1 + waves//4)*5
            startWaveBtn.on = False
            saveBtn.on = False
            attacking = True

        #Save progress if button is pressed
        if saveBtn.isPressed() and not attacking:
            saveFile = open(fileDirect + "\SavedState.txt",'w+')
            saveFile.write(str(waves) + "\n")
            saveFile.write(str(money) + "\n")
            saveFile.write(str(playerLives))
            for tower in towers:
                saveFile.write("\n" + str(tower.id) + "\t" + str(tower.x) + "\t" + str(tower.y))
            saveFile.close()

        #Upgrade tower if button is pressed
        if upgradeBtn.on and upgradeBtn.isPressed():
            oldID = towers[selectedTower].id
            x = towers[selectedTower].x
            y = towers[selectedTower].y
            towers.pop(selectedTower)
            newID = oldID + 1
            towers.append(good(x,y,newID))
            towers[-1].live = True
            money -= towers[-1].cost
            selectedTower = len(towers)
            
            
        #Add a new tower when the button is pressed
        for btn in buttons:
            if btn.on and btn.isPressed():
                addingTower = True
                towers.append(good(pygame.mouse.get_pos()[0] - 40,pygame.mouse.get_pos()[1] - 40,buttons.index(btn)*3))
                money -= towers[-1].cost
                selectedTower = len(towers)-1

    #Turn buy tower buttons on if player has enough money to buy
    for btn in buttons:
        if int(towerStats[buttons.index(btn)*3][4]) <= money:
            btn.on = True

        else:
            btn.on = False

    #Move the new tower to the desired position
    #Blue range display means the location is valid, red means it is invalid
    if addingTower:
        towers[-1].x = pygame.mouse.get_pos()[0] - 40
        towers[-1].y = pygame.mouse.get_pos()[1] - 40
        if towers[-1].isValidLocation(towers):
            towers[-1].rangeColor = (0,128,255)
            if pygame.mouse.get_pressed()[0]:
                addingTower = False
                towers[-1].live = True
        else:
            towers[-1].rangeColor = (255,0,0)

    
    #Run during a wave of enemies       
    if attacking:
        #Add enemies
        if maxEnemies > 0:
            if spawnTimer >= 30:
                spawnEnemy(waves)
                maxEnemies -= 1
                spawnTimer = 0
            else:
                spawnTimer += 1
        else:
            if len(enemies) <= 0:
                attacking = False
                startWaveBtn.on = True
                saveBtn.on = True


        #Move enemies
        for enemy in enemies:
            enemy.move()

        #Get the tower's target and shoot target if in range
        for tower in towers:
            if tower.live:
                tower.target = tower.findEnemy(enemies)
                if tower.shootCount >= tower.speed:
                    if len(enemies) > 1:
                        if enemies[tower.target].inRange(tower):
                            enemies[tower.target].hit(tower)
                            if not enemies[tower.target].live:
                                money += enemies[tower.target].reward
                                enemies.pop(tower.target)
                        tower.shootCount = 0
                    elif len(enemies) == 1:
                        if enemies[0].inRange(tower):
                            enemies[0].hit(tower)
                            if not enemies[0].live:
                                money += enemies[0].reward
                                enemies.pop(0)
                            tower.shootCount = 0
                else:
                    tower.shootCount += 1

        #Remove player's health if enemy reaches the end
        for enemy in enemies:
            if not enemy.live:
                enemies.pop(enemies.index(enemy))
                playerLives -= 1


    #Display info for selected tower
    for tower in towers:
            tower.selected = False

    upgradeBtn.on = False
    if selectedTower != len(towers):
        towers[selectedTower].selected = True
        if(towers[selectedTower].id + 1)%3 != 0:  
            if money >= int(towerStats[towers[selectedTower].id + 1][4]) and not addingTower:
                upgradeBtn.on = True

    if playerLives <= 0:
        run = False
        

    #Update display
    redrawGameWindow()

    #Update mouse status
    prevMouseState = mouseState

while runGO:
    win.blit(go, (0,0))
    goText = font.render("Waves Survived: " + str(waves-1), 1, (255,0,0))
    win.blit(goText,(500,300))
    pygame.display.update()
    
    #End game loop if window is closed
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            runGO = False
   

#End program
pygame.quit()
