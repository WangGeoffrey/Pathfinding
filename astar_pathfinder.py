import pygame
import math
from queue import PriorityQueue

WIDTH = 600
SIZE = 50
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Pathfinder")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
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

    def is_wall(self):
        return self.color == GREY

    def set_start(self):
        self.color = GREEN
    
    def set_end(self):
        self.color = RED

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
        current.set_path()
        draw_grid(grid)

def search(grid, start, end):
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
                    if paused:
                        paused = False
                    else:
                        paused = True
        if not paused:
            current = open.get()[2]
            open_hash.remove(current)
            if current == end:
                show_path(came_from, current, grid)
                end.set_end()
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
                        neighbour.set_open()
            draw_grid(grid)
            if current != start:
                current.set_closed()
    return False
     
def main():
    WIN.fill(WHITE)
    grid = make_grid()
    start = grid[0][0]
    start.set_start()
    end = grid[SIZE - 1][SIZE - 1]
    end.set_end()
    change_start = False
    change_end = False
    make_wall = False
    running = True
    prev_color = WHITE
    while running:
        draw_grid(grid)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONUP:
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
                if change_start:
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
                elif start.get_pos() == (x, y) and not change_end:
                    if not make_wall:
                        change_start = True
                elif end.get_pos() == (x, y) and not change_start:
                    if not make_wall:
                        change_end = True
                else:
                    make_wall = True
                    grid[x][y].set_wall()
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                x, y = find_node(pos)
                if not (start == grid[x][y] or end == grid[x][y]):
                    grid[x][y].set_default()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    for row in grid:
                        for node in row:
                            if valid_pos(node.get_pos(), grid):
                                node.set_default()
                    start.set_start()
                    end.set_end()
                    search(grid, start, end)
                    start.set_start()
                elif event.key == pygame.K_c:
                    grid = make_grid()
                    start = grid[start.x_pos][start.y_pos]
                    start.set_start()
                    end = grid[end.x_pos][end.y_pos]
                    end.set_end()
    pygame.quit()

main()

    