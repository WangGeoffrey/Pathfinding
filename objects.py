import pygame
import settings

WIDTH = settings.WIDTH
ACROSS = settings.ACROSS
SIZE = settings.SIZE
WIN = settings.WIN
font = settings.font

directions = [(0, -1), (1, 0), (0, 1), (-1, 0)] #[up, right, down, left]

BLACK = (0, 0, 0)
GREY = (128, 128, 128)
LIGHTGREY = (192, 192, 192)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
TURQUOISE = (64, 224, 208)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)

class Node:
    def __init__(self, pos):
        self.x_pos, self.y_pos = pos
        self.color = WHITE
        self.neighbors = []

    def get_pos(self):
        return self.x_pos, self.y_pos

    def change_pos(self, new_pos):
        self.x_pos, self.y_pos = new_pos

    def get_neighbors(self):
        return self.neighbors.copy()

    def is_start(self):
        return self.color == GREEN

    def is_end(self):
        return self.color == RED

    def is_flag(self):
        return self.color == ORANGE

    def is_destination(self):
        return self.is_start() or self.is_end() or self.is_flag()

    def is_wall(self):
        return self.color == GREY

    def is_path(self):
        return self.color == BLUE

    def set_default(self):
        self.color = WHITE

    def set_start(self):
        self.color = GREEN
    
    def set_end(self):
        self.color = RED

    def set_flag(self):
        self.color = ORANGE

    def set_wall(self):
        self.color = GREY

    def set_path(self):
        self.color = BLUE

    def set_open(self):
        self.color = YELLOW
    
    def set_closed(self):
        self.color = TURQUOISE

    def distance(self, other):
        x, y = other.get_pos()
        x_dist = abs(self.x_pos - x)
        y_dist = abs(self.y_pos - y)
        if x_dist <= y_dist:
            return x_dist*14 + (y_dist - x_dist)*10
        else:
            return y_dist*14 + (x_dist - y_dist)*10

    def update_neighbors(self, grid):
        self.neighbors.clear()
        x, y = self.get_pos()
        for index in range(len(directions)):
            x1, y1 = directions[index]
            x2, y2 = directions[(index+1)%4]
            if grid.valid_pos((x+x1, y+y1)):
                self.neighbors.append(grid.get_node((x+x1, y+y1)))
            if grid.valid_pos((x+x1+x2, y+y1+y2)) and (grid.valid_pos((x+x1, y+y1)) or grid.valid_pos((x+x2, y+y2))):
                self.neighbors.append(grid.get_node((x+x1+x2, y+y1+y2)))

    def draw(self):
        pygame.draw.rect(WIN, self.color, (self.x_pos*SIZE, self.y_pos*SIZE, SIZE, SIZE))

class Grid:
    def __init__(self):
        self.grid = []
        for i in range(ACROSS):
            self.grid.append([])
            for j in range(ACROSS):
                self.grid[i].append(Node((i, j)))
        self.start = self.grid[0][0]
        self.end = self.grid[ACROSS-1][ACROSS-1]
        self.start.set_start()
        self.end.set_end()
        self.flags = []
        self.old = Node((0, 0))

    def get_node(self, pos):
        x, y = pos
        return self.grid[x][y]

    def get_start(self):
        return self.start

    def get_end(self):
        return self.end

    def get_flags(self):
        return self.flags

    def get_flags_end(self):
        return self.flags + [self.end]

    def add_flag(self, flag):
        self.flags.append(flag)

    def remove_flag(self, flag):
        self.flags.remove(flag)

    def valid_pos(self, pos):
        x, y = pos
        if 0 <= x < ACROSS and 0 <= y < ACROSS:
            if not self.get_node(pos).is_wall():
                return True
        return False

    def move_node(self, node):
        x, y = pos = node.get_pos()
        self.old.change_pos(pos)
        run = True
        while run:
            for event in pygame.event.get():
                if not pygame.mouse.get_pressed()[0]:
                    run = False
                mouse = tuple(elem//(SIZE) for elem in pygame.mouse.get_pos())
                if mouse != pos:
                    if mouse[0] < ACROSS:
                        if not self.get_node(mouse).is_destination():
                            self.grid[x][y] = self.old
                            self.old = self.get_node(mouse)
                            x, y = pos = mouse
                            self.grid[x][y] = node
                            node.change_pos(mouse)
                            self.draw()
        self.old.set_default()

    def clear_all(self):
        for col in self.grid:
            for node in col:
                node.set_default()
        self.start.set_start()
        self.end.set_end()
        self.flags.clear()

    def clear_other(self):
        for col in self.grid:
            for node in col:
                if not (node.is_destination() or node.is_wall()):
                    node.set_default()

    def reset(self):
        self.start.set_default()
        self.start = self.grid[0][0]
        self.end.set_default()
        self.end = self.grid[ACROSS-1][ACROSS-1]
        self.clear_all()
    
    def draw(self):
        for col in self.grid:
            for node in col:
                node.draw()
        for indent in range(0, WIDTH+1, SIZE):
            pygame.draw.line(WIN, BLACK, (0, indent), (WIDTH, indent))
            pygame.draw.line(WIN, BLACK, (indent, 0), (indent, WIDTH))
        pygame.display.update()

class Button: #Toggle button
    def __init__(self, x_pos, y_pos, width, height, text):
        self.color = WHITE
        self.rect = pygame.Rect(x_pos, y_pos, width, height)
        self.text = font.render(text, True, BLACK)
        self.text_rect = self.text.get_rect(center=(x_pos + width//2, y_pos + height//2))

    def get_rect(self):
        return self.rect

    def click(self):
        if self.is_selected():
            self.deselect()
        else:
            self.select()
        return False

    def select(self):
        self.color = GREY

    def deselect(self):
        self.color = WHITE

    def is_selected(self):
        return self.color == GREY

    def hovered(self):
        if not self.is_selected():
            self.color = LIGHTGREY

    def clear(self):
        if not self.is_selected():
            self.color = WHITE

    def draw(self):
        pygame.draw.rect(WIN, self.color, self.rect)
        WIN.blit(self.text, self.text_rect)

class Button2(Button): #Execute button
    def __init__(self, x_pos, y_pos, width, height, text, function):
        super(Button2, self).__init__(x_pos, y_pos, width, height, text)
        self.execute = function

    def click(self):
        self.color = GREY
        self.draw()
        self.color = WHITE
        return self.execute()
        
class Button3(Button2): #Relational button
    def click(self):
        self.color = GREY
        self.draw()
        self.execute()
        return False
