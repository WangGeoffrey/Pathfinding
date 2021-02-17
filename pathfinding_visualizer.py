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

    def get_grid(self):
        return self.grid

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
        result = False
        if 0 <= x < ACROSS and 0 <= y < ACROSS:
            if not self.get_node(pos).is_wall():
                result = True
        return result

    def move_node(self, move_node):
        x, y = pos = move_node.get_pos()
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
                            self.grid[x][y] = move_node
                            move_node.change_pos(mouse)
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
        if not self.grid[0][0].is_start():
            x, y = self.start.get_pos()
            self.grid[x][y] = self.grid[0][0]
            self.grid[x][y].change_pos((x, y))
            self.grid[0][0] = self.start
            self.start.change_pos((0, 0))
        if not self.grid[ACROSS-1][ACROSS-1].is_end():
            x, y = self.end.get_pos()
            self.grid[x][y] = self.grid[ACROSS-1][ACROSS-1]
            self.grid[x][y].change_pos((x, y))
            self.grid[ACROSS-1][ACROSS-1] = self.end
            self.end.change_pos((ACROSS-1, ACROSS-1))
        self.clear_all()
    
    def draw(self):
        for col in self.grid:
            for node in col:
                node.draw()
        for number in range(0, WIDTH+1, SIZE):
            pygame.draw.line(WIN, BLACK, (0, number), (WIDTH, number))
            pygame.draw.line(WIN, BLACK, (number, 0), (number, WIDTH))
        pygame.display.update()

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

def get_path(came_from, current):
    result = []
    while current in came_from:
        result.append(current)
        current = came_from[current]
    return result

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
    g_cost = {start: 0}
    f_cost = {start: start.distance(end)}
    open_hash = {start}
    while not open.empty():
        if exit():
            return False
        current = open.get()[2]
        open_hash.remove(current)
        if current == end:
            return g_cost[current], get_path(came_from, current)
        current.update_neighbors(grid)
        x1, y1 = current.get_pos()
        for neighbor in current.get_neighbors():
            x2, y2 = neighbor.get_pos()
            new_g_cost = g_cost[current] + 10 + 4*((abs(x1 - x2) + abs(y1 - y2) + 1)%2)
            if neighbor not in g_cost or new_g_cost < g_cost[neighbor]:
                g_cost[neighbor] = new_g_cost
                f_cost[neighbor] = g_cost[neighbor] + neighbor.distance(end)
                came_from[neighbor] = current
                if not neighbor in open_hash:
                    count += 1
                    open.put((f_cost[neighbor], count, neighbor))
                    open_hash.add(neighbor)
                    if neighbor != end and not (neighbor.is_path() or neighbor.is_destination()):
                        neighbor.set_open()
        grid.draw()
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
            return current_cost, get_path(came_from, current)
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
        grid.draw()
        if current != start and not (current.is_path() or current.is_destination()):
            current.set_closed()
    return False

def maze(pos, grid): #Generate maze by making walls
    grid.draw()
    x, y = pos
    d = directions.copy()
    while bool(d):
        if exit():
            return False
        x1, y1 = d.pop(d.index(choice(d)))
        for i in range(-1, 2):
            new_x = x+x1+i*abs(y1)
            new_y = y+y1+i*abs(x1)
            if not (grid.valid_pos((new_x, new_y)) and grid.valid_pos((new_x+x1, new_y+y1))):
                break
        else:
            if not grid.get_node((x+x1, y+y1)).is_destination():
                grid.get_node((x+x1, y+y1)).set_wall()
                maze((x+x1, y+y1), grid)

