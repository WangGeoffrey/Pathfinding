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
    def __init__(self, x_pos, y_pos):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.color = WHITE
        self.neighbours = []

    def get_pos(self):
        return self.x_pos, self.y_pos

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

    def update_neighbours(self, grid):
        self.neighbours.clear()
        x, y = self.get_pos()

        if valid_pos((x-1, y), grid):
            self.neighbours.append(grid[x-1][y])
        if valid_pos((x, y-1), grid):
            self.neighbours.append(grid[x][y-1])
        if valid_pos((x+1, y), grid):
            self.neighbours.append(grid[x+1][y])
        if valid_pos((x, y+1), grid):
            self.neighbours.append(grid[x][y+1])

        if valid_pos((x-1, y-1), grid) and (valid_pos((x-1, y), grid) or valid_pos((x, y-1), grid)):
            self.neighbours.append(grid[x-1][y-1])
        if valid_pos((x-1, y+1), grid) and (valid_pos((x-1, y), grid) or valid_pos((x, y+1), grid)):
            self.neighbours.append(grid[x-1][y+1])
        if valid_pos((x+1, y-1), grid) and (valid_pos((x+1, y), grid) or valid_pos((x, y-1), grid)):
            self.neighbours.append(grid[x+1][y-1])
        if valid_pos((x+1, y+1), grid) and (valid_pos((x+1, y), grid) or valid_pos((x, y+1), grid)):
            self.neighbours.append(grid[x+1][y+1])

class Button:
    def __init__(self, x_pos, y_pos, width, height, text):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.width = width
        self.height = height
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

def make_grid():
    grid = []
    for i in range(SIZE):
        grid.append([])
        for j in range(SIZE):
            grid[i].append(Node(i, j))
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
            for neighbour in current.neighbours:
                new_g_cost = g_cost[current] + 10 + 4*((abs(current.x_pos - neighbour.x_pos) + abs(current.y_pos - neighbour.y_pos) + 1)%2)
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
            for neighbour in current.neighbours:
                if neighbour not in open_hash:
                    new_cost = current_cost + 10 + 4*((abs(current.x_pos - neighbour.x_pos) + abs(current.y_pos - neighbour.y_pos) + 1)%2)
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

def maze_check(pos, grid):
    x, y = pos
    if 0 <= x and x < SIZE and 0 <= y and y < SIZE:
        return not grid[x][y].is_wall()
    return False

def maze(current, grid):
    draw_grid(grid)
    pygame.display.update()
    directions = {1, 2, 3, 4}
    num = 0
    x, y = current.get_pos()
    while not len(directions) == 0:
        while not num in directions:
            num = randint(0, 4)
        directions.remove(num)
        if num == 1: #up
            if valid_pos((x, y-1), grid):
                if not grid[x][y-1].is_destination():
                    if maze_check((x-1, y-1), grid) and maze_check((x-1, y-2), grid) and maze_check((x, y-2), grid) and maze_check((x+1, y-2), grid) and maze_check((x+1, y-1), grid):
                        grid[x][y-1].set_wall()
                        maze(grid[x][y-1], grid)
        elif num == 2:#right
            if valid_pos((x+1, y), grid):
                if not grid[x+1][y].is_destination():
                    if maze_check((x+1, y-1), grid) and maze_check((x+2, y-1), grid) and maze_check((x+2, y), grid) and maze_check((x+2, y+1), grid) and maze_check((x+1, y+1), grid):
                        grid[x+1][y].set_wall()
                        maze(grid[x+1][y], grid)
        elif num == 3:#down
            if valid_pos((x, y+1), grid):
                if not grid[x][y+1].is_destination():
                    if maze_check((x-1, y+1), grid) and maze_check((x-1, y+2), grid) and maze_check((x, y+2), grid) and maze_check((x+1, y+2), grid) and maze_check((x+1, y+1), grid):
                        grid[x][y+1].set_wall()
                        maze(grid[x][y+1], grid)
        elif num == 4:#left
            if valid_pos((x-1, y), grid):
                if not grid[x-1][y].is_destination():
                    if maze_check((x-1, y-1), grid) and maze_check((x-2, y-1), grid) and maze_check((x-2, y), grid) and maze_check((x-2, y+1), grid) and maze_check((x-1, y+1), grid):
                        grid[x-1][y].set_wall()
                        maze(grid[x-1][y], grid) 
     
def main():
    WIN.fill(WHITE)
    grid = make_grid()
    start = grid[0][0]
    start.set_start()
    end = grid[SIZE - 1][SIZE - 1]
    end.set_end()
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
    change_start = False
    change_end = False
    make_wall = False
    make_flag = False
    flags = []
    running = True
    prev_color = WHITE
    while running:
        draw_grid(grid)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONUP:
                if not (change_start or change_end or make_wall):
                    if WIDTH <= pos[0]:
                        for button in buttons:
                            if button.get_rect().collidepoint(event.pos):
                                if buttons.index(button) == 2:
                                    maze(grid[SIZE//2][SIZE//2], grid)
                                elif buttons.index(button) == 3:
                                    make_flag = not make_flag
                                else:
                                    temp = search
                                    search = buttons.index(button)
                prev_color = WHITE
                if change_start:
                    change_start = False
                elif change_end:
                    change_end = False
                elif make_wall:
                    make_wall = False
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                x, y = find_node(pos)
                if WIDTH <= pos[0]:
                    pass
                elif change_start:
                    if not grid[x][y].is_end():
                        start.color = prev_color
                        start = grid[x][y]
                        prev_color = start.color
                        start.set_start()
                elif change_end:
                    if not grid[x][y].is_start():
                        end.color = prev_color
                        end = grid[x][y]
                        prev_color = end.color
                        end.set_end()
                elif make_flag:
                    if not grid[x][y].is_destination():
                        grid[x][y].set_flag()
                        flags.append(grid[x][y])
                        make_flag = False
                elif start.get_pos() == (x, y) and not change_end:
                    if not make_wall:
                        change_start = True
                elif end.get_pos() == (x, y) and not change_start:
                    if not make_wall:
                        change_end = True
                else:
                    make_wall = True
                    if not grid[x][y].is_flag():
                        grid[x][y].set_wall()
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                x, y = find_node(pos)
                if WIDTH <= pos[0]:
                    pass
                elif not (start == grid[x][y] or end == grid[x][y]):
                    if grid[x][y].is_flag():
                        flags.remove(grid[x][y])
                    grid[x][y].set_default()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    for row in grid:
                        for node in row:
                            if valid_pos(node.get_pos(), grid):
                                node.set_default()
                    start.set_start()
                    end.set_end()
                    for flag in flags:
                        flag.set_flag()
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
                    grid = make_grid()
                    start = grid[start.x_pos][start.y_pos]
                    start.set_start()
                    end = grid[end.x_pos][end.y_pos]
                    end.set_end()
                    flags.clear()
        pos = pygame.mouse.get_pos()
        for button in buttons:
            if button.get_rect().collidepoint(pos) or buttons.index(button) == search or (buttons.index(button) == 3 and make_flag):
                button.selected()
            else:
                button.deselected()
            button.draw()
        pygame.draw.line(WIN, BLACK, (WIDTH, 3*SIDE_BAR//2 - 2), (WIDTH+SIDE_BAR, 3*SIDE_BAR//2 - 2), 2)
    pygame.quit()

main()
