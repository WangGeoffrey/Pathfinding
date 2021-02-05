import pygame
import math
from queue import PriorityQueue
from random import randint

pygame.init()
WIDTH = 600
SIDE_BAR = 100
SIZE = 50
WIN = pygame.display.set_mode((WIDTH+SIDE_BAR, WIDTH))
pygame.display.set_caption("Pathfinding Visualizer")
font = pygame.font.SysFont('Corbel', 15)

directions = [(0, -1), (1, 0), (0, 1), (-1, 0)] #[up, right, down, left]

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

class Node:
    def __init__(self, pos):
        self.x_pos, self.y_pos = pos
        self.color = WHITE
        self.neighbours = []

    def get_pos(self):
        return self.x_pos, self.y_pos

    def change_pos(self, new_pos):
        self.x_pos, self.y_pos = new_pos

    def draw(self):
        size = WIDTH//SIZE
        pygame.draw.rect(WIN, self.color, (self.x_pos*size, self.y_pos*size, size, size))

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

    def set_start(self):
        self.color = GREEN
    
    def set_end(self):
        self.color = RED

    def set_flag(self):
        self.color = ORANGE

    def set_wall(self):
        self.color = GREY

    def set_default(self):
        self.color = WHITE

    def set_path(self):
        self.color = BLUE

    def set_open(self):
        self.color = YELLOW
    
    def set_closed(self):
        self.color = TURQUOISE

    def put_in_grid(self, grid):
        grid[self.x_pos][self.y_pos] = self

    def update_neighbours(self, grid):
        self.neighbours.clear()
        x, y = self.get_pos()
        for index in range(len(directions)):
            x1, y1 = directions[index]
            x2, y2 = directions[(index+1)%4]
            if valid_pos((x+x1, y+y1), grid):
                self.neighbours.append(grid[x+x1][y+y1])
            if valid_pos((x+x1+x2, y+y1+y2), grid) and (valid_pos((x+x1, y+y1), grid) or valid_pos((x+x2, y+y2), grid)):
                self.neighbours.append(grid[x+x1+x2][y+y1+y2])