def grow_tree(grid, mode): #Generate maze by removing walls
    grid.reset()
    nodes = {}
    d = {(x*2, y*2) for x, y in directions}
    for i in range(0, ACROSS):
        for j in range(i, ACROSS):
            if i%2 == 1 or j%2 == 1:
                grid.get_node((i, j)).set_wall()
                grid.get_node((j, i)).set_wall()
            else:
                nodes[grid.get_node((i, j))] = {grid.get_node((i+v, j+h)) for v, h in d if grid.valid_pos((i+v, j+h))}
                nodes[grid.get_node((j, i))] = {grid.get_node((j+v, i+h)) for v, h in d if grid.valid_pos((j+v, i+h))}
        grid.draw()
    if mode:
        next_node = lambda: check[len(check)-1]
    else:
        next_node = lambda: check[check.index(choice(check))]        #1
        # get_node = lambda: check[check.index(set(check).pop())]   #2
    check = [set(nodes.keys()).pop()]
    removed = set()
    while bool(check):
        if exit():
            return False
        grid.draw()
        current = next_node()
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
            grid.get_node((x+(x1-x)//2, y+(y1-y)//2)).set_default()

#costs: a dictionary with key as tuple of connected nodes and value as distance between them
def shortest_path(costs, flags, visited, next, end, path, distance):
    if len(path) < flags:
        current = (path, distance)
        distance = 0
        for key in costs:
            if visited.isdisjoint(set(key)) and next in key and not end in key:
                final_path, final_distance = shortest_path(costs, flags, visited.union({next}), key[(key.index(next)+1)%2], end, current[0]+[key], current[1]+costs[key])
                if final_distance < distance or not bool(distance):
                    distance = final_distance
                    path = final_path
    else:
        key = (next, end)
        path.append(key)
        distance += costs[key]
    return path, distance

def main():
    WIN.fill(WHITE)
    grid = Grid()
    labels = ('Algorithm', 'Flags', 'Maze Gen.')
    for i in range(len(labels)):
        text = font.render(labels[i] , True , BLACK)
        text_rect = text.get_rect(center=(WIDTH+SIDE_BAR//2, 2*(i)*SIDE_BAR + SIDE_BAR//4))
        WIN.blit(text, text_rect)
        pygame.draw.line(WIN, BLACK, (WIDTH, (4*(i+1)-3)*SIDE_BAR//2 - 2), (WIDTH+SIDE_BAR, (4*(i+1)-3)*SIDE_BAR//2 - 2), 2)
    buttons = [
        Button(WIDTH+1, SIDE_BAR//2, SIDE_BAR, SIDE_BAR//2, 'A*'),
        Button(WIDTH+1, SIDE_BAR, SIDE_BAR, SIDE_BAR//2, 'Dijkstra'),
        Button(WIDTH+1, 5*SIDE_BAR//2, SIDE_BAR, SIDE_BAR//2, 'Add Flag'),
        Button(WIDTH+1, 3*SIDE_BAR, SIDE_BAR, SIDE_BAR//2, 'Ordered'),
        Button2(WIDTH+1, 9*SIDE_BAR//2, SIDE_BAR, SIDE_BAR//2, 'Maze', lambda: maze((ACROSS//2, ACROSS//2), grid)),
        Button2(WIDTH+1, 5*SIDE_BAR, SIDE_BAR, SIDE_BAR//2, 'Recursive', lambda: grow_tree(grid, True)),
        Button2(WIDTH+1, 11*SIDE_BAR//2, SIDE_BAR, SIDE_BAR//2, 'Prim\'s', lambda: grow_tree(grid, False))
    ]
    buttons[0].clicked()
    buttons[3].clicked()
    search = lambda: astar(grid, prev, next)
    change = False
    make_wall = False
    running = True
    while running:
        grid.draw()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            pos = pygame.mouse.get_pos()
            x, y = tuple(elem//(SIZE) for elem in pos)
            if event.type == pygame.MOUSEBUTTONUP:
                if WIDTH <= pos[0]:
                    for button in buttons:
                        if button.get_rect().collidepoint(pos):
                            if buttons.index(button) == 3:
                                if not bool(grid.get_flags()):
                                    continue
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
                    current = grid.get_node((x, y))
                    if current.is_destination():
                        if not (change or buttons[2].is_selected() or make_wall):
                            move_node = current
                            change = True
                    elif change:
                        grid.move_node(move_node)
                        change = False
                    elif buttons[2].is_selected():
                        current.set_flag()
                        grid.add_flag(current)
                        buttons[2].clicked()
                    else:
                        make_wall = True
                        current.set_wall()
            elif pygame.mouse.get_pressed()[2]:
                if pos[0] < WIDTH:
                    current = grid.get_node((x, y))
                    if not (current.is_start() or current.is_end()):
                        if current.is_flag():
                            grid.remove_flag(current)
                        current.set_default()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    grid.clear_other()
                    if not buttons[3].is_selected():
                        prev = grid.get_start()
                        costs = {}
                        came_from = {}
                        path_exists = True
                        for next in grid.get_flags():
                            try:
                                costs[(prev, next)], came_from[(prev, next)] = search()
                            except: #Path not found
                                path_exists = False
                                break
                        if path_exists:
                            flags = grid.get_flags_end()
                            for i in range(len(flags)):
                                prev = flags[i]
                                for j in range(i+1, len(flags)):
                                    next = flags[j]
                                    try:
                                        costs[(prev, next)], came_from[(prev, next)] = search()
                                    except: #Path not found
                                        path_exists = False
                                        break
                        if path_exists:
                            path, distance = shortest_path(costs, len(grid.get_flags()), set(), grid.get_start(), grid.get_end(), [], 0)
                            connect = grid.get_start()
                            for key in path:
                                if came_from[key][0] != connect:
                                    came_from[key].pop(0)
                                    came_from[key] = reversed(came_from[key])
                                else:
                                    came_from[key].pop(len(came_from[key])-1)
                                for node in came_from[key]:
                                    node.set_path()
                                    grid.draw()
                                else:
                                    connect = node
                    else:
                        prev = grid.get_start()
                        for next in grid.get_flags_end():
                            try:
                                dummy, came_from = search()
                                came_from.pop(0)
                                for node in reversed(came_from):
                                    node.set_path()
                                    grid.draw()
                            except: #Path not found
                                break
                            prev = next
                elif event.key == pygame.K_c:
                    grid.clear_all()
        if not bool(grid.get_flags()) and not buttons[3].is_selected():
            buttons[3].clicked()
        for button in buttons:
            button.selected()
            if button.get_rect().collidepoint(pos):
                button.hovered()
            button.draw()
    pygame.quit()

main()
