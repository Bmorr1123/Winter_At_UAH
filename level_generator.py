from random import randint


directions = {0: (1, 0), 1: (0, -1), 2: (-1, 0), 3: (0, 1)}
def lerp(x1, y1, x2, y2):
    dist=1
    while x1 != x2 or y1 != y2:
        dist += 1
        if x1 < x2:
            x1 += 1
        elif x1 > x2:
            x1 -= 1
        if y1 < y2:
            y1 += 1
        elif y1 > y2:
            y1 -= 1
        yield x1, y1, dist


max_size = (54, 30)

width, height = max_size

startx, starty, startdir = randint(1, width - 2), randint(1, height - 2), randint(0, 3)
blocks, paths = [], []

def getValidBlocks(origin, direction, check=50):
    x2, y2 = directions[direction]
    x2 *= check
    y2 *= check
    x2 += origin[0]
    y2 += origin[1]
    poss_blocks = []
    # print(*origin, x2, y2)
    for x, y, dist in lerp(*origin, x2, y2):
        print(x, y)
        if (x, y) not in paths and dist >= 2:
            poss_blocks.append((x, y))
        if (x, y) in blocks and dist >= 2:
            poss_blocks.append((x, y))
            break
    return poss_blocks


currentx, currenty, currentdir = startx, starty, startdir
for i in range(33):
    possible_blocks = getValidBlocks((currentx, currenty), currentdir)
    if len(possible_blocks) > 0:
        l = 0
        bx, by = block = possible_blocks[l]
        while not (0 <= bx < width and 0 <= by < height):
            bx, by = block = possible_blocks[l]
        print("Block:", block)
        paths += [(x, y) for x, y, dist in lerp(currentx, currenty, *block)]
        blocks.append(block)
        currentx, currenty = block
        newdir = currentdir
        while (currentdir + newdir) % 2 == 1:
            newdir = randint(0, 3)
        currentdir = newdir

arr = [[" " for x in range(width)] for y in range(height)]
for x, y in blocks:
    arr[y][x] = "0"

for y in arr:
    for x in y:
        print(x, end="")
    print()


