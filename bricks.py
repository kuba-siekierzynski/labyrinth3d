from pyglet.gl import *
from pyglet.window import key
import math
import random
import sys

ADOM = {0: '.', 1: '#', 2: '<', 3: '>'}
# tribute to Ancient Domains of Mystery ;)

N, S, E, W = 1, 2, 4, 8
# directions translated into bitnums to store information on all cleared walls in one variable per cell

GO_DIR = {N: (0, -1), S: (0, 1), E: (1, 0), W: (-1, 0)}
# dictionary with directions translated to digging moves

REVERSE = {E: W, W: E, N: S, S: N}
# when a passage is dug from a cell, the other cell obtains the reverse passage, too


class Lab:

    def __init__(self, size, seed):
        self.SIZE = size
        self.seed = seed
        self.lab = list(list(0 for i in range(self.SIZE[0])) for j in range(self.SIZE[1]))
        self.hash_lab = list(list(0 for i in range(self.SIZE[0] * 2 + 1)) for j in range(self.SIZE[1] * 2 + 1))
        random.seed(self.seed)

        def dig(x, y):
            # digs passage from a cell (x, y) in an unvisited cell
            dirs = [N, E, W, S]
            random.shuffle(dirs)
            # shuffles directions each time for more randomness
            for Dir in dirs:
                new_x = x + GO_DIR[Dir][0]
                new_y = y + GO_DIR[Dir][1]
                if (new_y in range(self.SIZE[1])) and \
                        (new_x in range(self.SIZE[0])) and \
                        (self.lab[new_y][new_x] == 0):
                    # checks if the new cell is not visited
                    self.lab[y][x] |= Dir
                    self.lab[new_y][new_x] |= REVERSE[Dir]
                    # if so, apply info on passages to both cells
                    dig(new_x, new_y)
                    # repeat recursively
        dig(self.SIZE[0] // 2, self.SIZE[1] // 2)

        # draw hash_lab border
        for j in range(self.SIZE[1] * 2 + 1):
            self.hash_lab[j][0] = 1
            self.hash_lab[j][self.SIZE[0] * 2] = 1
        for i in range(self.SIZE[0] * 2 + 1):
            self.hash_lab[0][i] = 1
            self.hash_lab[self.SIZE[1] * 2][i] = 1

        # put hash_lab matrix (cross-walls)
        for j in range(0, self.SIZE[1] * 2, 2):
            for i in range(0, self.SIZE[0] * 2, 2):
                self.hash_lab[j][i] = 1

        # translate into roguelike lab
        for j in range(self.SIZE[1]):
            for i in range(self.SIZE[0]):
                if (self.lab[j][i] & S) == 0:
                    self.hash_lab[(j + 1) * 2][(i + 1) * 2 - 1] = 1
                if (self.lab[j][i] & E) == 0:
                    self.hash_lab[(j + 1) * 2 - 1][(i + 1) * 2] = 1
        self.hash_lab[0][1], self.hash_lab[self.SIZE[1] * 2][self.SIZE[0] * 2 - 1] = 0, 0

    def draw_ascii(self):
        # displays the labyrinth in ASCII for reference
        print("Labyrinth of Kuba #" + str(self.seed) + " (" + str(self.SIZE[0]) + "x" + str(self.SIZE[1]) + ")")
        # prints the seed (for reference) and the lab size

        print("_" * (self.SIZE[0] * 2))
        for j in range(self.SIZE[1]):
            if j != 0:
                print("|", end='')
            else:
                print("_", end='')
            for i in range(self.SIZE[0]):
                if self.lab[j][i] & S != 0:
                    print(" ", end='')
                else:
                    print("_", end='')
                if self.lab[j][i] & E != 0:
                    if (self.lab[j][i] | self.lab[j][i + 1]) & S != 0:
                        print(" ", end='')
                    else:
                        print("_", end='')
                elif (j == self.SIZE[1] - 1) & (i == self.SIZE[0] - 1):
                    print("_", end='')
                else:
                    print("|", end='')
            print("")

    def draw_hash(self):
        for j in range(0, self.SIZE[1] * 2 + 1):
            for i in range(0, self.SIZE[0] * 2 + 1):
                print(ADOM[self.hash_lab[j][i]], end='')
            print("")


class Model:

    def get_tex(self, file):
        tex = pyglet.image.load(file).texture
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        return pyglet.graphics.TextureGroup(tex)

    def add_cube(self, pos):

        tex_coords = ('t2f', (0, 0, 1, 0, 1, 1, 0, 1,))
        # texture coordinates

        x, y, z = 0, 0, -1
        X, Y, Z = x+1, y+1, z+1

        self.batch.add(4, GL_QUADS, self.side,
                       ('v3f', (X + pos[0], y + pos[1], z + pos[2], x + pos[0], y + pos[1], z + pos[2],
                                x + pos[0], Y + pos[1], z + pos[2], X + pos[0], Y + pos[1], z + pos[2],)),
                       tex_coords)  # back
        self.batch.add(4, GL_QUADS, self.side,
                       ('v3f', (x + pos[0], y + pos[1], Z + pos[2], X + pos[0], y + pos[1], Z + pos[2],
                                X + pos[0], Y + pos[1], Z + pos[2], x + pos[0], Y + pos[1], Z + pos[2],)),
                       tex_coords)  # front
        self.batch.add(4, GL_QUADS, self.side,
                       ('v3f', (x + pos[0], y + pos[1], z + pos[2], x + pos[0], y + pos[1], Z + pos[2],
                                x + pos[0], Y + pos[1], Z + pos[2], x + pos[0], Y + pos[1], z + pos[2],)),
                       tex_coords)  # left
        self.batch.add(4, GL_QUADS, self.side,
                       ('v3f', (X + pos[0], y + pos[1], Z + pos[2], X + pos[0], y + pos[1], z + pos[2],
                                X + pos[0], Y + pos[1], z + pos[2], X + pos[0], Y + pos[1], Z + pos[2],)),
                       tex_coords)  # right
        self.batch.add(4, GL_QUADS, self.bottom,
                       ('v3f', (x + pos[0], y + pos[1], z + pos[2], X + pos[0], y + pos[1], z + pos[2],
                                X + pos[0], y + pos[1], Z + pos[2], x + pos[0], y + pos[1], Z + pos[2],)),
                       tex_coords)  # bottom
        self.batch.add(4, GL_QUADS, self.top,
                       ('v3f', (x + pos[0], Y + pos[1], Z + pos[2], X + pos[0], Y + pos[1], Z + pos[2],
                                X + pos[0], Y + pos[1], z + pos[2], x + pos[0], Y + pos[1], z + pos[2],)),
                       tex_coords)  # top

    def add_floor(self, pos):
        tex_coords = ('t2f', (0, 0, 1, 0, 1, 1, 0, 1,))
        # texture coordinates
        x, y, z = 0, 0, -1
        X, Y, Z = x + 1, y + 1, z + 1
        self.batch.add(4, GL_QUADS, self.bottom,
                       ('v3f', (x + pos[0], y + pos[1], z + pos[2], X + pos[0], y + pos[1], z + pos[2],
                                X + pos[0], y + pos[1], Z + pos[2], x + pos[0], y + pos[1], Z + pos[2],)),
                       tex_coords)  # bottom

    def add_gate(self, pos):
        tex_coords = ('t2f', (0, 0, 1, 0, 1, 1, 0, 1,))
        # texture coordinates
        x, y, z = 0, 0, -1
        X, Y, Z = x + 1, y + 1, z + 1
        self.batch.add(4, GL_QUADS, self.gate,
                       ('v3f', (X + pos[0], y + pos[1], z + pos[2], x + pos[0], y + pos[1], z + pos[2],
                                x + pos[0], Y + pos[1], z + pos[2], X + pos[0], Y + pos[1], z + pos[2],)),
                       tex_coords)  # back

    def add_portal(self, pos):
        tex_coords = ('t2f', (0, 0, 1, 0, 1, 1, 0, 1,))
        # texture coordinates
        x, y, z = 0, 0, -1
        X, Y, Z = x + 1, y + 1, z + 1
        self.batch.add(4, GL_QUADS, self.portal,
                       ('v3f', (x + pos[0], y + pos[1], Z + pos[2], X + pos[0], y + pos[1], Z + pos[2],
                                X + pos[0], Y + pos[1], Z + pos[2], x + pos[0], Y + pos[1], Z + pos[2],)),
                       tex_coords)  # front

    def add_ceiling(self, pos):
        tex_coords = ('t2f', (0, 0, 1, 0, 1, 1, 0, 1,))
        # texture coordinates
        x, y, z = 0, 0, -1
        X, Y, Z = x + 1, y + 1, z + 1
        self.batch.add(4, GL_QUADS, self.ceiling,
                       ('v3f', (x + pos[0], Y + pos[1], Z + pos[2], X + pos[0], Y + pos[1], Z + pos[2],
                                X + pos[0], Y + pos[1], z + pos[2], x + pos[0], Y + pos[1], z + pos[2],)),
                       tex_coords)  # top

    def __init__(self):
        self.batch = pyglet.graphics.Batch()
        # create batch

        self.top = self.get_tex('bricks_d.jpg')
        self.side = self.get_tex('bricks.jpg')
        self.bottom = self.get_tex('grass.jpg')
        self.gate = self.get_tex('gate_closed.jpg')
        self.portal = self.get_tex('portal.jpg')
        self.ceiling = self.get_tex('bricks_d.jpg')

        for i in range(labyrinth.SIZE[1] * 2 + 1):
            for j in range(labyrinth.SIZE[0] * 2 + 1):
                if labyrinth.hash_lab[j][i] == 1:
                    self.add_cube((i, 0, j))
                elif labyrinth.hash_lab[j][i] == 0:
                    self.add_floor((i, 0, j))
                    self.add_ceiling((i, 0, j))
        self.add_gate((1, 0, 0))
        self.add_portal((LAB_SIZE[1] * 2 - 1, 0, LAB_SIZE[0] * 2))

        # add to batch to draw all at once

    def draw(self):
        global pos
        self.batch.draw()
        pyglet.text.Label('Hello Truman!', color=(255, 255, 255, 255), font_name='Arial', font_size=8,
                          x=50, y=-10, anchor_x='center', anchor_y='center').draw()
        pyglet.image.load('thetrumanshow.jpg').blit(-400, -50, -600)

"""
        pyglet.text.Label('X:' + str(int(window.player.pos[0])) +
                          ' Y:' + str(int(window.player.pos[1])) +
                          ' Z:' + str(int(window.player.pos[2])),
                          font_name='monospace', font_size=12, x=10, y=10, anchor_x='center', anchor_y='center').draw()
        try:
            pyglet.text.Label(str(labyrinth.hash_lab[int(window.player.pos[2]+1)][int(window.player.pos[0])]),
                          font_name='monospace', font_size=12, x=10, y=30, anchor_x='center', anchor_y='center').draw()
        except:
            pass
"""


class Player:
    def __init__(self, pos, rot):
        self.pos = list(pos)
        self.rot = list(rot)
        self.lock = True

    def mouse_motion(self, dx, dy):
        dx /= 6
        dy /= 6
        self.rot[0] += dy
        self.rot[1] -= dx

    def update(self, dt, keys):
        pN, pS, pE, pW = False, False, False, False

        try:
            if self.lock:  # checks if the player is locked by the labyrinth walls
                pN = bool(labyrinth.hash_lab[int(self.pos[2] + 0.7)][int(self.pos[0])])
                pS = bool(labyrinth.hash_lab[int(self.pos[2] + 1.3)][int(self.pos[0])])
                pE = bool(labyrinth.hash_lab[int(self.pos[2] + 1.1)][int(self.pos[0] + 0.2)])
                pW = bool(labyrinth.hash_lab[int(self.pos[2] + 1.1)][int(self.pos[0] - 0.2)])
        except:
            pN, pS, pE, pW = False, False, False, False

        s = dt * 5
        rotY = -self.rot[1] / 180 * math.pi
        dx, dz = s * math.sin(rotY), s * math.cos(rotY)
        if keys[key.W]:
            if (dx > 0 and not pE) or (dx < 0 and not pW):
                self.pos[0] += dx
            if (dz > 0 and not pN) or (dz < 0 and not pS):
                self.pos[2] -= dz
        if keys[key.S]:
            if (dx < 0 and not pE) or (dx > 0 and not pW):
                self.pos[0] -= dx
            if (dz < 0 and not pN) or (dz > 0 and not pS):
                self.pos[2] += dz
        if keys[key.A]:
            if (dz < 0 and not pE) or (dz > 0 and not pW):
                self.pos[0] -= dz
            if (dx > 0 and not pN) or (dx < 0 and not pS):
                self.pos[2] -= dx
        if keys[key.D]:
            if (dz > 0 and not pE) or (dz < 0 and not pW):
                self.pos[0] += dz
            if (dx < 0 and not pN) or (dx > 0 and not pS):
                self.pos[2] += dx
        if keys[key.C]:
            self.pos = [1.5, 0.5, -0.5]
            self.rot = [0, 180]
        if keys[key.Q]:
            self.pos[1] += s
        if keys[key.E]:
            self.pos[1] -= s
        if keys[key.L]:
            self.lock = bool(1-self.lock)
            pN, pS, pE, pW = False, False, False, False
"""
        try:
            print(self.pos, self.rot, dx, dz, "C:", str(labyrinth.hash_lab[int(self.pos[2]+1)][int(self.pos[0])]),
              "N:", pN, "S:", pS, "E:", pE, "W:", pW, "L:", self.lock)
        except:
            pass
"""


class Window(pyglet.window.Window):

    def push(self, pos, rot):
        glPushMatrix()
        glRotatef(-rot[0], 1, 0, 0)
        glRotatef(-rot[1], 0, 1, 0)
        glTranslatef(-pos[0], -pos[1], -pos[2], )

    def Projection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

    def Model(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def set2d(self):
        # set up the window context as 2D
        self.Projection()
        gluOrtho2D(0, self.width, 0, self.height)
        # min and max render distance
        self.Model()

    def set3d(self):
        # set up the window context as 3D
        self.Projection()
        gluPerspective(60, self.width/self.height, 0.05, 1000)
        # 70 - fov, field of view; w/h - aspect ratio; 0.05/1000 - min/max render distance
        self.Model()

    def setLock(self, state):
        self.lock = state
        self.set_exclusive_mouse(state)

    lock = True
    mouse_lock = property(lambda self: self.lock, setLock)

    def on_mouse_motion(self, x, y, dx, dy):
        if self.mouse_lock: self.player.mouse_motion(dx, dy)

    def on_key_press(self, KEY, MOD):
        if KEY == key.ESCAPE: self.close()
        elif KEY == key.SPACE: self.mouse_lock = not self.mouse_lock

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_minimum_size(200, 200)
        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)
        pyglet.clock.schedule(self.update)

        self.model = Model()
        self.player = Player(start_pos, start_rot)

    def update(self, dt):
        self.player.update(dt, self.keys)

    def on_draw(self):
        self.clear()
        self.set3d()
        self.push(self.player.pos, self.player.rot)
        self.model.draw()
        glPopMatrix()


# Let's start!
random.seed()
seed = random.randint(0, 1000)
LAB_SIZE = (20, 20)
if sys.getrecursionlimit() < LAB_SIZE[0] * LAB_SIZE[1]:
    sys.setrecursionlimit(LAB_SIZE[0] * LAB_SIZE[1])

labyrinth = Lab(LAB_SIZE, seed)

start_pos = [1.5, 0.5, -0.5]
start_rot = [0, 180]

if __name__ == '__main__':
    window = Window(caption='Labyrinth 3D v2.0 - #' + str(seed), resizable=True, fullscreen=True)
    window.set_mouse_visible(False)
    window.set_exclusive_mouse(True)
    glClearColor(0.1, 0.2, 0.3, 1)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    # glEnable(GL_CULL_FACE)

pyglet.app.run()

"""
    # shuffles directions each time for more randomness
    for dir in dirs:
        new_x = x1 + GO_DIR[dir][0]
        new_y = y1 + GO_DIR[dir][1]
        if (new_y in range(SIZE[1])) and\
        (new_x in range(SIZE[0])) and\
        (lab[new_y][new_x] == 0):
            # checks if the new cell is not visited
            lab[y][x] |= dir
            lab[new_y][new_x] |= REVERSE[dir]
            # if so, apply info on passages to both cells
            solve(new_x, new_y)
            # repeat recursively

- preparing the solve() function - some notes below for further decision-making:
- recursion vs while True loop (until (x2, y2) reached on path list)
- visited - number (min number of visits each time)
- path - list of cells' coordinates (append good ones, pop bad ones)
- backtracking status - processing new branch or withdrawing from dead-end - needed True/False to determine\
if the crossroad cell should be marked as visited more than once (not if back from a dead-end and checking\
a new alternative - maybe manually putting the minus)

- backward tracking on the branch:
    - if min num of visits = 0 - it's a new path to check - append each visited cell to the path list, decrease by one the number of visits on the crossroad cell, invert backtracking status
    - if min num of visits = 1 - it's a dead-end - pop the whole branch from path list (one by one) until a crossroads with unvisited branches reached; then proceed the new path
    - apply path to hash_lab to display during print (,.:;)

"""