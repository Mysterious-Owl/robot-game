import random
import time
import PySimpleGUI as sg

body_choice = {"Simple": {"hp": 2, "mvt": 1, "slot": 1}, "Hard": {"hp": 5, "mvt": 1, "slot": 1},
               "Light": {"hp": 3, "mvt": 2, "slot": 1}, "Battle": {"hp": 2, "mvt": 1, "slot": 2}}
weapon_choice = {"Basic": {"hp": 1}, "Laser": {"hp": 1}, "Sword": {"hp": 2}, "Explosion": {"hp": 1},
                 "Dual Laser": {"hp": 1}}
height = 6
width = 6
starting_height = 1
robot_obstacle = 8
obstacle_hp = 1
no_of_players = 2
timeout = 750
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'
directions = [UP, DOWN, LEFT, RIGHT]
teams = {1: {"color": "Blue", "number": 1, "side": UP}, 2: {"color": "Red", "number": 1, "side": DOWN}}


class Object:

    def __init__(self):
        pass


class Body(Object):

    def __init__(self, name=None):
        super().__init__()
        name = random.choice(list(body_choice.keys())) if name is None else name
        self.name = name
        self.bhp = body_choice[name]['hp']
        self.mvt = body_choice[name]['mvt']
        self.slot = body_choice[name]['slot']

    def __repr__(self):
        return f"Body{'-' * 20}{self.name}\n{'Body Health Points:':<23}{self.bhp}\n{'Body Movement:':<23}{self.mvt}\n" \
               f"{'Weapon Slot:':<23}{self.slot}"

    def change_bhp(self, point):
        self.bhp += point

    def current_bhp(self):
        return self.bhp

    def get_mvt(self):
        return self.mvt

    def get_bhp(self):
        return self.bhp

    def get_slot(self):
        return self.slot


class Weapon(Object):

    def __init__(self, name=None):
        super().__init__()
        name = random.choice(list(weapon_choice.keys())) if name is None else name
        self.name = name
        self.whp = weapon_choice[name]['hp']

    def __repr__(self):
        return f"Weapon{'-' * 18}{self.name}\n{'Weapon Health Points:':<23}{self.whp}"

    def get_whp(self):
        return self.whp


class Robot:

    def __init__(self, body=None, weapon=None, team=None, direction=UP):
        self.body = Body(body)
        self.weapon = Weapon(weapon)
        self.team = team
        self.hp = 5
        self.direction = direction
        self.cor_x = 0
        self.cor_y = 0

    def __repr__(self):
        return f"{'Team:':<23}{self.team}\n{'Current position:':<23}{self.cor_x} {self.cor_y}\n" \
               f"{'Currently facing:':<23}{self.direction}\n{'Robot Health Points:':<23}{self.hp}" \
               f"\n{self.body}\n{self.weapon}\n"

    def attack(self, hp):
        self.hp -= hp if self.body.current_bhp() == 0 else 0
        self.body.change_bhp(-min(self.body.current_bhp(), hp))
        return True if self.get_hp() > 0 else False

    def get_hp(self):
        return self.body.current_bhp() + self.hp

    def set_pos(self, x, y):
        self.cor_x, self.cor_y = x, y

    def get_pos(self):
        return self.cor_x, self.cor_y

    def change_body(self, body):
        if body.get_bhp() > self.body.current_bhp():
            self.body = body

    def heal_robot(self, hp):
        self.hp = min(self.hp + hp, 5)

    def change_direction(self, direction):
        self.direction = direction

    def get_direction(self):
        return self.direction

    def is_alive(self):
        return False if self.get_hp() == 0 else True

    def get_team(self):
        return self.team


class Obstacle(Robot):
    def __init__(self, starting_bhp, x, y, drop=False):
        Robot.__init__(self)
        self.drop = random.choice(['weapon', 'body']) if drop else None
        self.body.bhp = starting_bhp
        self.set_pos(x, y)
        self.hp = 0

    def __repr__(self):
        return super().__repr__() + f"{'Drop type:':<23}{self.drop}"


class Robot_team:
    def __init__(self, number, team):
        self.team = [Robot('Simple', 'Basic', team=team) for _ in range(number)]

    def __repr__(self):
        a = ''
        for member in self.team:
            a += member.__repr__()
        return a

    def fetch_team(self):
        return self.team

    def fetch_alive_team(self):
        return [i for i in self.team if i.is_alive()]


