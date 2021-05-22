import socket
import json
import threading
import time
import pygame
import os
WIDTH, HEIGHT = 700, 700
pygame.font.init()
BG = pygame.transform.scale(pygame.image.load(os.path.join('assets','background-black.png')),(HEIGHT,WIDTH))
laser_img = pygame.image.load(os.path.join('assets', 'pixel_laser_blue.png'))
laser_rotated = pygame.image.load(os.path.join('assets', 'pixel_laser_blue_rotated.png'))
ship_img_up = pygame.image.load(os.path.join('assets','pixel_ship_yellow.png'))
ship_img_down = pygame.image.load(os.path.join('assets','pixel_ship_yellow_down.png'))
ship_img_left = pygame.image.load(os.path.join('assets','pixel_ship_yellow_left.png'))
ship_img_right = pygame.image.load(os.path.join('assets','pixel_ship_yellow_right.png'))


class network:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.client = socket.socket()
        self.client.connect((self.host, self.port))
        self.shoot = False
    def send_power_up(self,powerup):
        speed,damage,shield,burstfire = powerup[0],powerup[1],powerup[2],powerup[3]
        self.client.send(f'powerup:{speed},{damage},{burstfire},{shield}'.encode('utf-8'))
    def send_player_x_y(self, coordinates, mortarAngle, health):
        x, y = coordinates[0], coordinates[1]
        # print(f'{x},{y},{mortarAngle},{self.shoot},{health}')
        self.client.send(f'{x},{y},{mortarAngle},{self.shoot},{health}'.encode('utf-8'))
        self.shoot = False

    def send_message(self, message):
        self.client.send(message.encode('utf-8'))

    def shooting(self):
        self.shoot = True

    def recieve_coordinates(self):
        recieve_from_server = self.client.recv(4026).decode('utf-8')
        # print(recieve_from_server)
        self.x, self.y, mortarAngle, shoot, health = recieve_from_server.split(',')
        return (int(self.x), int(self.y), mortarAngle, shoot, int(health))
        # data = json.loads(recieve_from_server)
        # coordinates =[data.get('x'),data.get('y')]
        # print(self.recieve_from_server)

    def receive_message(self):
        message = self.client.recv(4026).decode('utf-8')
        print(message)
        message = message.replace('powerup:','')
        speed,damage,shield,burstfire = message.split(',')
        return speed,damage,shield,burstfire
    def recieve(self):
        msg = self.client.recv(4026).decode('utf-8')
        return msg
WIN = pygame.display.set_mode((HEIGHT, WIDTH))
pygame.display.set_caption('test')


class Laser:
    def __init__(self, x, y, rotation, img, rotatedImg):
        self.rotation = rotation
        self.x = x
        self.y = y
        self.img = img
        self.rotatedImg = rotatedImg
        self.mask = pygame.mask.from_surface(self.img)
        self.rotatedMask = pygame.mask.from_surface(self.rotatedImg)

    def draw(self, window):
        if self.rotation == 'up' or self.rotation == 'down':
            window.blit(self.img, (self.x, self.y))
        elif self.rotation == 'left' or self.rotation == 'right':
            window.blit(self.rotatedImg, (self.x, self.y))

    def move(self, vel):
        if self.rotation == 'left':
            self.x -= vel
        if self.rotation == 'right':
            self.x += vel
        if self.rotation == 'up':
            self.y -= vel
        if self.rotation == 'down':
            self.y += vel

    def collision(self, obj):
        return collide(obj, self)

    def off_screen(self, height):
        return not self.y >= height and self.y <= 0

    def Check_Laser_Collide(self, enemylasers, playerLasers):
        for eneLaser in enemylasers:
            for playerlas in playerLasers:
                if collide(eneLaser, playerlas):
                    playerLasers.remove(playerlas)
                    enemylasers.remove(eneLaser)


def collide(obj1, obj2):
    offset_y = obj2.y - obj1.y
    offset_x = obj2.x - obj1.x
    return obj2.mask.overlap(obj1.mask, (offset_y, offset_x)) != None


