from maze_generator import *


def is_collide(x, y):
    tmp_rect = player_rect.move(x, y)
    if tmp_rect.collidelist(walls_collide_list) == -1:
        return False
    return True

def is_game_over():
    global time, score, FPS #record, FPS
    if time < 0:
        pygame.time.wait(700)
        player_rect.center = TILE // 2, TILE // 2
        time, FPS = 60, 60


def set_record(rec):
    with open('record', 'w') as f:
        f.write(str(rec))


record = "F"
FPS = 60
pygame.init()
game_surface = pygame.Surface(RES)
surface = pygame.display.set_mode((WIDTH + 300, HEIGHT))
clock = pygame.time.Clock()

# use images
bg_game = pygame.image.load('img/bg_1.jpg').convert()
bg = pygame.image.load('img/bg_main.jpg').convert()

# get maze
maze = generate_maze()

exit = pygame.image.load('img/exit.png').convert_alpha()
exit = pygame.transform.scale(exit, (TILE - 2 * maze[0].thickness, TILE - 2 * maze[0].thickness))

# player settings
player_speed = 6
player_img = pygame.image.load('img/0.png').convert_alpha()
player_img = pygame.transform.scale(player_img, (TILE - 2 * maze[0].thickness, TILE - 2 * maze[0].thickness))
player_rect = player_img.get_rect()
player_rect.center = TILE // 2, TILE // 2
directions = {'a': (-player_speed, 0), 'd': (player_speed, 0), 'w': (0, -player_speed), 's': (0, player_speed)}
keys = {'a': pygame.K_a, 'd': pygame.K_d, 'w': pygame.K_w, 's': pygame.K_s}
direction = (0, 0)

# collision list
walls_collide_list = sum([cell.get_rects() for cell in maze], [])

# timer, score, record
pygame.time.set_timer(pygame.USEREVENT, 1000)
time = 30


# fonts
font = pygame.font.SysFont('Impact', 112)
text_font = pygame.font.SysFont('Impact', 60)

while True:
    surface.blit(bg, (WIDTH, 0))
    surface.blit(game_surface, (0, 0))
    game_surface.blit(bg_game, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT or time <= 0:
            pygame.quit()
        if event.type == pygame.USEREVENT:
            time -= 1
        if player_rect[0] >= 840 and player_rect[1] >= 600:
            print("YES")
            record = "T"
            set_record(record)
            pygame.quit()

    # controls and movement
    pressed_key = pygame.key.get_pressed()
    for key, key_value in keys.items():
        if pressed_key[key_value] and not is_collide(*directions[key]):
            direction = directions[key]
            break
    if not is_collide(*direction):
        player_rect.move_ip(direction)

    # draw maze
    [cell.draw(game_surface) for cell in maze]

    # draw player
    game_surface.blit(player_img, player_rect)
    game_surface.blit(exit, (WIDTH - 50, HEIGHT - 70))

    # draw information
    surface.blit(text_font.render('TIME', True, pygame.Color('forestgreen'), True), (WIDTH + 70, 10))
    surface.blit(font.render(f'{time}', True, pygame.Color('forestgreen')), (WIDTH + 70, 100))
    surface.blit(text_font.render('Use WASD', True, pygame.Color('forestgreen'), True), (WIDTH + 30, 250))
    surface.blit(text_font.render('to move', True, pygame.Color('forestgreen'), True), (WIDTH + 30, 335))

    # print(clock.get_fps())
    pygame.display.flip()
    clock.tick(FPS)
