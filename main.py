import pygame
import random
import time
import os
#init font with pygame
pygame.font.init()
# making pygame windows
WIDTH,HEIGHT = 700,750
WIN = pygame.display.set_mode((HEIGHT,WIDTH))
pygame.display.set_caption('spaceShip shooters online multiplayer')
#load images
red_space_ship= pygame.image.load(os.path.join('assets','pixel_ship_red_small.png'))
blue_space_ship = pygame.image.load(os.path.join('assets','pixel_ship_blue_small.png'))
green_space_ship = pygame.image.load(os.path.join('assets','pixel_ship_green_small.png'))
#main player
yellow_space_ship = pygame.image.load(os.path.join('assets','pixel_ship_yellow.png'))
#load lazers
laser_blue = pygame.image.load(os.path.join('assets','pixel_laser_blue.png'))
laser_green = pygame.image.load(os.path.join('assets','pixel_laser_green.png'))
laser_yellow = pygame.image.load(os.path.join('assets','pixel_laser_yellow.png'))
laser_red = pygame.image.load(os.path.join('assets','pixel_laser_red.png'))
# background
BG = pygame.transform.scale(pygame.image.load(os.path.join('assets','background-black.png')),(HEIGHT,WIDTH))
#class lazers
class Laser:
    def __init__(self,x,y,img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self,window):
        window.blit(self.img,(self.x,self.y))
    def move(self,vel):
        self.y +=vel
    def collision(self,obj):
        return collide(obj,self)
    def off_screen(self,height):
        return not self.y >= height and self.y <= 0
    def Check_Laser_Collide(self,enemylasers,playerLasers):
        for eneLaser in enemylasers:
            for playerlas in playerLasers:
                if collide(eneLaser,playerlas):
                    playerLasers.remove(playerlas)
                    enemylasers.remove(eneLaser)

def collide(obj1,obj2):
    offset_y = obj2.y - obj1.y
    offset_x = obj2.x - obj1.x
    return obj2.mask.overlap(obj2.mask,(offset_y,offset_x)) !=None
#ship class for basic ship to inheritance from another class ship classs ie enemy ship or player ships
class Ship:
    def __init__(self,x,y,helath=100):
        self.x = x
        self.y = y
        self.COOLDOWN = 30
        self.health = helath
        self.ship_img =None
        self.laser_img = None
        self.lasers = []
        self.cool_down_timer_laser = 0
    def draw(self,window):
        window.blit(self.ship_img,(self.x,self.y))
        for lazer in self.lasers:
            lazer.draw(window)
    def move_laser(self,vel,obj):
        self.coolDown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health-=10
                print(obj.health)
                self.lasers.remove(laser)
    def get_height(self):
        return self.ship_img.get_height()
    def get_width(self):
        return self.ship_img.get_width()
    def coolDown(self):
        if self.cool_down_timer_laser >= self.COOLDOWN:
            self.cool_down_timer_laser =0
        elif self.cool_down_timer_laser >0 :
            self.cool_down_timer_laser+=1
    def shoot(self):
        if self.cool_down_timer_laser == 0:
            laser = Laser(self.x,self.y,self.laser_img)
            self.lasers.append(laser)
            self.cool_down_timer_laser+=1



class Player(Ship):
    def __init__(self,x,y,helath=100):
        super().__init__(x,y,helath)
        self.ship_img=yellow_space_ship
        self.laser_img=laser_yellow
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = helath

    def move_laser(self, vel, objs):
        self.coolDown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)
    def draw(self,window):
        super().draw(window)
        self.healthBar(window)
    def healthBar(self,window):
        pygame.draw.rect(window,(255,0,0),(self.x,self.y+self.ship_img.get_height()+10,self.ship_img.get_width(),10))
        pygame.draw.rect(window, (0, 255, 0),(self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width()*(self.health/self.max_health), 10))




class Enemy(Ship):
    def __init__(self,x,y,color,health=100):
        COLOR_MAP = {'blue': (blue_space_ship, laser_blue),
                     'green': (green_space_ship, laser_green),
                     'red': (red_space_ship, laser_red)}
        super().__init__(x,y,health)
        self.ship_img,self.laser_img= COLOR_MAP.get(color)
        self.x =x
        self.y=y
        # self.vel = velocity
        self.mask = pygame.mask.from_surface(self.ship_img)
    def move(self,vel):
        self.y+=vel


    def shoot(self):
        if self.cool_down_timer_laser == 0:
            laser = Laser(self.x-15,self.y,self.laser_img)
            self.lasers.append(laser)
            self.cool_down_timer_laser+=1

# main loop
def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    enemies=[]
    wave=0
    enemy_vel =1
    lost = False
    laser_vel = 8
    lost_count =0
    player =Player(300,500)
    player_vel = 5
    main_font = pygame.font.SysFont("comicsans",50)
    lost_font = pygame.font.SysFont("comicsans", 100)
    clock = pygame.time.Clock() # make a clock that makes sure program runs at 60 fps

    # draws everything on screen again whenever called
    def redraw_window():
        WIN.blit(BG,(0,0))

        lives_label = main_font.render(f'lives : {lives}',1,(255,255,255))
        level_label = main_font.render(f'level : {level}', 1, (255, 255, 255))
        for enemy in enemies:
            enemy.draw(WIN)
        if lost:
            lost_label = lost_font.render('you lost !!!',1,(255,255,255))
            WIN.blit(lost_label, (WIDTH/2-lost_label.get_width()/2,HEIGHT/2-50))
        player.draw(WIN)
        WIN.blit(lives_label,(10,10))#x,y or width,height
        WIN.blit(level_label,(WIDTH-level_label.get_width()-5,10))
        pygame.display.update()
    while run:
        clock.tick(FPS)
        redraw_window()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        if player.health <=0 or lives<=0:
            lost =True
            lost_count += 1
        if lost:
            if lost_count > FPS * 6:
                run=False
            else:
                continue
        if len(enemies) == 0:
            level+=1
            wave+=5
            for i in range(wave):
                enemy = Enemy(random.randrange(70,WIDTH-100),random.randrange(-1000,-100),random.choice(['red','green','blue']),random.randrange(50,150))
                enemies.append(enemy)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x-player_vel > 0:
            player.x -=player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width()-50< WIDTH:
            player.x +=player_vel
        if keys[pygame.K_w] and player.y-player_vel >0:
            player.y -=player_vel
        if keys[pygame.K_s] and player.y+player.get_height()+50 +20+player_vel < HEIGHT:
            player.y +=player_vel
        if keys[pygame.K_SPACE] :
            player.shoot()


        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_laser(laser_vel,player)
            if random.randrange(0,2*FPS) ==1:
                enemy.shoot()
            if collide(enemy,player):
                player.health -=10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives-=1
                enemies.remove(enemy)
            for las in enemy.lasers:
                las.Check_Laser_Collide(enemy.lasers,player.lasers)

        player.move_laser(-laser_vel,enemies)

def main_menu():
    font = pygame.font.SysFont('comicsans',60)
    run = True
    while run:
        WIN.blit(BG,(0,0))
        title_label = font.render('press mouse button to start',1,(255,255,255))
        WIN.blit(title_label,(WIDTH/2-title_label.get_width()/2,350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()

main_menu()