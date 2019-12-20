from collections import deque
import random
import numpy as np

def parse(path):
    with open(path, mode='r') as f:
        return [int(x) for x in f.readline().split(',')]

class computer:
    def __init__(self, name, program, inputs):
        self.name    = name
        self.program = list(program)
        self.ip      = 0
        self.base    = 0
        self.outputs = []
        self.inputs  = deque(inputs)
        self.paused  = True

        ext = [0] * 1000000
        self.program.extend(ext)

    def run(self):
        self.paused = False
        opcode      = None

        while opcode != 99 and not self.paused:
            opcode, c, b, a = self.instruction()
            if   opcode == 1: self.add(c, b, a)
            elif opcode == 2: self.mul(c, b, a)
            elif opcode == 3: self.put(c)
            elif opcode == 4: self.get(c)
            elif opcode == 5: self.jumpt(c, b)
            elif opcode == 6: self.jumpf(c, b)
            elif opcode == 7: self.less(c, b, a)
            elif opcode == 8: self.equal(c, b, a)
            elif opcode == 9: self.rbase(c)
            else:
                break
        return self

    def instruction(self):
        opcode = self.program[self.ip] % 100
        c = (self.program[self.ip] // 100)  % 10
        b = (self.program[self.ip] // 1000) % 10
        a = (self.program[self.ip] // 10000)

        if opcode == 99: return opcode, c, b, a

        if   c == 0: c = self.program[self.ip + 1]
        elif c == 1: c = self.ip + 1
        elif c == 2: c = self.program[self.ip + 1] + self.base

        if   b == 0: b = self.program[self.ip + 2]
        elif b == 1: b = self.ip + 2
        elif b == 2: b = self.program[self.ip + 2] + self.base

        if   a == 0: a = self.program[self.ip + 3]
        elif a == 1: a = self.program[self.ip + 3]
        elif a == 2: a = self.program[self.ip + 3] + self.base

        return opcode, c, b, a

    def add(self, c, b, a):
        self.program[a] = self.program[c] + self.program[b]
        self.ip += 4

    def mul(self, c, b, a):
        self.program[a] = self.program[c] * self.program[b]
        self.ip += 4

    def put(self, c):
        if len(self.inputs) == 0:
            self.paused = True
            return

        self.program[c] = self.inputs.popleft()
        self.ip += 2

    def get(self, c):
        self.outputs.append(self.program[c])
        self.ip += 2

    def jumpt(self, c, b):
        if self.program[c] != 0: self.ip  = self.program[b]
        else:                    self.ip += 3

    def jumpf(self, c, b):
        if self.program[c] == 0: self.ip = self.program[b]
        else:                    self.ip += 3

    def less(self, c, b, a):
        if self.program[c] < self.program[b]: self.program[a] = 1
        else:                                 self.program[a] = 0
        self.ip += 4

    def equal(self, c, b, a):
        if self.program[c] == self.program[b]: self.program[a] = 1
        else:                                  self.program[a] = 0
        self.ip += 4

    def rbase(self, c):
        self.base += self.program[c]
        self.ip += 2

NORTH = 1
SOUTH = 2
WEST  = 3
EAST  = 4

# STATUS
WALL  = 0
MOVED = 1
GOAL  = 2

#MAP
WALL    = 0
UNKNOWN = 1
GOAL    = 2
START   = 3
FREE    = 4

roadrules = {
    NORTH : EAST,
    EAST  : SOUTH,
    SOUTH : WEST,
    WEST  : NORTH
}

def direction(d):
    if d == NORTH: return 'NORTH'
    if d == SOUTH: return 'SOUTH'
    if d == EAST: return 'EAST'
    if d == WEST: return 'WEST'

def stat(s):
    if s == WALL: return 'WALL'
    if s == MOVED: return 'MOVED'
    if s == GOAL: return 'GOAL'

def draw(area):
    out = []
    for x, line in enumerate(area):
        for y, point in enumerate(line):
            if   point == WALL: out.append('#')
            elif point == FREE: out.append(' ')
            elif point == UNKNOWN: out.append('.')
            elif point == GOAL: out.append('x')
            elif point == START: out.append('s')
        out.append('\n')
    out.append('\n')
    print(''.join(out))

def updatemap(area, x, y, facing, status):
    if   status == MOVED: front = FREE
    elif status == WALL:  front = WALL
    elif status == GOAL:  front = GOAL

    if   facing == NORTH: area[x-1, y] = front
    elif facing == SOUTH: area[x+1, y] = front
    elif facing == EAST:  area[x, y+1] = front
    elif facing == WEST:  area[x, y-1] = front

    return area

def explore(area, x, y):
    facing = random.choice(range(1,5))
    if   facing == NORTH: return x - 1, y
    elif facing == SOUTH: return x + 1, y
    elif facing == WEST: return x, y - 1
    elif facing == EAST: return x, y + 1

def maparea(com):
    facing = NORTH

    x, y = 25, 50
    area = np.reshape(np.ones(50*100), (50, 100))
    area[x, y] = START

    while True:
        com.inputs.append(facing)
        com.run()
        status = com.outputs[-1]

        area = updatemap(area, x, y, facing, status)

        if status == GOAL: return area

        x, y = explore(area, x, y)

        draw(area)

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

neighboor = [
    Point(1, 0),   # north
    Point(-1, 0),  # south
    Point(0, -1),  # west
    Point(0, 1),   # east
]

def findgoal(com):
    curr    = Point(0,0)
    visited = {curr : FREE}
    facing  = NORTH

    while True:
        facing = random.choice(range(4))
        while visited.get(curr + neighboor[facing], FREE) == WALL:
            facing = random.choice(range(4))

        com.inputs.append(facing)
        com.run()
        status = com.outputs[-1]

        if status == GOAL:
            visited[curr + neighboor[facing]] = GOAL
            break

        if status == WALL:
            visited[curr + neighboor[facing]] = WALL

        if status == MOVED:
            curr += neighboor[facing]
            visited[curr] = FREE

    return visited

if __name__ == '__main__':
    intcodes = parse('input.txt')
    com = computer('repair', intcodes, [1]).run()

    area = findgoal(com)
    print(area)
    print('Part 1: {}'.format(comp1.outputs[0]))
    print('Part 2: {}'.format(comp2.outputs[0]))