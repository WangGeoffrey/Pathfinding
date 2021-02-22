import pygame
import settings
import objects as obj
import algorithms as algo

WIDTH = settings.WIDTH
ACROSS = settings.ACROSS
SIZE = settings.SIZE
SIDE_BAR = settings.SIDE_BAR
WIN = settings.WIN
font = settings.font
pygame.display.set_caption("Pathfinding Visualizer")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

def main():
    WIN.fill(WHITE)
    grid = obj.Grid()
    labels = ('Algorithm', 'Flags', 'Maze Gen.')
    for i in range(len(labels)):
        text = font.render(labels[i] , True , BLACK)
        text_rect = text.get_rect(center=(WIDTH+SIDE_BAR//2, 2*i*SIDE_BAR + SIDE_BAR//4))
        WIN.blit(text, text_rect)
        pygame.draw.line(WIN, BLACK, (WIDTH, (4*(i+1)-3)*SIDE_BAR//2 - 2), (WIDTH+SIDE_BAR, (4*(i+1)-3)*SIDE_BAR//2 - 2), 2)
    buttons = [
        obj.Button3(WIDTH+1, SIDE_BAR//2, SIDE_BAR, SIDE_BAR//2, 'A*', lambda: buttons[1].deselect()),
        obj.Button3(WIDTH+1, SIDE_BAR, SIDE_BAR, SIDE_BAR//2, 'Dijkstra', lambda: buttons[0].deselect()),
        obj.Button(WIDTH+1, 5*SIDE_BAR//2, SIDE_BAR, SIDE_BAR//2, 'Add Flag'),
        obj.Button(WIDTH+1, 3*SIDE_BAR, SIDE_BAR, SIDE_BAR//2, 'Shortest Path'),
        obj.Button2(WIDTH+1, 9*SIDE_BAR//2, SIDE_BAR, SIDE_BAR//2, 'Maze', lambda: algo.maze((ACROSS//2, ACROSS//2), grid)),
        obj.Button2(WIDTH+1, 5*SIDE_BAR, SIDE_BAR, SIDE_BAR//2, 'Recursive', lambda: algo.grow_tree(grid, True)),
        obj.Button2(WIDTH+1, 11*SIDE_BAR//2, SIDE_BAR, SIDE_BAR//2, 'Prim\'s', lambda: algo.grow_tree(grid, False))
    ]
    buttons[0].select()
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
                            running = bool(button.click()-1)
                make_wall = False
            if pygame.mouse.get_pressed()[0]:
                if pos[0] < WIDTH:
                    current = grid.get_node((x, y))
                    if current.is_destination():
                        if not (make_wall or buttons[2].is_selected()):
                            grid.move_node(current)
                    elif buttons[2].is_selected():
                        current.set_flag()
                        grid.add_flag(current)
                        buttons[2].deselect()
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
                    if buttons[0].is_selected():
                        search = lambda: algo.astar(grid, prev, next)
                    else:
                        search = lambda: algo.dijkstra(grid, prev, next)
                    if buttons[3].is_selected():
                        prev = grid.get_start()
                        costs = {}
                        came_from = {}
                        path_exists = True
                        for next in grid.get_flags():
                            temp = search()
                            try:
                                costs[(prev, next)], came_from[(prev, next)] = temp
                            except: #Path not found or function exited
                                running = bool(temp-1)
                                path_exists = False
                                break
                        if path_exists:
                            flags = grid.get_flags_end()
                            for i in range(len(flags)):
                                prev = flags[i]
                                for j in range(i+1, len(flags)):
                                    next = flags[j]
                                    temp = search()
                                    try:
                                        costs[(prev, next)], came_from[(prev, next)] = temp
                                    except: #Path not found or function exited
                                        running = bool(temp-1)
                                        path_exists = False
                                        break
                        if path_exists:
                            path, distance = algo.shortest_path(costs, len(grid.get_flags()), set(), grid.get_start(), grid.get_end(), [], 0)
                            connect = grid.get_start()
                            for key in path:
                                if came_from[key][0] != connect:
                                    came_from[key] = reversed(came_from[key])
                                for node in came_from[key]:
                                    if not node.is_destination():
                                        node.set_path()
                                        grid.draw()
                                else:
                                    connect = node
                    else:
                        prev = grid.get_start()
                        for next in grid.get_flags_end():
                            temp = search()
                            try:
                                came_from = temp[1]
                                for node in reversed(came_from):
                                    if not node.is_destination():
                                        node.set_path()
                                        grid.draw()
                            except: #Path not found or function exited
                                running = bool(temp-1)
                                break
                            prev = next
                elif event.key == pygame.K_c:
                    grid.clear_all()
        if not (bool(grid.get_flags())):
            buttons[3].deselect()
        pos = pygame.mouse.get_pos()
        for button in buttons:
            button.clear()
            if button.get_rect().collidepoint(pos):
                button.hovered()
            button.draw()
    pygame.quit()

main()
