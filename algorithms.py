import pygame
from queue import PriorityQueue
from random import choice

directions = [(0, -1), (1, 0), (0, 1), (-1, 0)] #[up, right, down, left]

def exit():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return 1
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                return 2
    return 0

def get_path(came_from, current):
    result = [current]
    while current in came_from:
        current = came_from[current]
        result.append(current)
    return result

def astar(grid, start, end):
    count = 0
    open = PriorityQueue()
    open.put((0, count, start))
    came_from = {}
    g_cost = {start: 0}
    f_cost = {start: start.distance(end)}
    open_hash = {start}
    while not open.empty():
        escape = exit()
        if escape:
            return escape
        current = open.get()[2]
        open_hash.remove(current)
        if current == end:
            return g_cost[current], get_path(came_from, current)
        current.update_neighbors(grid)
        x1, y1 = current.get_pos()
        for neighbor in current.get_neighbors():
            x2, y2 = neighbor.get_pos()
            new_g_cost = g_cost[current] + 10 + 4*((abs(x1 - x2) + abs(y1 - y2) + 1)%2)
            if not neighbor in g_cost or new_g_cost < g_cost[neighbor]:
                g_cost[neighbor] = new_g_cost
                f_cost[neighbor] = g_cost[neighbor] + neighbor.distance(end)
                came_from[neighbor] = current
                if not neighbor in open_hash:
                    count += 1
                    open.put((f_cost[neighbor], count, neighbor))
                    open_hash.add(neighbor)
                    if not (neighbor.is_path() or neighbor.is_destination()):
                        neighbor.set_open()
        grid.draw()
        if not (current.is_path() or current.is_destination()):
            current.set_closed()
    return False

def dijkstra(grid, start, end):
    count = 0
    open = PriorityQueue()
    open.put((0, count, start))
    open_hash = {start}
    came_from = {}
    while not open.empty():
        escape = exit()
        if escape:
            return escape
        current_cost, dummy, current = open.get()
        if current == end:
            return current_cost, get_path(came_from, current)
        current.update_neighbors(grid)
        x1, y1 = current.get_pos()
        for neighbor in current.get_neighbors():
            if not neighbor in open_hash:
                x2, y2 = neighbor.get_pos()
                new_cost = current_cost + 10 + 4*((abs(x1 - x2) + abs(y1 - y2) + 1)%2)
                count += 1
                open.put((new_cost, count, neighbor))
                open_hash.add(neighbor)
                came_from[neighbor] = current
                if not (neighbor.is_path() or neighbor.is_destination()):
                        neighbor.set_open()
        grid.draw()
        if not (current.is_path() or current.is_destination()):
            current.set_closed()
    return False

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

def maze(pos, grid): #Generate maze by making walls
    grid.draw()
    x, y = pos
    d = directions.copy()
    while bool(d):
        escape = exit()
        if escape:
            return escape
        x1, y1 = d.pop(d.index(choice(d)))
        for i in range(-1, 2):
            new_x = x+x1+i*abs(y1)
            new_y = y+y1+i*abs(x1)
            if not (grid.valid_pos((new_x, new_y)) and grid.valid_pos((new_x+x1, new_y+y1))):
                break
        else:
            if not grid.get_node((x+x1, y+y1)).is_destination():
                grid.get_node((x+x1, y+y1)).set_wall()
                stop = maze((x+x1, y+y1), grid)
                if stop:
                    return stop
    return False

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
        escape = exit()
        if escape:
            return escape
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
            x1, y1 = current.get_pos()
            x2, y2 = neighbor.get_pos()
            grid.get_node((x1+(x2-x1)//2, y1+(y2-y1)//2)).set_default()
    return False