class Button:
    def __init__(self, x_pos, y_pos, width, height, text):
        self.color = WHITE
        self.rect = pygame.Rect(x_pos, y_pos, width, height)
        self.text = font.render(text, True, BLACK)
        self.text_rect = self.text.get_rect(center=(x_pos + width//2, y_pos + height//2))

    def get_rect(self):
        return self.rect

    def draw(self):
        pygame.draw.rect(WIN, self.color, self.rect)
        WIN.blit(self.text, self.text_rect)
    
    def selected(self):
        self.color = GREY

    def deselected(self):
        self.color = WHITE

def distance(current, end):
    x1, y1 = current.get_pos()
    x2, y2 = end.get_pos()
    x_dist = abs(x1 - x2)
    y_dist = abs(y1 - y2)
    if x_dist <= y_dist:
        return x_dist*14 + (y_dist - x_dist)*10
    else:
        return y_dist*14 + (x_dist - y_dist)*10

def valid_pos(pos, grid):
    x, y = pos
    result = False
    if 0 <= x and x < SIZE and 0 <= y and y < SIZE:
        if not grid[x][y].is_wall():
            result = True
    return result

def find_node(pos):
    size = WIDTH//SIZE
    x, y = pos
    return x//size, y//size

def make_grid(start, end):
    grid = []
    for i in range(SIZE):
        grid.append([])
        for j in range(SIZE):
            grid[i].append(Node((i, j)))
    start.put_in_grid(grid)
    end.put_in_grid(grid)
    return grid

def draw_grid(grid):
    for row in grid:
        for node in row:
            node.draw()
    for number in range(0, WIDTH+1, WIDTH//SIZE):
        pygame.draw.line(WIN, BLACK, (0, number), (WIDTH, number))
        pygame.draw.line(WIN, BLACK, (number, 0), (number, WIDTH))
    pygame.display.update()

def show_path(came_from, current, grid):
    while current in came_from:
        current = came_from[current]
        if not current.is_destination():
            current.set_path()
        draw_grid(grid)

def astar(grid, start, end):
    count = 0
    open = PriorityQueue()
    open.put((0, count, start))
    came_from = {}
    g_cost = {}
    g_cost[start] = 0
    f_cost = {}
    f_cost[start] = distance(start, end)
    open_hash = {start}
    paused = False
    while not open.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
        if not paused:
            current = open.get()[2]
            open_hash.remove(current)
            if current == end:
                show_path(came_from, current, grid)
                return True
            current.update_neighbours(grid)
            x1, y1 = current.get_pos()
            for neighbour in current.neighbours:
                x2, y2 = neighbour.get_pos()
                new_g_cost = g_cost[current] + 10 + 4*((abs(x1 - x2) + abs(y1 - y2) + 1)%2)
                if neighbour not in g_cost or new_g_cost < g_cost[neighbour]:
                    g_cost[neighbour] = new_g_cost
                    f_cost[neighbour] = g_cost[neighbour] + distance(neighbour, end)
                    came_from[neighbour] = current
                    if not neighbour in open_hash:
                        count += 1
                        open.put((f_cost[neighbour], count, neighbour))
                        open_hash.add(neighbour)
                        if neighbour != end and not (neighbour.is_path() or neighbour.is_destination()):
                            neighbour.set_open()
            draw_grid(grid)
            if current != start and not (current.is_path() or current.is_destination()):
                current.set_closed()
    return False

def dijkstra(grid, start, end):
    count = 0
    open = PriorityQueue()
    open.put((0, count, start))
    open_hash = {start}
    came_from = {}
    paused = False
    while not open.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
        if not paused:
            current_cost, dummy, current = open.get()
            if current == end:
                show_path(came_from, current, grid)
                return True
            current.update_neighbours(grid)
            x1, y1 = current.get_pos()
            for neighbour in current.neighbours:
                if neighbour not in open_hash:
                    x2, y2 = neighbour.get_pos()
                    new_cost = current_cost + 10 + 4*((abs(x1 - x2) + abs(y1 - y2) + 1)%2)
                    count += 1
                    open.put((new_cost, count, neighbour))
                    open_hash.add(neighbour)
                    came_from[neighbour] = current
                    if neighbour != end and not (neighbour.is_path() or neighbour.is_destination()):
                            neighbour.set_open()
            draw_grid(grid)
            if current != start and not (current.is_path() or current.is_destination()):
                current.set_closed()
    return False

def maze(pos, grid):
    draw_grid(grid)
    x, y = pos
    available = {0, 1, 2, 3}
    index = -1
    while bool(available):
        while not index in available:
            index = randint(0, 4) - 1
        available.remove(index)
        x1, y1 = directions[index]
        for i in range(-1, 2):
            new_x = x+x1+i*abs(y1)
            new_y = y+y1+i*abs(x1)
            if not (valid_pos((new_x, new_y), grid) and valid_pos((new_x+x1, new_y+y1), grid)):
                break
        else:
            if not grid[x+x1][y+y1].is_destination():
                grid[x+x1][y+y1].set_wall()
                maze((x+x1, y+y1), grid)

def main():
    WIN.fill(WHITE)
    start = Node((0, 0))
    start.set_start()
    end = Node((SIZE-1, SIZE-1))
    end.set_end()
    grid = make_grid(start, end)
    search = 0
    text = font.render('Algorithm' , True , BLACK)
    text_rect = text.get_rect(center=(WIDTH+SIDE_BAR//2, SIDE_BAR//4))
    WIN.blit(text, text_rect)
    pygame.draw.line(WIN, BLACK, (WIDTH, SIDE_BAR//2 - 2), (WIDTH+SIDE_BAR, SIDE_BAR//2 - 2), 2)
    buttons = [
        Button(WIDTH+1, SIDE_BAR//2, SIDE_BAR, SIDE_BAR//2, 'A*'),
        Button(WIDTH+1, SIDE_BAR, SIDE_BAR, SIDE_BAR//2, 'Dijkstra'),
        Button(WIDTH+1, 3*SIDE_BAR//2, SIDE_BAR, SIDE_BAR//2, 'Maze'),
        Button(WIDTH+1, 2*SIDE_BAR, SIDE_BAR, SIDE_BAR//2, 'Add Flag')
    ]
    buttons[0].selected()
    for button in buttons:
        button.draw()
    change = False
    make_wall = False
    add_flag = False
    flags = []
    running = True
    while running:
        draw_grid(grid)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            pos = pygame.mouse.get_pos()
            x, y = find_node(pos)
            if event.type == pygame.MOUSEBUTTONUP:
                if change or make_wall:
                    change = make_wall = False
                else:
                    if WIDTH <= pos[0]:
                        for button in buttons:
                            if button.get_rect().collidepoint(event.pos):
                                if buttons.index(button) == 2:
                                    maze((SIZE//2, SIZE//2), grid)
                                elif buttons.index(button) == 3:
                                    add_flag = not add_flag
                                else:
                                    search = buttons.index(button)
            if pygame.mouse.get_pressed()[0]:
                if pos[0] < WIDTH:
                    current = grid[x][y]
                    if current.is_destination():
                        if not (change or add_flag or make_wall):
                            move_node = current
                            prev_node = Node(current.get_pos())
                            change = True
                    elif change:
                        prev_node.put_in_grid(grid)
                        prev_node = current
                        move_node.change_pos(current.get_pos())
                        move_node.put_in_grid(grid)
                    elif add_flag:
                        current.set_flag()
                        flags.append(current)
                        add_flag = False
                    else:
                        make_wall = True
                        current.set_wall()
            elif pygame.mouse.get_pressed()[2]:
                if pos[0] < WIDTH:
                    current = grid[x][y]
                    if not (current.is_start() or current.is_end()):
                        if current.is_flag():
                            flags.remove(current)
                        current.set_default()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    for row in grid:
                        for node in row:
                            if valid_pos(node.get_pos(), grid) and not node.is_destination():
                                node.set_default()
                    flags.append(end)
                    prev = start
                    for flag in flags:
                        if search:
                            dijkstra(grid, prev, flag)
                        else:
                            astar(grid, prev, flag)
                        prev = flag
                    flags.remove(end)
                elif event.key == pygame.K_c:
                    grid = make_grid(start, end)
                    flags.clear()
        for button in buttons:
            if button.get_rect().collidepoint(pos) or buttons.index(button) == search or (buttons.index(button) == 3 and add_flag):
                button.selected()
            else:
                button.deselected()
            button.draw()
        pygame.draw.line(WIN, BLACK, (WIDTH, 3*SIDE_BAR//2 - 2), (WIDTH+SIDE_BAR, 3*SIDE_BAR//2 - 2), 2)
    pygame.quit()

main()
