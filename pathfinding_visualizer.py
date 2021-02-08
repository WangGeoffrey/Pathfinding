import pygame
from queue import PriorityQueue
from random import choice

pygame.init()
WIDTH = 612
ACROSS = 51
SIZE = WIDTH//ACROSS
SIDE_BAR = 100
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
LIGHTGREY = (192, 192, 192)
TURQUOISE = (64, 224, 208)

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

    def draw(self):
        pygame.draw.rect(WIN, self.color, (self.x_pos*SIZE, self.y_pos*SIZE, SIZE, SIZE))

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

    def update_neighbors(self, grid):
        self.neighbors.clear()
        x, y = self.get_pos()
        for index in range(len(directions)):
            x1, y1 = directions[index]
            x2, y2 = directions[(index+1)%4]
            if valid_pos((x+x1, y+y1), grid):
                self.neighbors.append(grid[x+x1][y+y1])
            if valid_pos((x+x1+x2, y+y1+y2), grid) and (valid_pos((x+x1, y+y1), grid) or valid_pos((x+x2, y+y2), grid)):
                self.neighbors.append(grid[x+x1+x2][y+y1+y2])

class Button: #Toggle button
    def __init__(self, x_pos, y_pos, width, height, text):
        self.color = WHITE
        self.rect = pygame.Rect(x_pos, y_pos, width, height)
        self.text = font.render(text, True, BLACK)
        self.text_rect = self.text.get_rect(center=(x_pos + width//2, y_pos + height//2))
        self.toggle = False

    def get_rect(self):
        return self.rect

    def draw(self):
        pygame.draw.rect(WIN, self.color, self.rect)
        WIN.blit(self.text, self.text_rect)

    def hovered(self):
        if self.color != GREY:
            self.color = LIGHTGREY

    def clicked(self):
        self.toggle = not self.toggle

    def is_selected(self):
        return self.toggle
    
    def selected(self):
        if self.toggle:
            self.color = GREY
        else:
            self.color = WHITE

class Button2(Button): #Execute button
    def __init__(self, x_pos, y_pos, width, height, text, function):
        self.color = WHITE
        self.rect = pygame.Rect(x_pos, y_pos, width, height)
        self.text = font.render(text, True, BLACK)
        self.text_rect = self.text.get_rect(center=(x_pos + width//2, y_pos + height//2))
        self.execute = function

    def clicked(self):
        self.color = GREY
        self.draw()
        self.execute()

    def selected(self):
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
    if 0 <= x < ACROSS and 0 <= y < ACROSS:
        if not grid[x][y].is_wall():
            result = True
    return result

def make_grid(start, end):
    grid = []
    for i in range(ACROSS):
        grid.append([])
        for j in range(ACROSS):
            grid[i].append(Node((i, j)))
    start.put_in_grid(grid)
    end.put_in_grid(grid)
    return grid

def draw_grid(grid):
    for row in grid:
        for node in row:
            node.draw()
    for number in range(0, WIDTH+1, SIZE):
        pygame.draw.line(WIN, BLACK, (0, number), (WIDTH, number))
        pygame.draw.line(WIN, BLACK, (number, 0), (number, WIDTH))
    pygame.display.update()

def show_path(came_from, current, grid):
    while current in came_from:
        current = came_from[current]
        if not current.is_destination():
            current.set_path()
        draw_grid(grid)

def exit():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            return True

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
    while not open.empty():
        if exit():
            return False
        current = open.get()[2]
        open_hash.remove(current)
        if current == end:
            show_path(came_from, current, grid)
            return True
        current.update_neighbors(grid)
        x1, y1 = current.get_pos()
        for neighbor in current.get_neighbors():
            x2, y2 = neighbor.get_pos()
            new_g_cost = g_cost[current] + 10 + 4*((abs(x1 - x2) + abs(y1 - y2) + 1)%2)
            if neighbor not in g_cost or new_g_cost < g_cost[neighbor]:
                g_cost[neighbor] = new_g_cost
                f_cost[neighbor] = g_cost[neighbor] + distance(neighbor, end)
                came_from[neighbor] = current
                if not neighbor in open_hash:
                    count += 1
                    open.put((f_cost[neighbor], count, neighbor))
                    open_hash.add(neighbor)
                    if neighbor != end and not (neighbor.is_path() or neighbor.is_destination()):
                        neighbor.set_open()
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
    while not open.empty():
        if exit():
            return False
        current_cost, dummy, current = open.get()
        if current == end:
            show_path(came_from, current, grid)
            return True
        current.update_neighbors(grid)
        x1, y1 = current.get_pos()
        for neighbor in current.get_neighbors():
            if neighbor not in open_hash:
                x2, y2 = neighbor.get_pos()
                new_cost = current_cost + 10 + 4*((abs(x1 - x2) + abs(y1 - y2) + 1)%2)
                count += 1
                open.put((new_cost, count, neighbor))
                open_hash.add(neighbor)
                came_from[neighbor] = current
                if neighbor != end and not (neighbor.is_path() or neighbor.is_destination()):
                        neighbor.set_open()
        draw_grid(grid)
        if current != start and not (current.is_path() or current.is_destination()):
            current.set_closed()
    return False

def maze(pos, grid): #Generate maze by making walls
    draw_grid(grid)
    x, y = pos
    d = directions.copy()
    while bool(d):
        if exit():
            return False
        x1, y1 = d.pop(d.index(choice(d)))
        for i in range(-1, 2):
            new_x = x+x1+i*abs(y1)
            new_y = y+y1+i*abs(x1)
            if not (valid_pos((new_x, new_y), grid) and valid_pos((new_x+x1, new_y+y1), grid)):
                break
        else:
            if not grid[x+x1][y+y1].is_destination():
                grid[x+x1][y+y1].set_wall()
                maze((x+x1, y+y1), grid)

def gen_maze(start, end, grid, flags, mode):
    for col in grid:
        for node in col:
            node.set_default()
    if start.get_pos() != (0, 0):
        x, y = start.get_pos()
        start.change_pos((0, 0))
        start.put_in_grid(grid)
        grid[x][y] = Node((x, y))
    if end.get_pos() != (ACROSS-1, ACROSS-1):
        x, y = end.get_pos()
        end.change_pos((ACROSS-1, ACROSS-1))
        end.put_in_grid(grid)
        grid[x][y] = Node((x, y))
    flags.clear()
    grow_tree(mode, grid)
    start.set_start()
    end.set_end()

def grow_tree(mode, grid): #Generate maze by removing walls
    nodes = {}
    d = {(x*2, y*2) for x, y in directions}
    for i in range(0, ACROSS):
        for j in range(i, ACROSS):
            if i%2 == 1 or j%2 == 1:
                grid[i][j].set_wall()
                grid[j][i].set_wall()
            else:
                nodes[grid[i][j]] = {grid[i+v][j+h] for v, h in d if valid_pos((i+v, j+h), grid)}
                nodes[grid[j][i]] = {grid[j+v][i+h] for v, h in d if valid_pos((j+v, i+h), grid)}
        draw_grid(grid)
    if mode:
        get_node = lambda: check[len(check)-1]
    else:
        get_node = lambda: check[check.index(choice(check))]        #1
        # get_node = lambda: check[check.index(set(check).pop())]   #2
    check = [set(nodes.keys()).pop()]
    removed = set()
    while bool(check):
        if exit():
            return False
        draw_grid(grid)
        current = get_node()
        neighbors = nodes.get(current)
        neighbors = neighbors.difference(set(check).union(removed))
        if bool(neighbors):
            neighbor = choice(list(neighbors))    #1
            neighbors.remove(neighbor)            #1
            # neighbor = neighbors.pop()          #2
        if not bool(neighbors):
            check.remove(current)
            removed.add(current)
        if not (neighbor in check or neighbor in removed):
            check.append(neighbor)
            x, y = current.get_pos()
            x1, y1 = neighbor.get_pos()
            grid[x+(x1-x)//2][y+(y1-y)//2].set_default()

def main():
    WIN.fill(WHITE)
    start = Node((0, 0))
    start.set_start()
    end = Node((ACROSS-1, ACROSS-1))
    end.set_end()
    grid = make_grid(start, end)
    text = font.render('Algorithm' , True , BLACK)
    text_rect = text.get_rect(center=(WIDTH+SIDE_BAR//2, SIDE_BAR//4))
    WIN.blit(text, text_rect)
    pygame.draw.line(WIN, BLACK, (WIDTH, SIDE_BAR//2 - 2), (WIDTH+SIDE_BAR, SIDE_BAR//2 - 2), 2)
    buttons = [
        Button(WIDTH+1, SIDE_BAR//2, SIDE_BAR, SIDE_BAR//2, 'A*'),
        Button(WIDTH+1, SIDE_BAR, SIDE_BAR, SIDE_BAR//2, 'Dijkstra'),
        Button(WIDTH+1, 3*SIDE_BAR//2, SIDE_BAR, SIDE_BAR//2, 'Add Flag'),
        Button2(WIDTH+1, 2*SIDE_BAR, SIDE_BAR, SIDE_BAR//2, 'Maze', lambda: maze((ACROSS//2, ACROSS//2), grid)),
        Button2(WIDTH+1, 5*SIDE_BAR//2, SIDE_BAR, SIDE_BAR//2, 'Recursive', lambda: gen_maze(start, end, grid, flags, True)),
        Button2(WIDTH+1, 3*SIDE_BAR, SIDE_BAR, SIDE_BAR//2, 'Prim\'s', lambda: gen_maze(start, end, grid, flags, False))
    ]
    buttons[0].clicked()
    for button in buttons:
        button.draw()
    search = lambda: astar(grid, prev, next)
    change = False
    make_wall = False
    flags = []
    running = True
    while running:
        draw_grid(grid)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            pos = pygame.mouse.get_pos()
            x, y = tuple(elem//(SIZE) for elem in pos)
            if event.type == pygame.MOUSEBUTTONUP:
                if WIDTH <= pos[0]:
                    for button in buttons:
                        if button.get_rect().collidepoint(pos):
                            if buttons.index(button) > 1:
                                pass
                            elif buttons.index(button) > 0:
                                buttons[0].clicked()
                                search = lambda: dijkstra(grid, prev, next)
                            else:
                                buttons[1].clicked()
                                search = lambda: astar(grid, prev, next)
                            button.clicked()
                change = make_wall = False
            if pygame.mouse.get_pressed()[0]:
                if pos[0] < WIDTH:
                    current = grid[x][y]
                    if current.is_destination():
                        if not (change or buttons[2].is_selected() or make_wall):
                            move_node = current
                            prev_node = Node(current.get_pos())
                            change = True
                    elif change:
                        prev_node.put_in_grid(grid)
                        prev_node = current
                        move_node.change_pos(current.get_pos())
                        move_node.put_in_grid(grid)
                    elif buttons[2].is_selected():
                        current.set_flag()
                        flags.append(current)
                        buttons[2].clicked()
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
                            if not (node.is_destination() or node.is_wall()):
                                node.set_default()
                    flags.append(end)
                    prev = start
                    for next in flags:
                        search()
                        prev = next
                    flags.remove(end)
                elif event.key == pygame.K_c:
                    grid = make_grid(start, end)
                    flags.clear()
        for button in buttons:
            button.selected()
            if button.get_rect().collidepoint(pos):
                button.hovered()
            button.draw()
        pygame.draw.line(WIN, BLACK, (WIDTH, 3*SIDE_BAR//2 - 2), (WIDTH+SIDE_BAR, 3*SIDE_BAR//2 - 2), 2)
    pygame.quit()

main()
