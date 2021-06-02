import pygame
from pygame.locals import *
from pygame import mixer

pygame.mixer.pre_init(44100, -16, 2, 512) #preset
mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 60
# velikost okna
screen_width = 1000
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# nazevhry
pygame.display.set_caption("RAPtilián demo")

# nacteni obrazků
banner_img = pygame.image.load('img/banner.png')
pozadi_img = pygame.image.load('img/pozadi.jpg')
slunce_img = pygame.image.load('img/slunce.png')
postava_img = pygame.image.load('img/postava.png')
restart_img = pygame.image.load('img/restart_button.png')
start_img = pygame.image.load('img/start_button.png')
exit_img = pygame.image.load('img/exit_button.png')
pervitin_img = pygame.image.load('img/pervitin.png')
foscopama_img = pygame.image.load('img/foscopalma.png')
#nacteni zvuků
pygame.mixer.music.load('sound/hudba.wav')
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(50,0.0,5000)
bitcoin_fx = pygame.mixer.Sound('sound/bitcoin.mp3')
bitcoin_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound('sound/jump.mp3')
jump_fx.set_volume(0.2)
game_over_fx = pygame.mixer.Sound('sound/game_over.mp3')
game_over_fx.set_volume(0.5)



# promenne pro hru
tile_size = 50
game_over = 0
main_menu = True
level = 0
max_levels = 3
score = 0

#fonty
font = pygame.font.SysFont('bahnschrift', 50)
font_score = pygame.font.SysFont('Bauhuas 93', 30)

#barvy
white = (255,255,255)
red = (255,0,0)


class World():
    def __init__(self, data):
        self.tile_list = []
        # nacteni obrazku
        zed_img = pygame.image.load('img/zed.png')
        zed2_img = pygame.image.load('img/zed2.png')
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(zed_img, (
                    tile_size, tile_size))  # prevedeni obrazku na spravnou velikost podle velikosti mrizky
                    img_rect = img.get_rect()  # prevedeni img na ctverec
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(zed2_img, (tile_size, tile_size))
                    img_rect = img.get_rect()  # prevedeni img na ctverec
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    pervitin = Enemy(col_count * tile_size, row_count * tile_size + 15,pervitin_img)
                    pervitin_group.add(pervitin)
                if tile == 4:
                    kyselina = Kyselina(col_count * tile_size, row_count * tile_size)
                    kyselina_group.add(kyselina)
                if tile == 5:
                    exit = Exit(col_count * tile_size,row_count * tile_size)
                    exit_group.add(exit)
                if tile == 6:
                    bitcoin = Bitcoin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
                    bitcoin_group.add(bitcoin)
                if tile == 7:
                    foscopalma = Enemy(col_count * tile_size, row_count * tile_size -50, foscopama_img)
                    foscopalma_group.add(foscopalma)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            #pygame.draw.rect(screen, (255, 255, 255), tile[1], 2) #pomocný ctverec kolem bloků pro reseni kolizi


class Player():
    def __init__(self, x, y):
        self.reset(x,y)


    def update(self,game_over):

        # reakce na klavesy
        dx = 0  # deltax
        dy = 0  # deltay
        walk_cooldown = 5

        if game_over == 0:
            key = pygame.key.get_pressed()
            if key[pygame.K_LEFT]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 5
                self.counter += 1
                self.direction = 1
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]
            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                jump_fx.play()
                self.vel_y = -15
                self.jumped = True
            if key[pygame.K_SPACE] == False:  # po provedeni skoku se znovu prepne na False
                self.jumped = False

            # zpracování animace pohybu

            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1

                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]
            # gravitace
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            # kontrola kolizí
            self.in_air = True
            for tile in world.tile_list:
                # směr x
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.widt, self.height):
                    dx = 0
                # směr y
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.widt, self.height):
                    # směr y nahoru (skakni)
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    # směr y dolu (padani)
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False
            # kolize s enemies
            if pygame.sprite.spritecollide(self,pervitin_group, False):
                game_over = -1
                game_over_fx.play()
            if pygame.sprite.spritecollide(self, foscopalma_group, False):
                game_over = -1
                game_over_fx.play()
            # kolize s kyselinou
            if pygame.sprite.spritecollide(self, kyselina_group, False):
                game_over = -1
                game_over_fx.play()
            # kontrola kolize s exit
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1



            #pohyb
            self.rect.x += dx
            self.rect.y += dy





        #změna animace při smrti
        elif game_over == -1:
            self.image = self.dead_image
            draw_text('Zkus to znovu!', font, red,(screen_width //2) -150, screen_height -550)
            if self.rect.y > 100:
                self.rect.y -= 5

        screen.blit(self.image, self.rect)  # nakresleni hrace
        #pygame.draw.rect(screen, (255, 255, 255), self.rect, 2) #pomocny ctverec kolem hrace pro reseni kolizi
        return game_over

    def reset(self,x,y):
        self.images_right = []  # animace obrazky
        self.images_left = []  # animace obrazky
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img_right = pygame.image.load(f"img/postava{num}.png")
            img_right = pygame.transform.scale(img_right, (35, 80))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load('img/postava_dead.png')
        self.dead_image = pygame.transform.scale(self.dead_image, (50, 80))
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.widt = self.image.get_width()
        self.height = self.image.get_height()
        # skok
        self.vel_y = 0
        self.jumped = False
        self.in_air = True

        self.direction = 0

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, obrazek):
        pygame.sprite.Sprite.__init__(self)
        self.image = obrazek
        #self.image = pygame.transform.scale(self.image, (50, 80))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction =1
        self.move_counter =0
    def update(self, vzdalenost):
        #pohyb enemy
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter)>vzdalenost: #abs = absloutní hodnota
            self.move_direction *= -1
            self.move_counter *= -1