class Player:
    def __init__(self, x, y, rotate='up', health=100,img=None):
        self.x = x
        self.health = health
        self.y = y
        self.mortarAngle = rotate
        self.laser_img = None
        self.laser_objs = []
        self.cool_down_timer_laser = 0
        self.COOLDOWN = 30
        self.ship = img
        self.damage = 10
        self.player_vel = 5
        '''
        powerUPS
        '''
        self.burstfire = False
        self.damagefire = False
        self.shield = False
        self.shieldHP = 0
        self.speed = False
        '''
        powerUPS
        '''

        self.ship_down = ship_img_down
        self.ship_left = ship_img_left
        self.ship_right = ship_img_right
        self.mask = pygame.mask.from_surface(self.ship)
    def draw(self, window):
        if self.mortarAngle=='up':
            window.blit(self.ship,(self.x, self.y))
        if self.mortarAngle == 'down':
           window.blit(self.ship_down, (self.x, self.y))
        if self.mortarAngle == 'left':
            window.blit(self.ship_left, (self.x, self.y))
        if self.mortarAngle == 'right':
            window.blit(self.ship_right, (self.x, self.y))

        # if self.mortarAngle == 'up':
        #     self.mortar = pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.get_height()+5, 5, 10))
        # if self.mortarAngle == 'down':
        #     self.mortar = pygame.draw.rect(window, (0, 255, 0), (self.x, self.y+self.get_height()-5, 5, 10))
        # if self.mortarAngle == 'right':
        #     self.mortar = pygame.draw.rect(window, (0, 255, 0), (self.x + 35, self.y + 10, 40, 20))
        # if self.mortarAngle == 'left':
        #     self.mortar = pygame.draw.rect(window, (0, 255, 0), (self.x - 25, self.y + 10, 30, 20))
        for lazer in self.laser_objs:
            lazer.draw(window)

    def coolDown(self):
        if self.cool_down_timer_laser >= self.COOLDOWN:
            self.cool_down_timer_laser = 0
        elif self.cool_down_timer_laser > 0:
            self.cool_down_timer_laser += 1

    def shoot(self):
        if self.cool_down_timer_laser == 0:
            print('spawning_laser')
            laser = Laser(self.x, self.y, self.mortarAngle, laser_img, laser_rotated)
            self.laser_objs.append(laser)
            self.cool_down_timer_laser += 1

    def get_height(self):
        return self.ship.get_height()

    def get_width(self):
        return self.ship.get_width()

    def move_laser(self, vel, enemy):
        self.coolDown()
        for laser in self.laser_objs:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.laser_objs.remove(laser)
            if laser.collision(enemy):
                if enemy.shield == True:
                    if not enemy.shieldHP <= 0:
                        enemy.shieldHP -= self.damage
                    else:
                        enemy.health -=self.damage
                else:
                    enemy.health -= self.damage
                print(enemy.health)
                self.laser_objs.remove(laser)
            # elif laser.collision(obj):
            #     obj.health -= 10
            #     print(obj.health)
            #     self.lasers.remove(laser)
    def burst_fire(self):
        self.COOLDOWN = self.COOLDOWN//2
    def speeddd(self):
        self.player_vel = self.player_vel * 2
    def SHIELD(self):
        self.shield = True
        self.shieldHP = 50
    def DAMAGE(self):
        self.damage = self.damage*2
