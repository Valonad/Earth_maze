import time
import pygame
import sys
import os
from pygame.locals import *


# Initializing
pygame.init()

# Setting up FPS
frames = 60
FPS = pygame.time.Clock()

# Creating colors
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)

# Other Variables for use in the program
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
# length of each grid
movement_distance = 140
grid_start_x = 290
grid_start_y = 200
move_number = 6
tile_look = "up"
game_end = False

# Display window
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
window.fill(CYAN)
pygame.display.set_caption("Roots")
background = pygame.image.load("backgroundlv1.png")

# Setting up Fonts
font = pygame.font.SysFont("Courier", 60)
font_small = pygame.font.SysFont("Courier", 20)
game_over = font.render("Game Over", True, BLACK)
game_win = font.render("You win", True, YELLOW)
instructions = font_small.render("Use the arrow keys to move.", True, BLACK)
instructions2 = font_small.render("Press R if you get stuck.", True, BLACK)


# making player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, moves):
        # Initializes from the super sprite class
        # image is the loop of the player
        # rect is turning the image's dimensions into the rectangle
        # center of the rectangle is where it starts
        # moves is how many moves the player has
        # its position is the position relative to the grid
        super().__init__()
        self.level = None
        self.image = pygame.image.load("up.png")
        self.direction = "down"
        self.rect = self.image.get_rect()
        self.rect.center = (x + self.rect.width // 2, y + self.rect.height // 2)
        self.moves = moves
        self.pos = [0, 0]  # Y AND X NOT X AND Y

    def assign_level(self, level):
        self.level = level
        self.rect.center = (level.x, level.y)

    def move_up(self):
        if self.rect.top > 0 and self.moves > 0 and self.pos[0] >= 0:
            self.rect.move_ip(0, -movement_distance)
            # self.image = pygame.image.load("up.png")
            self.pos[1] -= 1
            self.change_moves()
            self.image = pygame.image.load("down.png")
            self.direction = "up"
            pygame.mixer.Sound("move.wav").play()

    def move_down(self):
        if self.rect.bottom < SCREEN_HEIGHT and self.moves > 0:
            self.rect.move_ip(0, movement_distance)
            # self.image = pygame.image.load("down.png")
            self.pos[1] += 1
            self.change_moves()
            self.image = pygame.image.load("up.png")
            self.direction = "down"
            pygame.mixer.Sound("move.wav").play()

    def move_left(self):
        if self.rect.left > 0 and self.moves > 0 and self.pos[1] >= 0:
            self.rect.move_ip(-movement_distance, 0)
            # self.image = pygame.image.load("left.png")
            self.pos[0] -= 1
            self.change_moves()
            self.image = pygame.image.load("right.png")
            self.direction = "left"
            pygame.mixer.Sound("move.wav").play()

    def move_right(self):
        if self.rect.right < SCREEN_WIDTH and self.moves > 0:
            self.rect.move_ip(movement_distance, 0)
            # self.image = pygame.image.load("right.png")
            self.pos[0] += 1
            self.change_moves()
            self.image = pygame.image.load("left.png")
            self.direction = "right"
            pygame.mixer.Sound("move.wav").play()

    def change_moves(self):
        for tl in self.level.tiles:
            if tl.pos == self.pos:
                if tl.isbad:
                    self.moves -= 2
                else:
                    self.moves -= 1

    def bool_direction(self, direction, evt):
        rock_bool = False
        if direction == "down":
            for tl in self.level.tiles:
                if tl.pos[1] == self.pos[1] + 1 and tl.pos[0] == self.pos[0]:
                    if tl.isrock or tl.isused:
                        rock_bool = True
            return evt.key == K_DOWN and not player_seed.direction == "up" and not rock_bool
        elif direction == "up":
            for tl in self.level.tiles:
                if tl.pos[1] == self.pos[1] - 1 and tl.pos[0] == self.pos[0]:
                    if tl.isrock or tl.isused:
                        rock_bool = True
            return evt.key == K_UP and not player_seed.direction == "down" and not rock_bool
        elif direction == "right":
            for tl in self.level.tiles:
                if tl.pos[1] == self.pos[1] and tl.pos[0] == self.pos[0] + 1:
                    if tl.isrock or tl.isused:
                        rock_bool = True
            return evt.key == K_RIGHT and not player_seed.direction == "left" and not rock_bool
        else:
            for tl in self.level.tiles:
                if tl.pos[1] == self.pos[1] and tl.pos[0] == self.pos[0] - 1:
                    if tl.isrock or tl.isused:
                        rock_bool = True
            return evt.key == K_LEFT and not player_seed.direction == "right" and not rock_bool

    def restart_level(self, level, plant):
        self.rect.center = (level.x, level.y)
        self.pos = [0, 0]
        self.direction = "down"
        self.moves = level.moves
        self.image = pygame.image.load("up.png")
        plant.age = 0
        plant.update()
        for tl in level.tiles:
            tl.image = pygame.image.load("grid.png")
            if not tl.pos == [0, 0]:
                tl.isused = False


class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, pos):
        super().__init__()
        self.image = pygame.image.load("grid.png")
        self.rect = self.image.get_rect()
        self.rect.center = (x + self.rect.width // 2, y + self.rect.height // 2)
        self.pos = pos
        self.isbad = False
        self.isrock = False
        self.isused = False


class Level:
    # levels should have: grid starts (x and y), number of moves, a tile list
    def __init__(self, start_x, start_y, moves, tiles, width, height, player):
        self.x = start_x + player.rect.width // 2
        self.y = start_y + player.rect.height // 2
        self.moves = moves
        self.tiles = tiles
        self.width = width
        self.height = height
        self.number = None


class Plant(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("s1.png")
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.age = 1

    def move(self, x, y):
        self.rect.center = (x, y)

    def update(self):
        if self.age < 5:
            self.age += 1
        if self.age == 1:
            self.image = pygame.image.load("s1.png")
        if self.age == 2:
            self.image = pygame.image.load("s2.png")
        if self.age == 3:
            self.image = pygame.image.load("s3.png")
        if self.age == 4:
            self.image = pygame.image.load("s4.png")
        if self.age == 5:
            self.image = pygame.image.load("s5.png")
        if self.age == 6:
            self.image = pygame.image.load("s6.png")

    def update_last(self):
        if self.age == 5:
            self.age += 1
            self.image = pygame.image.load("s6.png")


def assign_tile(pl, tiles, tile_pic):
    for tl in tiles:
        if tl.pos == pl.pos:
            tl.image = pygame.image.load(tile_pic)
            tl.isused = True


# Creates objects


# create a list of tiles. tlx and tly is the position of the [0,0] tile
tile_list = []
tlx = grid_start_x
tly = grid_start_y
# loop to make the tiles
for i in range(3):
    for j in range(4):
        tile_list.append(Tile(tlx + movement_distance * i, tly + movement_distance * j, [i, j]))
tile_list[0].image = pygame.image.load("up.png")  # marks initial tile as filled
# creates map and marked tiles
for tile in tile_list:
    if tile.pos == [0, 2] or tile.pos == [1, 1] or tile.pos == [2, 0]:
        tile.isbad = True
    if tile.pos == [0, 3] or tile.pos == [2, 3]:
        tile.isrock = True
    if tile.pos == [0, 0]:
        tile.isused = True

# creates level 2 tiles
tile_list2 = []
tlx2 = 220
tly2 = 200
for i in range(4):
    for j in range(4):
        tile_list2.append(Tile(tlx2 + movement_distance * i, tly2 + movement_distance * j, [i, j]))
tile_list2[0].image = pygame.image.load("up.png")  # marks initial tile as filled
# creates map and marked tiles
for tile in tile_list2:
    if tile.pos == [0, 1] or tile.pos == [1, 1] or tile.pos == [2, 0] or tile.pos == [1, 2]:
        tile.isbad = True
    if tile.pos == [0, 3] or tile.pos == [1, 3] or tile.pos == [3, 3]:
        tile.isrock = True
    if tile.pos == [0, 0]:
        tile.isused = True

# create player
player_seed = Player(grid_start_x, grid_start_y, move_number)

# creates levels
level1 = Level(grid_start_x, grid_start_y, 6, tile_list, 2, 3, player_seed)
level1.number = 1
player_seed.assign_level(level1)
level2 = Level(tlx2, tly2, 6, tile_list2, 3, 3, player_seed)
level2.number = 2

# creates plant
tommy = Plant(level1.x + 20, level1.y - movement_distance - 30)

# groups the player and plant into a group for some easy functions
all_sprites = pygame.sprite.Group()
all_sprites.add(player_seed)
all_sprites.add(tommy)


def level_loop(player, level, win_position):
    global tile_look
    global background
    global game_end
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYUP:
            if event.key == K_r:
                player.restart_level(level, tommy)
            if player.bool_direction("up", event) and not player.pos[1] == 0:
                if player.direction == "up":
                    tile_look = "vertical.png"
                if player.direction == "right":
                    tile_look = "left up.png"
                if player.direction == "left":
                    tile_look = "right up.png"
                assign_tile(player, level.tiles, tile_look)
                player.move_up()
                tommy.update()
            elif player.bool_direction("down", event) and not player.pos[1] == level.height:
                if player.direction == "down":
                    tile_look = "vertical.png"
                if player.direction == "right":
                    tile_look = "left down.png"
                if player.direction == "left":
                    tile_look = "right down.png"
                assign_tile(player, level.tiles, tile_look)
                player.move_down()
                tommy.update()
            elif player.bool_direction("left", event) and not player.pos[0] == 0:
                if player.direction == "up":
                    tile_look = "left down.png"
                if player.direction == "down":
                    tile_look = "left up.png"
                if player.direction == "left":
                    tile_look = "horizontal.png"
                assign_tile(player, level.tiles, tile_look)
                player.move_left()
                tommy.update()
            elif player.bool_direction("right", event) and not player.pos[0] == level.width:
                if player.direction == "up":
                    tile_look = "right down.png"
                if player.direction == "down":
                    tile_look = "right up.png"
                if player.direction == "right":
                    tile_look = "horizontal.png"
                assign_tile(player, level.tiles, tile_look)
                player.move_right()
                tommy.update()
    # Draws background then score
    window.blit(background, (0, 0))
    moves_remaining = font_small.render(f'Moves Remaining: {player_seed.moves}', True, BLACK)
    window.blit(moves_remaining, (10, 10))
    # writes more text
    window.blit(instructions, (10, instructions.get_height()+10))
    window.blit(instructions2, (10, instructions.get_height()*2+10))

    # if player arrives at win position they win, otherwise if they run out of moves they lose
    if player_seed.pos == win_position:
        player.image = pygame.image.load("last.png")
        for tl in level.tiles:
            if player.pos == tl.pos:
                tl.image = pygame.image.load("last.png")
        # draws all sprites then draws tiles
        all_sprites.draw(window)
        for tl in level.tiles:
            window.blit(tl.image, tl.rect)
        pygame.display.update()
        pygame.mixer.Sound("win.wav").play()
        time.sleep(0.5)
        while tommy.age < 6:
            tommy.update()
            tommy.update_last()
            all_sprites.draw(window)
            pygame.display.update()
            time.sleep(1)
        if level.number == 1:
            player_seed.assign_level(level2)
            player_seed.restart_level(level2, tommy)
            tommy.move(level2.x + 20, level2.y - movement_distance - 30)
            background = pygame.image.load("backgroundlv2.png")
        else:
            game_end = True
    elif player_seed.moves <= 0:
        pygame.display.update()
        time.sleep(1)
        player_seed.restart_level(level, tommy)


    # draws all sprites then draws tiles
    all_sprites.draw(window)
    for tl in level.tiles:
        window.blit(tl.image, tl.rect)

    pygame.display.update()
    FPS.tick(frames)


# gameplay loop
while True:
    if player_seed.level == level1:
        level_loop(player_seed, level1, [1, 3])
    elif player_seed.level == level2 and not game_end:
        level_loop(player_seed, level2, [2, 3])
    else:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        window.blit(game_win, (500-game_win.get_width() // 2, 10))
        pygame.display.update()
