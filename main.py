# main.py
# Ben Morrison


import pygame, math, random, pygame.gfxdraw, configparser, pygame_gui as ui
from pprint import pprint as pp

# Pygame setup and application stuff
game_name = "Winter At UAH"
pygame.init()
display, clock = pygame.display.Info(), pygame.time.Clock()
width, height = display.current_w, display.current_h
center_x, center_y = width // 2, height // 2
win = pygame.display.set_mode((width, height))
pygame.display.set_caption(game_name)

# GUI Library setup

manager = ui.UIManager((width, height))

# Configuration loading
config = configparser.ConfigParser()
config.read("settings.config")

# Classes
class Map:
    def __init__(self, name, author):
        self.name = name
        self.author = author
        self.width, self.height = None, None
        self.map = None
        self.entities = []

    def is_within(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def get_pos(self, x, y):
        if self.is_within(x, y):
            for entity in self.entities:
                if (x, y) == entity.pos():
                    return entity
            return self.map[x][y]
        return 1

    def is_empty(self, x, y):
        value = self.get_pos(x, y)
        return value == 0 or value == 9

    def find(self, to_find) -> tuple:
        for x in range(self.width):
            for y in range(self.height):
                if self.get_pos(x, y) == to_find:
                    yield x, y

    def set(self, x, y, value):
        self.map[x][y] = value

    def load(self):
        self.entities = []
        with open(f"levels/{self.name}.txt", "r") as file:
            rows = []
            while data := file.readline()[0:-1]:
                rows.append([int(i) for i in data])
            game_map = [[rows[y][x] for y in range(len(rows))] for x in range(len(rows[0]))]
            self.map = game_map
            self.width, self.height = len(game_map), len(game_map[0])
            self.entities = [Player(point, (0, 0, 255), i, self) for i, point in enumerate(self.find(2))]\
                            + [Box(point, (255, 255 // 2, 0), i, self) for i, point in enumerate(self.find(3))]
            for point in list(self.find(2)) + list(self.find(3)):
                self.set(*point, 0)

    def beaten(self):
        return all([player.finished for player in self.get_players()])

    def get_players(self):
        for entity in self.entities:
            if isinstance(entity, Player):
                yield entity

class Box:
    def __init__(self, pos, color, id, game_map):
        self.x, self.y = pos
        self.r, self.g, self.b = self.color = color
        self.id = id
        self.direction = -1
        self.map = game_map
        self.future_pos = pos
        game_map.map[self.x][self.y] = 0

    def pos(self):
        return self.x, self.y

    def is_moving(self):
        return self.direction != -1

    def change_direction(self, direction):
        self.direction = direction

    def get_next(self, steps=1, x=None, y=None, ignore_collision=False):
        if x is None or y is None:
            x, y = self.x, self.y
        sx, sy = x, y
        if self.direction != -1:
            d = self.direction
            if d == 0:
                x += 1
            elif d == 1:
                y -= 1
            elif d == 2:
                x -= 1
            elif d == 3:
                y += 1

        if self.map.is_empty(x, y) or ignore_collision:
            if steps == 1:
                return x, y
            elif steps > 1:
                return self.get_next(steps - 1, x, y)
        return sx, sy

    def tick(self):
        future_pos = self.get_next()
        # Checking for player collision
        hit_player = False
        for player2 in self.map.entities:
            if self.id != player2.id and future_pos == player2.pos():
                if self.direction != player2.direction or future_pos == player2.get_next():
                    hit_player = True

        # Checking for bounds or wall collision
        if not hit_player and future_pos != self.pos():
            self.future_pos = future_pos
            # Checking for finish
            if self.map.get_pos(*future_pos) == 9:
                self.direction = -1
        else:
            collided = self.map.get_pos(*self.get_next(ignore_collision=True))
            if isinstance(collided, Box):
                collided.direction = self.direction
                self.future_pos = self.pos()
                self.direction = -1
            else:
                self.future_pos = self.pos()
                self.direction = -1


class Player:
    def __init__(self, pos, color, id, game_map):
        self.x, self.y = pos
        self.r, self.g, self.b = self.color = color
        self.id = id
        self.direction = -1
        self.map = game_map
        self.future_pos = pos
        self.finished = False
        game_map.map[self.x][self.y] = 0

    def pos(self):
        return self.x, self.y

    def is_moving(self):
        return self.direction != -1

    def change_direction(self, direction):
        self.direction = direction

    def get_next(self, steps=1, x=None, y=None, ignore_collision=False):
        if x is None or y is None:
            x, y = self.x, self.y
        sx, sy = x, y
        if self.direction != -1:
            d = self.direction
            if d == 0:
                x += 1
            elif d == 1:
                y -= 1
            elif d == 2:
                x -= 1
            elif d == 3:
                y += 1

        if self.map.is_empty(x, y) or ignore_collision:
            if steps == 1:
                return x, y
            elif steps > 1:
                return self.get_next(steps - 1, x, y)
        return sx, sy

    def tick(self):
        if not self.finished:
            future_pos = self.get_next()
            # Checking for player collision
            hit_player = False
            for player2 in self.map.entities:
                if self.id != player2.id and future_pos == player2.pos():
                    if self.direction != player2.direction or future_pos == player2.get_next():
                        hit_player = True

            # Checking for bounds or wall collision
            if not hit_player and future_pos != self.pos():
                self.future_pos = future_pos
                # Checking for finish
                if self.map.get_pos(*future_pos) == 9:
                    self.finished = True
                    self.direction = -1
            else:
                collided = self.map.get_pos(*self.get_next(ignore_collision=True))
                if isinstance(collided, Box):
                    collided.direction = self.direction
                    self.future_pos = self.pos()
                    self.direction = -1
                else:
                    self.future_pos = self.pos()
                    self.direction = -1

# Functions
def menu():
    # Setting up loop variables
    running, paused, time = True, False, 0

    # Setting up UI
    play_button = ui.elements.UIButton(relative_rect=pygame.Rect(center_x, center_y, 100, 50),
                                        text='Play', manager=manager,
                                        anchors={'left': 'left',
                                                 'right': 'right',
                                                 'top': 'top',
                                                 'bottom': 'bottom'})

    # Loading control configuration
    up, down = int(config["controls"]["up"]), int(config["controls"]["down"])
    left, right = int(config["controls"]["left"]), int(config["controls"]["right"])
    reset = int(config["controls"]["reset"])

    while running:
        delta = clock.tick(60) / 1000

        # Event handling
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            # UI Events
            if event.type == pygame.USEREVENT:
                if event.user_type == ui.UI_BUTTON_PRESSED:
                    if event.ui_element == play_button:
                        return 1
            # Key Events
            elif event.type == pygame.KEYUP:
                key = event.key
                print(key)
                if key == pygame.K_ESCAPE:
                    return -1
                elif key == pygame.K_p:
                    paused = not paused
                elif key == reset:
                    return 0
                elif key == pygame.K_d:
                    manager.set_visual_debug_mode(True)
            elif event.type == pygame.KEYDOWN:
                pass
            manager.process_events(event)

        # Ticking
        manager.update(delta)
        if not paused:
            time += delta
        else:
            print("Paused")

        # Drawing
        win.fill((0, 0, 50))

        manager.draw_ui(win)
        pygame.display.update()

    return -1
#kekW Ben
def game():
    # Setting up loop variables
    running, paused, time = True, False, 0

    # Loading control configuration
    up, down = int(config["controls"]["up"]), int(config["controls"]["down"])
    left, right = int(config["controls"]["left"]), int(config["controls"]["right"])
    reset = int(config["controls"]["reset"])

    # Setting up game variables
    maps = [Map("level1", "Bmorr"), Map("level2", "Bmorr"), Map("level3", "Bmorr"), Map("level4", "Bmorr")]
    # Setting up level variables
    game_map = maps[0]
    game_map.load()
    grid_size = min(width // game_map.width, height // game_map.height)
    while running:
        delta = clock.tick(60) / 1000
        events = pygame.event.get()
        tick = False
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYUP:
                key = event.key
                if key == pygame.K_ESCAPE:
                    return -1
                elif key == pygame.K_p:
                    paused = not paused
                elif key == reset:
                    game_map.load()
                elif key == pygame.K_SPACE:
                    if game_map.beaten():
                        current_map = maps.index(game_map)
                        if len(maps) - 1 > current_map:
                            game_map = maps[current_map + 1]
                            game_map.load()
                            grid_size = min(width // game_map.width, height // game_map.height)
            elif event.type == pygame.KEYDOWN:
                key = event.key
                if key == pygame.K_m:
                    print()
                elif key == pygame.K_t:  # Manual ticking for debugging purposes
                    tick = True

                # Player Movement
                player_moving = False
                for player in game_map.entities:
                    if isinstance(player, Player):
                        player_moving = player_moving or player.is_moving()
                # Keypress Processing
                if not player_moving:
                    for i, player in enumerate(game_map.entities):
                        if isinstance(player, Player):
                            if key == right:
                                player.direction = 0
                            elif key == up:
                                player.direction = 1
                            elif key == left:
                                player.direction = 2
                            elif key == down:
                                player.direction = 3
        # Ticking
        if not paused or tick:
            time += delta

            # Tick each player
            for entity in game_map.entities:
                entity.tick()
            # Actually move each player
            for player in game_map.entities:
                player.x, player.y = player.future_pos

        # Drawing
        win.fill((0, 0, 0))
        # Fill in the level area
        pygame.draw.rect(win, (255, 255, 255), (0, 0, grid_size * game_map.width, grid_size * game_map.height))
        # Loop through each x, y pair in the level
        for x in range(game_map.width):
            for y in range(game_map.height):
                value, color = game_map.get_pos(x, y), (255, 255, 255)
                if value != 0:
                    if value == 1:
                        color = (0, 0, 0)
                    elif isinstance(value, Box):
                        color = value.color
                    elif value == 9:
                        color = (0, 255, 0)
                    pygame.draw.rect(win, color, (x * grid_size, y * grid_size, grid_size, grid_size))
        for i, player in enumerate(game_map.entities):
            color = player.color
            pygame.draw.rect(win, color, (player.x * grid_size, player.y * grid_size, grid_size, grid_size))
        pygame.display.flip()

    return -1


def main():
    looping = True
    next_view = 0
    while looping:
        if next_view == -1:
            looping = False
        elif next_view == 0:
            next_view = menu()
        elif next_view == 1:
            next_view = game()
        else:
            print(f"ERROR: View #{next_view} not found!")
            looping = False
    print("Quitting application!")


if __name__ == '__main__':
    main()

pygame.display.quit()