class Board:
    def __init__(self):
        self.status = [[None for _ in range(width)] for _ in range(height)]

    def print_board(self):
        for row in self.status:
            for cell in row:
                print(f'{type(cell).__name__:<10}', end=' ')
            print()

    def place_obstacles(self):
        for _ in range(robot_obstacle):
            while True:
                x = random.randint(starting_height, height - starting_height - 1)
                y = random.randint(0, width - 1)
                if self.status[x][y] is None:
                    break
            self.status[x][y] = Obstacle(starting_bhp=obstacle_hp, x=x, y=y, drop=True)
            # print(self.status[x][y])
            # print('--'*20)

    def place_robot(self, player, side):
        while True:
            x = random.randint(0 if side == UP else height - starting_height,
                               starting_height - 1 if side == UP else height - 1)
            y = random.randint(0, width - 1)
            if self.status[x][y] is None:
                break
        self.status[x][y] = player
        player.set_pos(x, y)

    def in_bounds(self, x, y):
        return False if x >= len(self.status) or y >= len(self.status[0]) or x < 0 or y < 0 else True

    def cell_status(self, x, y):
        if not self.in_bounds(x, y):
            return False
        return self.status[x][y]

    def move_object(self, x_src, y_src, x_des, y_des):
        if x_src > len(self.status) or y_src > len(self.status[0]) or x_src < 0 or y_src < 0 or \
                x_des > len(self.status) or y_des > len(self.status[0]) or x_des < 0 or y_des < 0 or \
                self.cell_status(x_src, y_src) is None:
            return False
        if x_src == x_des and y_des == y_src:
            return True
        if self.cell_status(x_des, y_des) is None:
            self.status[x_des][y_des] = self.status[x_src][y_src]
        elif isinstance(self.cell_status(x_des, y_des), Obstacle):
            self.status[x_des][y_des] = self.status[x_src][y_src].absorb_body(self.status[x_des][y_des])
        self.status[x_src][y_src] = None
        self.status[x_des][y_des].set_pos(x_des, y_des)
        return True

    def empty_neighbour(self, x, y):
        positions_available = []
        if self.cell_status(x + 1, y) is None:
            positions_available.append((x + 1, y))
        if self.cell_status(x - 1, y) is None:
            positions_available.append((x - 1, y))
        if self.cell_status(x, y + 1) is None:
            positions_available.append((x, y + 1))
        if self.cell_status(x, y - 1) is None:
            positions_available.append((x, y - 1))
        # print(positions_available)
        return positions_available

    def empty_cell(self, x, y):
        self.status[x][y] = None


def move_robot(player, board):
    move = random.choice(directions)
    pos = player.get_pos()
    pos_options = board.empty_neighbour(*pos)
    if len(pos_options) > 1:
        pos_options = random.choice(pos_options)
    elif len(pos_options) == 1:
        pos_options = pos_options[0]
    else:
        pos_options = pos
    # print(pos_options)
    board.move_object(*pos, *pos_options)
    player.change_direction(move)


def attack(player, board):
    if not player.is_alive():
        return
    whp = player.weapon.get_whp()
    x, y = player.get_pos()
    attack_pos = []
    if player.get_direction() == UP:
        dx = -1
        dy = 0
    elif player.get_direction() == DOWN:
        dx = 1
        dy = 0
    elif player.get_direction() == LEFT:
        dx = 0
        dy = -1
    else:
        dx = 0
        dy = 1
    for ii in range(1, 4):
        if board.in_bounds(x + ii * dx, y + ii * dy):
            attack_pos.append((x + ii * dx, y + ii * dy))
        if board.cell_status(x + ii * dx, y + ii * dy):
            if not board.cell_status(x + ii * dx, y + ii * dy).attack(whp):
                board.empty_cell(x + ii * dx, y + ii * dy)
    return attack_pos


def initialize():
    new.place_obstacles()
    for each_team in teams.values():
        players.append(Robot_team(each_team['number'], each_team['color']))
        for i in players[-1].fetch_team():
            new.place_robot(i, each_team['side'])


# print(new.print_board())
# player1 = players[0]
# player2 = players[1]
# player1 = player1.__repr__().split('\n')
# player2 = player2.__repr__().split('\n')
# for i, j in zip(player1, player2):
#     print(f'{i:<35}{j}')
# print()
# while True:
#     for teama in players:
#         for membera in teama.fetch_alive_team():
#             move_robot(membera, new)
#             attack(membera, new)
#     print(new.print_board())
#     player1 = players[0]
#     player2 = players[1]
#     player1 = player1.__repr__().split('\n')
#     player2 = player2.__repr__().split('\n')
#     for i, j in zip(player1, player2):
#         print(f'{i:<35}{j}')
#     if 0 in [len(teama.fetch_alive_team()) for teama in players]:
#         break
#     # time.sleep(0.1)
def gui():
    global timeout
    layout1 = [[sg.Text(players[0].fetch_team()[0], key='1')]]
    layout3 = [[sg.Text(players[1].fetch_team()[0], key='2')]]
    layout2 = [[sg.Text('')]]

    for row in range(height):
        lay = []
        for col in range(width):
            cell = new.cell_status(row, col)
            if cell is None:
                name = ''
                color = 'yellow'
            elif isinstance(cell, Obstacle):
                name = 'O'
                color = 'black'
            else:
                name = 'R'
                color = cell.get_team()
            lay.append(sg.Button(name, size=(10, 5), pad=(0, 0), border_width=0, button_color=color, key=(row, col)))
        layout2.append(lay)

    layout2.append([sg.Slider((0, 1500), timeout, 10, 100, 'h', size=(58, 10), key='time', enable_events=True)])
    layout = [[sg.Column(layout1), sg.Column(layout2), sg.Column(layout3)]]
    window = sg.Window('Robot Simulation', layout)

    while True:
        event, values = window.read(timeout=timeout)
        if event == 'time':
            timeout = values['time']
        elif event in (sg.WIN_CLOSED, 'Exit'):
            break
        else:
            for teama in players:
                for membera in teama.fetch_alive_team():
                    move_robot(membera, new)
                    for row in range(height):
                        for col in range(width):
                            cell = new.cell_status(row, col)
                            if cell is None:
                                name = ''
                                color = 'yellow'
                            elif isinstance(cell, Obstacle):
                                name = 'O'
                                color = 'black'
                            else:
                                name = 'R'
                                color = cell.get_team()
                            window[(row, col)].update(name, button_color=color)
                    attack_pos = attack(membera, new)
                    window['1'].update(players[0].__repr__())
                    window['2'].update(players[1].__repr__())
                    for apos in attack_pos:
                        window[apos].update(button_color='white')
                    _e, _v = window.read(timeout=timeout)

            if 0 in [len(teama.fetch_alive_team()) for teama in players]:
                timeout = 100000000

    window.close()


players = []
new = Board()

initialize()
gui()
