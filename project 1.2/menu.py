import sys

import pygame

ITEM_INTERVAL = 60

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_BLUE = 0, 191, 255
BLUE = 33, 150, 243
LIGHT_GREEN = 204, 255, 51
FONT_BOLD = 'source/fonts/Slimamif.ttf'


class Menu(object):

    def __init__(self, screen, items, background):
        self.screen = screen
        self.items = items
        if background is None:
            back_img = pygame.Surface([SCREEN_WIDTH, SCREEN_HEIGHT])
            back_img.fill(LIGHT_BLUE)
            back_img.set_alpha(2) #прозрачность, 2 - степень
            self.background = back_img
        else:
            self.background = background

    def main_menu_setup(self):
        start_item_y = SCREEN_HEIGHT / 2 - len(self.items) / 2 * ITEM_INTERVAL
        i = 0
        self.buttons = []
        for item in self.items:
            center = (int(SCREEN_WIDTH / 2), int(start_item_y) + ITEM_INTERVAL * i)
            self.buttons.append((center, item))
            i += 1

    def main_menu_render(self, namber):
        i = 0
        self.screen.blit(self.background, [0, 0])
        for item in self.buttons:
            if i == namber:
                color = LIGHT_GREEN
            else:
                color = BLACK
            i += 1
            text_surf, text_rect = self.text_objects(item[1], FONT_BOLD,36, color)
            text_rect.center = item[0]
            self.screen.blit(text_surf, text_rect)

    def text_objects(self, text, font_name, size=36, colour=BLACK):
        font = pygame.font.Font(font_name, size)
        text_surface = font.render(text, True, colour)
        return text_surface, text_surface.get_rect()

    def main_menu(self):
        global ticks
        clock = pygame.time.Clock()
        self.main_menu_setup()
        self.main_menu_render(0)
        start_game = view_hs = False
        i_item=0;
        smth_pressed = False
        while True:
            for event in pygame.event.get():
                pressed_keys = pygame.key.get_pressed()
                alt_f4 = (event.type == pygame.KEYDOWN and (event.key == pygame.K_F4
                                                     and (pressed_keys[pygame.K_LALT] or pressed_keys[pygame.K_RALT])))
                if event.type == pygame.QUIT or alt_f4:
                    return len(self.items) - 1
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        i_item -= 1
                    if event.key == pygame.K_DOWN:
                        i_item += 1
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        smth_pressed = True
                    if event.key == pygame.K_ESCAPE:
                        return -1


            if smth_pressed: return i_item

            if i_item < 0:
                i_item = len(self.items)-1
            if i_item >= len(self.items):
                i_item = 0

            self.main_menu_render(i_item)

            pygame.display.flip()
            clock.tick(60)
