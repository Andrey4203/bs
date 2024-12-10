import random


class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за пределы поля!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку!"

class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Ship:
    def __init__(self, bow, length, orientation):
        self.bow = bow
        self.length = length
        self.orientation = orientation
        self.lives = length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            cur_x = self.bow.x + (i if self.orientation == 1 else 0)
            cur_y = self.bow.y + (i if self.orientation == 0 else 0)
            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots

    def hit(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid
        self.field = [["O"] * size for _ in range(size)]
        self.ships = []
        self.busy = []
        self.count = 0

    def add_ship(self, ship):
        for dot in ship.dots:
            if self.out(dot) or dot in self.busy:
                raise BoardWrongShipException()
        for dot in ship.dots:
            self.field[dot.x][dot.y] = "■"
            self.busy.append(dot)
        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship):
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),          (0, 1),
                      (1, -1), (1, 0), (1, 1)]
        for dot in ship.dots:
            for dx, dy in directions:
                cur_dot = Dot(dot.x + dx, dot.y + dy)
                if not self.out(cur_dot) and cur_dot not in self.busy:
                    self.busy.append(cur_dot)

    def out(self, dot):
        return not (0 <= dot.x < self.size and 0 <= dot.y < self.size)

    def shot(self, dot):
        if self.out(dot):
            raise BoardOutException()
        if dot in self.busy:
            raise BoardUsedException()
        self.busy.append(dot)

        for ship in self.ships:
            if ship.hit(dot):
                ship.lives -= 1
                self.field[dot.x][dot.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship)
                    return "Корабль уничтожен!"
                return "Корабль ранен!"
        self.field[dot.x][dot.y] = "T"
        return "Мимо!"

    def display(self):
        header = "  | " + " | ".join(str(i + 1) for i in range(self.size)) + " |"
        print(header)
        for i, row in enumerate(self.field):
            row_display = " | ".join(row)
            print(f"{i + 1} | {row_display} |")


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                result = self.enemy.shot(target)
                print(result)
                return result == "Корабль ранен!"
            except BoardException as e:
                print(e)

# Класс пользователя
class User(Player):
    def ask(self):
        while True:
            coords = input("Введите координаты выстрела (формат x y): ").split()
            if len(coords) != 2:
                print("Введите две координаты!")
                continue
            x, y = coords
            if not (x.isdigit() and y.isdigit()):
                print("Координаты должны быть числами!")
                continue
            return Dot(int(x) - 1, int(y) - 1)


class AI(Player):
    def ask(self):
        dot = Dot(random.randint(0, 5), random.randint(0, 5))
        print(f"Ход компьютера: {dot.x + 1} {dot.y + 1}")
        return dotё


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True
        self.user = User(pl, co)
        self.ai = AI(co, pl)

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def try_board(self):
        board = Board(size=self.size)
        lengths = [3, 2, 2, 1, 1, 1, 1]
        for length in lengths:
            attempts = 0
            while True:
                attempts += 1
                if attempts > 1000:
                    return None
                ship = Ship(
                    Dot(random.randint(0, self.size - 1), random.randint(0, self.size - 1)),
                    length,
                    random.randint(0, 1)
                )
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        return board

    def greet(self):
        print("Добро пожаловать в игру 'Морской бой'!")

    def loop(self):
        while True:
            print("Ваша доска:")
            self.user.board.display()
            print("Доска противника:")
            self.ai.board.display()
            if self.user.move():
                print("Вы победили!")
                break
            if self.ai.move():
                print("Компьютер победил!")
                break

    def start(self):
        self.greet()
        self.loop()


game = Game()
game.start()