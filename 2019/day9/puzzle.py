import logging
from collections import deque

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

if __name__ == '__main__':
    intcodes = parse('input.txt')
    comp1 = computer('Computer 1', intcodes, [1]).run()
    comp2 = computer('Computer 1', intcodes, [2]).run()

    print('Part 1: {}'.format(comp1.outputs[0]))
    print('Part 2: {}'.format(comp2.outputs[0]))