# client = network()
message = ''
def main():
    main_font = pygame.font.SysFont("comicsans",20)
    lost_font = pygame.font.SysFont('comicsans', 50)
    win_font = pygame.font.SysFont('comicsans', 50)
    FPS = 100
    player = Player(300, 300,img=ship_img_up)
    clock = pygame.time.Clock()
    client = network()
    threadrun=True
    player2 = Player(250, 350,img=ship_img_up)
    run = True
    count = 0
    lost_counter = 0
    lost = False
    win = False
    power_up_menu(player,client,player2)
    print('power_up_menu finished')
    message = client.recieve()
    def recieve():
        while True:
            try:
                client.send_player_x_y((player.x, player.y), player.mortarAngle, player.health)
                x, y, mortarAngle, shoot, health = client.recieve_coordinates()
                print(x,y,mortarAngle,shoot, health )
                player2.x = x
                player2.y = y
                player2.mortarAngle = mortarAngle
                player2.health = health
                if shoot == 'True':
                    player2.shoot()
                draw_everythong()
                if lost or win:
                    break
            except Exception as err:
                print(err)
                pass
    def draw_everythong():
        WIN.blit(BG,(0,0))
        player.draw(WIN)
        # WIN.blit(laser_img,(10,10))
        angle_label = main_font.render(f'mortarAngle : {player.mortarAngle}',1,(255,255,255))
        health_label = main_font.render(f'health :{player.health}',1,(255,255,255))
        shield_label = main_font.render(f'shield :{player.shieldHP}',1,(255,255,255))
        WIN.blit(angle_label,(10,10))
        WIN.blit(health_label, (WIDTH-10-health_label.get_width(), 10))
        WIN.blit(shield_label, (WIDTH - 20 - shield_label.get_width(), HEIGHT-20-shield_label.get_height()))
        print(lost,win)
        if lost:
            lost_label = lost_font.render('you lost !!',1,(255,255,255))
            WIN.blit(lost_label,(WIDTH/2-lost_label.get_width()/2,HEIGHT-100))
        if win:
            win_label = win_font.render('you won !!', 1, (255,255,255))
            WIN.blit(win_label, (WIDTH / 2 - win_label.get_width() / 2, HEIGHT - 100))
        player2.draw(WIN)
        pygame.display.update()

    if player.damagefire == True:
        player.DAMAGE()
    if player.shield == True:
        player.SHIELD()
    if player.burstfire == True:
        player.burst_fire()
    if player.speed == True:
        player.speeddd()

    if player2.damagefire == True or player2.damagefire == 'True':
        player2.DAMAGE()
    if player2.shield == True or player2.shield == 'True':
        player2.SHIELD()
    if player2.burstfire == True or player2.burstfire == 'True':
        player2.burst_fire()
        print(player2.COOLDOWN)
    if player2.speed == True or player2.speed == 'True':
        player2.speeddd()
    while run:
        clock.tick(FPS)
        print(lost,win)
        if lost or win:
            draw_everythong()
            if lost_counter > FPS * 6:
                run=False
            else:
                lost_counter += 1
                continue
        if player.health <=0:
            lost = True
        if player2.health <=0:
            win = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if player.burstfire == False:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_z:
                        player.shoot()
                        print('shooting')
                        client.shooting()

        keys = pygame.key.get_pressed()
        if player.burstfire:
            if keys[pygame.K_z]:
                player.shoot()
                print('shooting')
                client.shooting()
        if keys[pygame.K_a]:
            player.x -= player.player_vel
        if keys[pygame.K_d]:
            player.x += player.player_vel
        if keys[pygame.K_s]:
            player.y += player.player_vel
        if keys[pygame.K_w]:
            player.y -= player.player_vel
        # if keys[pygame.K_SPACE]:
        #     player.shoot()

        if keys[pygame.K_LEFT]:
            player.mortarAngle = 'left'
        if keys[pygame.K_RIGHT]:
            player.mortarAngle = 'right'
        if keys[pygame.K_DOWN]:
            player.mortarAngle = 'down'
        if keys[pygame.K_UP]:
            player.mortarAngle = 'up'


            # player.move_laser(5)

        if message == '!READY!':
            try:
                # client.send_laser_info(player.mortarAngle)
                # x, y, mortarAngle, shoot, health = client.recieve_coordinates()
                # print(coord)
                # player2.x = x
                # player2.y = y
                # player2.mortarAngle = mortarAngle
                # player2.health = health
                # if shoot == 'True':
                #     player2.shoot()
                if threadrun:
                    print('thread started')
                    thread = threading.Thread(target=recieve)
                    thread.start()
                    threadrun = False
                if len(player.laser_objs) != 0:
                    player.move_laser(5, player2)
                if len(player2.laser_objs) != 0:
                    player2.move_laser(5, player)

            except Exception as err:
                print(err)
                continue
        count+=1


def power_up_menu(player,client,player2):
    font = pygame.font.SysFont('comicsans',20)
    run_menu = True

    def power():
        try:
            message = client.receive_message()
            player2.speed, player2.damagefire , player2.shield,player2.burstfire = message[0], message[1], message[2],message[3]
            print(player2.speed, player2.damagefire , player2.shield,player2.burstfire)
            print('done')

        except Exception as err:
            print(err)
    while run_menu:
        WIN.blit(BG,(0,0))
        title_label = font.render('choose power up 1 for speed  2 for damage  3 for  shield  4 for burst fire',1,(255,255,255))
        WIN.blit(title_label,(WIDTH/2-title_label.get_width()/2,350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run_menu = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    print('speed')
                    player.speed = True
                    run_menu = False
                elif event.key == pygame.K_2:
                    print('damage')
                    player.damagefire = True
                    run_menu = False
                elif event.key == pygame.K_3:
                    print('shield')
                    player.shield = True
                    run_menu = False
                elif event.key == pygame.K_4:
                    print('burst_fire')
                    player.burstfire = True
                    run_menu = False
        if player.speed == True or player.damagefire == True or player.burstfire== True or player.shield== True:
            client.send_power_up((player.speed,player.damagefire,player.burstfire,player.shield))
            power()
main()