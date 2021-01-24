import sys
from ctypes import pydll

import pygame

from menu import Menu

pygame.init()
########CONST##########
ITEMS = ['новая игрa', 'загрузить', 'рекорды', 'выход']
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

MAIN_BACKGROUND = 'source/level01/back_small.png'
DEATH_BACKGROUND = 'source/default/death.png'

MYCAPTION="-----------------"
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
CRIMSON = (220, 20, 60)
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
GRAVITY_START = 1
GRAVITY_ACCELERATION = 0.35
SPEED_RIGHT=6
SPEED_LEFT=-SPEED_RIGHT
PLAYER_UNDEAD_TIME=60
PLAYER_LIFE_COUNT = 3


##CHECK_POINT##
CHECK_POINT_WIDTH = 50
CHECK_POINT_HEIGHT = 50
##CAMERA##
CAMERA_RIGHT_BOUND = 500
CAMERA_LEFT_BOUND = 300
CAMERA_TOP_BOUND = 100
CAMERA_BOTTOM_BOUND = 500

##LIFE&DEATH##
DOWN_LIMIT_LIFE = -1500
DEFAULT_RESTART_POINT = 200, 200
#######################





class Dummy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([PLAYER_WIDTH, PLAYER_HEIGHT])
        self.image = pygame.image.load('objects/actor_right.png')
        self.rect = self.image.get_rect()
        self.change_x = 0
        self.change_y = 0
        self.level = None
        self.alive = True
        self.forward = 1


    def update(self):    #!!!
        self.calc_grav() #расчет гравитации
        self.rect.x += self.change_x #получение нового положения по X

        #раcчет коллизий (столкновений)
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False) #получение листа объектов(спрайтов), которые сталкиваются с игроком при движении по X
        for block in block_hit_list: #по каждому объекту в листе
            if self.change_x > 0: #если движение вправо
                self.rect.right = block.rect.left #то правая граница игрока останавливается у левой границе объекта
            elif self.change_x < 0: #если движение влево
                self.rect.left = block.rect.right #

        self.rect.y += self.change_y #получение нового положения по Y

        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False) #получение листа объектов(спрайтов), которые сталкиваются с игроком при движении по Y
        for block in block_hit_list: #по каждому объекту в листе
            if self.change_y > 0: #если движение вниз
                self.rect.bottom = block.rect.top #то упирается в верхнюю границу объекта
            elif self.change_y < 0: #если движение вверх
                self.rect.top = block.rect.bottom #то упирается в нижнюю границу объекта

            self.change_y = 0 #движение по Y останавливается

            if isinstance(block, MovingPlatform): #если объект еще и является ДвижущейсяПлатформой
                self.rect.x += block.change_x #тогда двигаемся вместе с платформой по Х
                                              #можно дописать движение по Y, если в классе MovingPlatform прописать change_y

        if self.level.world_shift_y < DOWN_LIMIT_LIFE: #если упадет ниже - умрет
            self.alive = False

        self.collision_with_restart_point() #заглушка для рассчета коллизий с чекпоинтами
        self.collision_with_damage() #заглушка для коллизий с дамагом


    def collision_with_restart_point(self):
        pass

    def collision_with_damage(self):
        pass

    def calc_grav(self):
        #Считаем гравитацию
        if self.change_y == 0: #если вверх/вниз не движемся
            self.change_y = GRAVITY_START #падаем на GRAVITY_START
        else:
            self.change_y += GRAVITY_ACCELERATION #иначе ускоряемся на GRAVITY_ACCELERATION

    def jump(self):
        # костыль
        self.rect.y += 2 # двигаемся вниз на 2 пикселя для проверки, есть ли от чего отталкиваться
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False) #собираем в лист то, что под ногами
        self.rect.y -= 2 # возвращаем на место игрока

        # если под ногами что-то есть и координаты нижней грани игрока больше высоты экрана (т.е. нижняя грань игрока выше нижней границы игрового поля)
        if len(platform_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.change_y = -10


    def go_left(self):
        self.change_x = SPEED_LEFT
        self.forward = -1

    def go_right(self):
        self.change_x = SPEED_RIGHT
        self.forward = 1

    def stop(self):
        self.change_x = 0

class Player(Dummy):
    def __init__(self):
        super().__init__()
        self.lifesize = 100
        self.undead = False
        self.undead_time = PLAYER_UNDEAD_TIME

    def collision_with_restart_point(self):
        block_hit_list = pygame.sprite.spritecollide(self, self.level.list_restart_point, False)  # лист чекпоинтов по колизиям
        if len(block_hit_list) > 0:  # если с кем-то есть столкновения
            for block in self.level.list_restart_point:
                block.image=pygame.image.load('objects/small_platform.png')  # то все чекпоинты становятся белыми
        for block in block_hit_list:  # и только активированный - красный
            self.level.active_restart_point = block.rect.x - self.level.world_shift_x, block.rect.y - self.level.world_shift_y  # активируем новый чекпоинт через запись x и y
            block.image.fill(CRIMSON)

    def get_damage(self, damage):
        if not self.undead:
            self.lifesize -= damage
            self.rect.x -= self.forward * 50
            self.rect.y -= 50
            self.undead = True
            if self.lifesize <= 0:
                self.alive = False


    def collision_with_damage(self):
        block_hit_list = pygame.sprite.spritecollide(self, self.level.enemy_list, False)
        for enemy in block_hit_list:
            self.get_damage(enemy.set_damage())

    def update(self):
        super().update()
        if self.undead:
            self.undead_time -= 1
            if self.undead_time <= 0:
                self.undead = False
                self.undead_time = PLAYER_UNDEAD_TIME


class Enemy(Dummy):
    def __init__(self):
        super().__init__()
        self.life_size=100
        self.damage = 10
        self.image = pygame.Surface([30, 30])
        self.image = pygame.image.load('objects/mine.png')
        self.rect = self.image.get_rect()
        self.border_patrol_right = -1
        self.border_patrol_left = -1

    def get_damage(self, damage):
        self.life_size -= damage
        if self.life_size <= 0:
            self.alive = False

    def set_damage(self):
        return self.damage

    def update(self):
        super().update()
        self.go_patrol()

    def go_patrol(self):
        if -1 < self.border_patrol_right < self.border_patrol_left and self.border_patrol_left > -1:
            self.rect.x += self.change_x
        posOtnX = self.rect.x - self.level.world_shift_x  # т.к. мир движется через координаты экрана, находим относительную координату по X
        # меняем направление движения
        if posOtnX < self.border_patrol_left or posOtnX > self.border_patrol_right:
            self.change_x *= -1


class EnemyShooter(Enemy):
    def __init__(self):
        super().__init__()
        self.damage = 0
        self.image = pygame.Surface([70, 30])
        self.image = pygame.image.load('objects/mine.png')
        self.rect = self.image.get_rect()

    def update(self):
        super().update()

class Platform(pygame.sprite.Sprite):

    def __init__(self, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image = pygame.image.load('objects/big_platform.png')
        self.rect = self.image.get_rect()


class MovingPlatform(Platform):
    #ДвигающаясяПлатформа
    change_x = 0
    change_y = 0

    boundary_top = 0
    boundary_bottom = 0
    boundary_left = 0
    boundary_right = 0

    player = None

    level = None

    def update(self):
        self.rect.x += self.change_x

        hit = pygame.sprite.collide_rect(self, self.player) #проверяем, есть ли коллизия с игроком
        if hit:
            if self.change_x < 0: #если платформа движемся вправо
                self.player.rect.right = self.rect.left #сдвигаем игрока вправо
            else:
                # или наоборот
                self.player.rect.left = self.rect.right

        self.rect.y += self.change_y
        # тоже самое для верх/вниз
        hit = pygame.sprite.collide_rect(self, self.player)
        if hit:
            if self.change_y < 0:
                self.player.rect.bottom = self.rect.top
            else:
                self.player.rect.top = self.rect.bottom


        posOtnY = self.rect.y - self.level.world_shift_y  # т.к. мир движется через координаты экрана, находим относительную координату по Y
        #изменение направления движения, если платформа вышла за  верхнюю или нижнюю границы (boundary)
        if posOtnY > self.boundary_bottom or posOtnY < self.boundary_top:
            self.change_y *= -1

        posOtnX = self.rect.x - self.level.world_shift_x #т.к. мир движется через координаты экрана, находим относительную координату по X
        #и также меняем направление движения
        if posOtnX < self.boundary_left or posOtnX > self.boundary_right:
            self.change_x *= -1


class AnotherMovingPlatform(MovingPlatform):

    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pygame.image.load('objects/medium_platform.png')


class CheckPoint(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([CHECK_POINT_WIDTH, CHECK_POINT_HEIGHT])
        self.image = pygame.image.load('objects/small_platform.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Player_UI(): #интерфейс в игре
    def __init__(self, surf):
        self.font_name = pygame.font.match_font('arial')
        self.surf = surf

    def draw_text(self, text, size, x, y):
        if text is None:
            text1 = "None"
        else:
            text1 = str(text)
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text1, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.surf.blit(text_surface, text_rect)

class Level(object): #базовый класс для уровня

    def __init__(self, player):#, platforms, moving_platform, enemies):
        self.platform_list = pygame.sprite.Group()
        #for platform in platforms:

        self.enemy_list = pygame.sprite.Group()
        self.player = player

        # изображение для бекгроунда
        #self.background = None

        self.world_shift_x = 0  # начало уровня
        self.world_shift_y = 0  # начало уровня
        self.level_limit = -2000 # конец уровня

        self.list_restart_point=pygame.sprite.Group() # точки восстановления
        self.list_restart_point.add(CheckPoint(DEFAULT_RESTART_POINT[0],DEFAULT_RESTART_POINT[1]))
        self.active_restart_point=self.list_restart_point.sprites()[0].rect.x,self.list_restart_point.sprites()[0].rect.y

        self.background_image = pygame.image.load('source/level01/city_small.jpg').convert()

    def update(self):
        self.platform_list.update()
        self.enemy_list.update()
        self.list_restart_point.update()

    def draw(self, screen):
        screen.blit(self.background_image, [0, 0])
        self.platform_list.draw(screen)
        self.enemy_list.draw(screen)
        self.list_restart_point.draw(screen)

    def restart_level(self):
        self.world_shift_x = 0  # начало уровня
        self.world_shift_y = 0  # начало уровня

    def set_shift_world_x(self, shift_x): # двигаем мир если игрок двигается по X
        self.world_shift_x += shift_x

        for platform in self.platform_list: #передвигаем все, что в листе с платформами
            platform.rect.x += shift_x

        for enemy in self.enemy_list: # передвигаем весь лист врагов
            enemy.rect.x += shift_x

        for check_point in self.list_restart_point:
            check_point.rect.x +=shift_x

    def set_shift_world_y(self, shift_y): # двигаем мир если игрок двигается по Y
        self.world_shift_y += shift_y

        for platform in self.platform_list: #передвигаем все, что в листе с платформами
            platform.rect.y += shift_y

        for enemy in self.enemy_list: # передвигаем весь лист врагов
            enemy.rect.y += shift_y

        for check_point in self.list_restart_point:
            check_point.rect.y += shift_y

    def get_player_respawn(self):
        return self.active_restart_point





# Create platforms for the level
class Level_01(Level):
    """ Definition for level 1. """

    def __init__(self, player):
        """ Create level 1. """

        # Call the parent constructor
        Level.__init__(self, player)

        self.level_limit = -1500

        # Array with width, height, x, and y of platform
        level = [[600,100,20,500],
                 [210, 70, 500, 500],
                 [210, 70, 800, 400],
                 [210, 70, 1000, 500],
                 [210, 70, 1120, 280],
                 [600,100,1350, 280]]

        # Go through the array above and add platforms
        for platform in level:
            block = Platform(platform[0], platform[1])
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            block.player = self.player #???
            self.platform_list.add(block)

        enemies_xy = [[500, 400, -1, -1],
                      [850, 300, 800, 900]]
        for enemy_xy in enemies_xy:
            enemy = Enemy()
            enemy.rect.x = enemy_xy[0]
            enemy.rect.y = enemy_xy[1]
            enemy.level = self
            if enemy_xy[2] >-1:
                enemy.border_patrol_left = enemy_xy[2]
                enemy.border_patrol_right = enemy_xy[3]
                enemy.change_x = 3
                enemy.image = pygame.image.load('objects/mine.png')
            self.enemy_list.add(enemy)

        # Add a custom moving platform
        block = MovingPlatform(70, 40)
        block.rect.x = 1350
        block.rect.y = 280
        block.boundary_left = 1350
        block.boundary_right = 1600
        block.change_x = 1
        block.player = self.player
        block.level = self
        self.platform_list.add(block)

        block = AnotherMovingPlatform(70, 70)
        block.rect.x = 300
        block.rect.y = 300
        block.boundary_top = -100
        block.boundary_bottom = 550
        block.change_y = -1
        block.player = self.player
        block.level = self
        self.platform_list.add(block)

        self.list_restart_point.add(CheckPoint(1350, 200))

# Create platforms for the level
class Level_02(Level):
    """ Definition for level 2. """

    def __init__(self, player):
        """ Create level 1. """

        # Call the parent constructor
        Level.__init__(self, player)

        self.level_limit = -1000

        # Array with type of platform, and x, y location of the platform.
        level = [[600,100,50,500],
                 [210, 70, 500, 550],
                 [210, 70, 800, 400],
                 [210, 70, 1000, 500],
                 [210, 70, 1120, 280],
                 ]

        # Go through the array above and add platforms
        for platform in level:
            block = Platform(platform[0], platform[1])
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            block.player = self.player
            self.platform_list.add(block)

        # Add a custom moving platform
        block = MovingPlatform(70, 70)
        block.rect.x = 1500
        block.rect.y = 300
        block.boundary_top = 100
        block.boundary_bottom = 550
        block.change_y = -1
        block.player = self.player
        block.level = self
        self.platform_list.add(block)


class Camera(object):

    def __init__(self,player,current_level):
        self.current_level = current_level
        self.player = player

    def move(self):
        if self.player.rect.right > CAMERA_RIGHT_BOUND:
            diff_x = - self.player.rect.right + CAMERA_RIGHT_BOUND
            self.player.rect.right = CAMERA_RIGHT_BOUND
            self.current_level.set_shift_world_x(diff_x)

        if self.player.rect.left < CAMERA_LEFT_BOUND:
            diff_x = CAMERA_LEFT_BOUND - self.player.rect.left
            self.player.rect.left = CAMERA_LEFT_BOUND
            self.current_level.set_shift_world_x(diff_x)

        if self.player.rect.top < CAMERA_TOP_BOUND:
            diff_y = CAMERA_TOP_BOUND - self.player.rect.top
            self.player.rect.top = CAMERA_TOP_BOUND
            self.current_level.set_shift_world_y(diff_y)

        if self.player.rect.bottom > CAMERA_BOTTOM_BOUND:
            diff_y = CAMERA_BOTTOM_BOUND - self.player.rect.bottom
            self.player.rect.bottom = CAMERA_BOTTOM_BOUND
            self.current_level.set_shift_world_y(diff_y)

def game(screen):
    # Create the player
    player = Player()

    player_life_count = PLAYER_LIFE_COUNT
    # Create all the levels
    level_list = []
    level_list.append(Level_01(player))
    level_list.append(Level_02(player))

    # Set the current level
    current_level_no = 0
    current_level = level_list[current_level_no]

    active_sprite_list = pygame.sprite.Group()
    player.level = current_level

    camera = Camera(player, current_level)

    player.rect.x = current_level.active_restart_point[0]
    player.rect.y = current_level.active_restart_point[1]
    active_sprite_list.add(player)

    # Loop until the user clicks the close button.
    done = False

    player_ui = Player_UI(screen)

    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    # -------- Main Program Loop -----------
    while not done:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.go_left()
                if event.key == pygame.K_RIGHT:
                    player.go_right()
                if event.key == pygame.K_UP:
                    player.jump()
                if event.key == pygame.K_ESCAPE:
                    pause_items=['Продолжить', 'Выход']
                    res = Menu(screen, pause_items, None).main_menu()
                    if res == len(pause_items) - 1:
                        sys.exit()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and player.change_x < 0:
                    player.stop()
                if event.key == pygame.K_RIGHT and player.change_x > 0:
                    player.stop()

        # Update the player.
        active_sprite_list.update()

        # Update items in the level
        current_level.update()

        # движение камеры
        camera.move()

        # If the player gets to the end of the level, go to the next level
        current_position = player.rect.x + current_level.world_shift_x
        if current_position < current_level.level_limit:
            if current_level_no < len(level_list) - 1:
                player.rect.x = 120
                current_level_no += 1
                current_level = level_list[current_level_no]
                player.level = current_level
                camera = Camera(player, current_level)
            else:
                # Out of levels. This just exits the program.
                # You'll want to do something better.
                done = True

        if not player.alive:
            player_life_count -= 1
            if player_life_count < 1:
                return 0
            else:
                current_level.set_shift_world_x(-current_level.world_shift_x)
                current_level.world_shift_x = 0
                player.rect.x = current_level.active_restart_point[0]
                current_level.set_shift_world_y(-current_level.world_shift_y)
                current_level.shift_world_y = 0
                player.rect.y =  current_level.active_restart_point[1]
                player.alive = True
                player.lifesize = 100

        # ALL CODE TO DRAW SHOULD GO BELOW THIS COMMENT
        current_level.draw(screen)
        active_sprite_list.draw(screen)

        # отрисовка очков, жизни и пр. текста
        player_ui.draw_text(player.lifesize, 36, 50, 10)
        player_ui.draw_text(' X ',36, 90, 10)
        player_ui.draw_text(player_life_count, 36, 110, 10)
        player_ui.draw_text(player.rect.x, 18, SCREEN_WIDTH / 2 - 50, 10)
        player_ui.draw_text(player.rect.y, 18, SCREEN_WIDTH / 2 - 50, 30)
        if player.level is not None:
            player_ui.draw_text(-player.level.world_shift_x + player.rect.x, 18, SCREEN_WIDTH / 2 + 50, 10)
            player_ui.draw_text(-player.level.world_shift_y + player.rect.y, 18, SCREEN_WIDTH / 2 + 50, 30)
            player_ui.draw_text(player.level.active_restart_point[0], 18, SCREEN_WIDTH / 2 + 100, 10)
            player_ui.draw_text(player.level.active_restart_point[1], 18, SCREEN_WIDTH / 2 + 100, 30)
        # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT

        # Limit to 60 frames per second
        clock.tick(60)

        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()


def main():
    """ Main Program """
    pygame.init()
    # Set the height and width of the screen
    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)

    pygame.display.set_caption(MYCAPTION)

    background = MAIN_BACKGROUND
    menu=Menu(screen, ITEMS, pygame.image.load(background).convert())
    res = menu.main_menu()

    while res != 3:
        res = game(screen)
        if res == 0:
            background = DEATH_BACKGROUND
        res = Menu(screen, ITEMS, pygame.image.load(background).convert()).main_menu()
        if res == 0:
            background = MAIN_BACKGROUND

    # Be IDLE friendly. If you forget this line, the program will 'hang'
    # on exit.
    pygame.quit()


if __name__ == "__main__":
    main()

