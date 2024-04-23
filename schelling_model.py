from random import sample, shuffle
from itertools import product
from time import time

def neighborhood(grid, x, y):
    length = len(grid)
    width = len(grid[0])
    for dx, dy in product(range(-1, 2), repeat=2):
        if (dx or dy) and 0 <= x + dx < length and 0 <= y + dy < width:
            yield x + dx, y + dy

def is_satisfied(grid, x, y, p, val=None):
    neighbors = [(nx, ny) for nx, ny in neighborhood(grid, x, y) if grid[nx][ny] != -1]
    like_minded = [0 for nx, ny in neighbors if grid[nx][ny] == (grid[x][y] if val is None else val)]
    return len(like_minded) >= len(neighbors) * p

def unsatisfied_spaces(grid, p):
    coords = []
    for x, y in product(range(len(grid)), repeat=2):
        if not is_satisfied(grid, x, y, p):
            coords.append((x, y))
    shuffle(coords)
    return coords

def satisfactory_space(grid, x, y, p):
    val = grid[x][y]
    to_flood = {(x, y)}
    seen = {(x, y)}
    while to_flood:
        next_flood = set()
        for x, y in to_flood:
            for nx, ny in neighborhood(grid, x, y):
                if (nx, ny) not in seen:
                    if grid[nx][ny] == -1 and is_satisfied(grid, nx, ny, p, val=val):
                        return nx, ny
                    seen.add((nx, ny))
                    next_flood.add((nx, ny))
        to_flood = next_flood

def simulate_schelling(p, q):
    length = 50
    width = 50
    grid = [[0 for _ in range(length)] for _ in range(width)]
    empties = round(length * width * 0.1)
    num_agents = round(q * length * width) - empties / 2
    for i, space in enumerate(sample(range(length * width), length * width)):
        x = space // 50
        y = space % 50
        grid[x][y] = 0 if i < num_agents else (-1 if i < num_agents + empties else 1)

    prev_unsat_count = 0
    time_changed = time()
    start = time()
    while unsatisfied := unsatisfied_spaces(grid, p):
        if time() - start >= 120:
            break
        if len(unsatisfied) != prev_unsat_count:
            prev_unsat_count = len(unsatisfied)
            time_changed = time()
        elif time() - time_changed >= 5:
            break

        moved = False
        for x, y in unsatisfied:
            new_loc = satisfactory_space(grid, x, y, p)
            if new_loc:
                moved = True
                grid[new_loc[0]][new_loc[1]] = grid[x][y]
                grid[x][y] = -1
                break
        if not moved:
            break

    frac_same = 0
    count = 0
    for x, y in product(range(50), repeat=2):
        if grid[x][y] != -1:
            count += 1
            neighbors = [int(grid[nx][ny] == grid[x][y]) for nx, ny in neighborhood(grid, x, y) if grid[nx][ny] != -1]
            if neighbors:
                frac_same += sum(neighbors) / len(neighbors)

    return grid, frac_same / (length * width - empties)

for q in [1/2, 3/4]:
    print(f'--------------q={q}--------------')
    for p in range(9):
        frac_same = 0
        for trial in range(10):
            frac_same += simulate_schelling(p / 8, q)[1]
        print(f'p={p / 8}: {frac_same / 10}')
