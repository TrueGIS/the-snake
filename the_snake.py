from random import choice, randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
START_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвета фона и игровых объектов
BORDER_COLOR = (93, 216, 228)
BOARD_BACKGROUND_COLOR = (0, 0, 0)
SICK_SNAKE_COLOR = (255, 255, 255)
DEFAULT_GRAY_COLOR = (50, 50, 50)
RED_APPLE_COLOR = (255, 0, 0)
BLUE_APPLE_COLOR = (0, 0, 255)
GOLDEN_APPLE_COLOR = (255, 215, 0)
SNAKE_COLOR = (0, 255, 0)

# Настройки игрового поля, окна и времени:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption('Змейка')
clock = pg.time.Clock()


class GameObject:
    """
    Базовый класс, где хранятся общие атрибуты
    для игровых объектов Apple и Snake
    """

    BOARD_BACKGROUND_COLOR: tuple = BOARD_BACKGROUND_COLOR

    def __init__(self, position: tuple = START_POSITION,
                 body_color: tuple = DEFAULT_GRAY_COLOR):
        self.position = position
        self.body_color = body_color

    def draw_cell(self, position, cell_color=DEFAULT_GRAY_COLOR,
                  border_color=None):
        """
        Отрисовка ячейки.

        Метод используется для отрисовки элементов
        всех игровых объектов: яблок и змейки.
        """
        self.cell_color = cell_color
        cell = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.cell_color, cell)
        if border_color:
            pg.draw.rect(screen, border_color, cell, 1)

    def draw(self):
        """Заглушка для метода отрисовки."""
        raise NotImplementedError("Дочерние классы должны"
                                  + " реализовать метод draw()")


class Snake(GameObject):
    """
    Представляет змейку.

    Доступны перемещение, проверка на столкновение, изменение направления
    движения, отрисовка змейки и сброс игры.

    В игрвом цикле используй draw() для отрисовки, move() для перемещения,
    update_direction() для изменения направления, snake.collision()
    для проверки столкновения с хвостом.
    """

    def __init__(self, body_color=SNAKE_COLOR):
        super().__init__(body_color=body_color)
        self.positions: list = [self.position]
        self.length: int = 1
        self.direction: tuple = RIGHT
        self.next_direction: tuple = None
        self.last: tuple = None

    def get_head_position(self) -> tuple:
        """Возвращает текущие координаты головы змейки."""
        return self.positions[0]

    def reset(self):
        """
        Сбрасывает змейку в случае столкновения с хвостом.

        Перемещает в исходное положение, сбрасывает хвост, задаёт случайное
        направление движения, закрашивает поле базовым цветом фона.
        """
        self.positions = [self.position]
        self.length = 1
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        screen.fill(GameObject.BOARD_BACKGROUND_COLOR)

    def move(self):
        """
        Перемещает змейку в границах экрана.

        В случае достижения границ экрана змейка возвращается
        с противоположной стороны.
        """
        head_position = self.get_head_position()
        snake_head_x = ((head_position[0] + self.direction[0]
                         * GRID_SIZE) % SCREEN_WIDTH)
        snake_head_y = ((head_position[1] + self.direction[1]
                         * GRID_SIZE) % SCREEN_HEIGHT)
        self.positions.insert(0, (snake_head_x, snake_head_y))
        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def collision(self) -> bool:
        """
        Проверка на столкновение головы с хвостом.

        В случае столкновения возвращает True.
        """
        head_snake_position = self.get_head_position()
        if head_snake_position in self.positions[1:]:
            return True
        else:
            return False

    def update_direction(self):
        """
        Меняет направление движения змейки.

        После нажатия на клавишу через переменную
        next_direction передаётся соответсвующее направление.
        """
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def draw(self):
        """
        Отрисовывает змейку.

        Отрисовывает голову,
        стирает последний сегмент тела после смещения головы.
        """
        self.draw_cell(self.positions[0], SNAKE_COLOR, BORDER_COLOR)
        self.draw_cell(self.last, GameObject.BOARD_BACKGROUND_COLOR)


class Apple(GameObject):
    """Представляет яблоки, перемещает и рисует их."""

    def __init__(self, body_color=DEFAULT_GRAY_COLOR,
                 closed_positions: list[tuple[int, int]] | None = None
                 ):
        super().__init__(position=START_POSITION, body_color=body_color)
        if closed_positions is None:
            self.closed_positions = [START_POSITION]
        else:
            self.closed_positions = closed_positions
        self.randomize_position(self.closed_positions)

    def randomize_position(self, closed_positions: list[tuple[int, int]]):
        """
        Вычисляет координаты случайным образом,
        передаёт их в атрибут position для
        перемещения яблока.
        """
        while self.position in closed_positions:
            apple_x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
            apple_y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            self.position = (apple_x, apple_y)

    def draw(self):
        """Отрисовывает яблоко."""
        self.draw_cell(self.position, self.body_color, BORDER_COLOR)


def handle_keys(game_object):
    """
    Обработчик нажатия клавиш для выхода из игры и управления змейкой.

    Перехватывает нажатия клавиш вверх, вниз, влево, вправо
    и соответсвующим образом меняет переменную direction, а так же
    не позволяет идти змейке по самой себе. При закрытии окна
    корректно выходит из игры.
    """
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """
    Основной игровой цикл.


    Съедание яблок:
    При съедании золотого яблока змейка ускоряется на 20, а золотое
    яблоко перемещается в случайную точку на экране.

    При съедании ядовитого яблока змейка уменьшается, отравляется
    (экран становится белым, пока не съешь нормальное яблоко),
    ядовитое яблоко перемещается в случайную точку на экране.
    Если змейка была длиной 1, то вызывается метод reset()
    и змейка перемещается в центр и меняет направление движения.

    При съедании красного яблока змейка растёт, излечивается от
    отравления (фон становится чёрным), а яблоко перемещается
    в случайную точку на экране.
    """
    pg.init()
    speed_game = 10
    snake = Snake()
    red_apple = Apple(RED_APPLE_COLOR)
    blue_apple = Apple(BLUE_APPLE_COLOR)
    golden_apple = Apple(GOLDEN_APPLE_COLOR)
    while True:
        clock.tick(speed_game)
        handle_keys(snake)
        snake.update_direction()
        snake.move()
        closed_pos = (snake.positions + [red_apple.position]
                      + [blue_apple.position] + [golden_apple.position])
        if snake.get_head_position() == red_apple.position:
            if GameObject.BOARD_BACKGROUND_COLOR == SICK_SNAKE_COLOR:
                GameObject.BOARD_BACKGROUND_COLOR = BOARD_BACKGROUND_COLOR
                screen.fill(GameObject.BOARD_BACKGROUND_COLOR)
            snake.length += 1
            red_apple.randomize_position(closed_pos)
        elif snake.get_head_position() == blue_apple.position:
            if len(snake.positions) == 1:
                snake.reset()
                blue_apple.randomize_position(closed_pos)
            else:
                snake.positions.remove(snake.positions[-1])
                snake.length = len(snake.positions)
                blue_apple.randomize_position(closed_pos)
            GameObject.BOARD_BACKGROUND_COLOR = SICK_SNAKE_COLOR
            screen.fill(GameObject.BOARD_BACKGROUND_COLOR)
        elif snake.get_head_position() == golden_apple.position:
            speed_game += 20
            golden_apple.randomize_position(closed_pos)
        elif snake.collision():
            snake.reset()
        snake.draw()
        red_apple.draw()
        blue_apple.draw()
        golden_apple.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