class Kyselina(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/kyselina.png')
        self.image = pygame.transform.scale(img,(tile_size,tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Bitcoin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/bitcoin.png')
        self.image = pygame.transform.scale(img,(tile_size // 2, tile_size // 2 ))
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)


class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/exit.png')
        #self.image = pygame.transform.scale(img,(tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Button():
    def __init__(self,x,y,image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False
    def draw(self):
        action = False
        pos = pygame.mouse.get_pos() #pozice mysi

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] ==1 and self.clicked == False:
                action = True
                self.clicked = True

            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False   #restart stavu


        screen.blit(self.image, self.rect)

        return action



#založení instancí tříd
player = Player(100, screen_height - 150)
pervitin_group = pygame.sprite.Group()
kyselina_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
bitcoin_group = pygame.sprite.Group()
foscopalma_group = pygame.sprite.Group()

from lvl import levely
world = World(levely[level]) #nacteni dat pro level a vytvoření světa
#tlačítka
restart_button = Button(screen_width //2 -75, screen_height // 2 -150, restart_img)
start_button = Button(screen_width // 2 -300, screen_height //2 - 75, start_img)
exit_button = Button(screen_width // 2 + 150, screen_height //2 - 75, exit_img)


# funkce pro nakresleni pomocne mrizky
def draw_grid():
    for line in range(0, 12):
        pygame.draw.line(screen, (255, 255, 255), (0, line * tile_size), (screen_width, line * tile_size))
        pygame.draw.line(screen, (255, 255, 255), (line * tile_size, 0), (line * tile_size, screen_height))

# funkce pro vytvoreni noveho levelu
def reset_level(level):
    player.reset(100,screen_height - 150)
    pervitin_group.empty()
    kyselina_group.empty()
    exit_group.empty()
    bitcoin_group.empty()
    foscopalma_group.empty()
    world = World(levely[level])
    return world
# funkce pro vykresleni textu
def draw_text(text,font,text_col,x,y):
    img = font.render(text, True, text_col)
    screen.blit(img,(x,y))

# hlavni smycka Hry
run = True
while run:
    clock.tick(fps)

    screen.blit(pozadi_img, (0, 0))
    #screen.blit(slunce_img,(200,200))

    if main_menu == True: #vykresleni menu
        screen.blit(banner_img,(200,10))
        postava_img = pygame.transform.scale(postava_img, (313, 422))
        screen.blit(postava_img, (313, 100))
        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = False
    else:
        # draw_grid() #pomocná mřížka

        world.draw()
        if game_over ==0:
            pervitin_group.update(50) #pohyb enemies
            foscopalma_group.update(15)
            if pygame.sprite.spritecollide(player, bitcoin_group, True): #bool True zajistí že bitcoin po kolizi zmizí, takze to vypada jako by byl sebrán
                score +=1
                bitcoin_fx.play()
            draw_text(str(score) + ' BTC',font_score,white,tile_size + 50,10)

        exit_group.draw(screen)
        bitcoin_group.draw(screen)
        pervitin_group.draw(screen)
        foscopalma_group.draw(screen)
        kyselina_group.draw(screen)





        game_over = player.update(game_over)

        if game_over == -1: #pokud je hrac mrtvy
            if restart_button.draw(): #nakresli pouze pokud vraci true
                world = reset_level(level)
                game_over =0
                score = 0

        if game_over == 1: #pokud hrac vstoupil na exit
            level += 1
            if level <= max_levels:
                world = reset_level(level)
                game_over = 0
            else:
                draw_text('KONEC HRY, VYHRÁL JSI!', font, red,(screen_width //2) -300, screen_height -550)
                if restart_button.draw():
                    level = 0
                    world = reset_level(level)
                    game_over = 0



    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()

pygame.quit()
