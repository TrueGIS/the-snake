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
    """Базовый класс для объектов игры."""

    BOARD_BACKGROUND_COLOR: tuple = BOARD_BACKGROUND_COLOR

    def __init__(self, body_color: tuple = DEFAULT_GRAY_COLOR):
        self.position: tuple = START_POSITION
        self.body_color = body_color

    def draw_cell(self, position, color=DEFAULT_GRAY_COLOR, border_color=None):
        """Отрисовка ячейки"""
        if color:
            self.color = color
        else:
            self.color = self.body_color
        cell = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.color, cell)
        if border_color:
            pg.draw.rect(screen, border_color, cell, 1)

    def draw(self):
        """Заглушка для метода отрисовки."""


class Snake(GameObject):
    """
    Представляет змейку.

    Доступны перемещение, проверка на столкновение, изменение направления
    движения, отрисовка змейки и сброс игры.

    В игрвом цикле используй draw() для отрисовки, move() для перемещения,
    update_direction() для изменения направления, snake.collision()
    для проверки столкновения с хвостом.
    """

    def __init__(self):
        super().__init__()
        self.body_color: tuple = SNAKE_COLOR
        self.positions: list = [self.position]
        self.length: int = 1
        self.direction: tuple = RIGHT
        self.next_direction: tuple = None
        self.last: tuple = None
        self.speed: int = 10

    def get_head_position(self) -> tuple:
        """Возвращает текущие координаты головы змейки."""
        return self.positions[0]

    def reset(self):
        """
        Сбрасывает змейку в случае столкновения с хвостом.

        Перемещает в исходное положение, сбрасывает хвост, задаёт случайное
        направление движения. ВОЗМОЖНО ЗДЕСЬ НУЖНО СБРОСИТЬ ЕЩЁ И ЯБЛОКИ? НО ЭТО ЖЕ ЗМЕЙКА
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
        snake_head_x = head_position[0] + self.direction[0] * GRID_SIZE
        if snake_head_x == SCREEN_WIDTH or snake_head_x < 0:
            snake_head_x = snake_head_x % SCREEN_WIDTH
        snake_head_y = head_position[1] + self.direction[1] * GRID_SIZE
        if snake_head_y == SCREEN_HEIGHT or snake_head_y < 0:
            snake_head_y = snake_head_y % SCREEN_HEIGHT
        self.positions.insert(0, (snake_head_x, snake_head_y))
        self.last = self.positions[-1]
        if len(self.positions) > self.length:
            self.positions.pop()

    def collision(self):
        """
        Описывает поведение при столкновении головы с хвостом.

        В случае столкновения вызвает метод reset()
        для сброса параметров змейки.
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

        Отрисовывает каждый сегмент из списка positions,
        стирает последний сегмент после смещения головы.
        """
        self.draw_cell(self.positions[0], SNAKE_COLOR, BORDER_COLOR)
        self.draw_cell(self.last, BOARD_BACKGROUND_COLOR)

class Apple(GameObject):
    """Представляет яблоки, перемещает и рисует их."""

    def __init__(self):
        super().__init__()
        self.position = START_POSITION
        self.body_color = DEFAULT_GRAY_COLOR

    def randomize_position(self):
        """
        Вычисляет координаты случайным образом,
        возвращает кортеж из координат.
        """
        apple_x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
        apple_y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        return apple_x, apple_y

    def draw(self):
        """Отрисовывает яблоко."""
        self.draw_cell(self.position, self.body_color, BORDER_COLOR)


class RedApple(Apple):
    """Представляет красное, вкусное яблоко."""

    def __init__(self):
        super().__init__()
        self.position = self.randomize_position()
        self.body_color = RED_APPLE_COLOR

    def ate_apple(self, snake: Snake):
        """
        Съедание красного яблока змейкой.

        При съедании яблока змейка растёт, излечивается от отравления
        (фон становится чёрным), а яблоко перемещается в случайную
        точку на экране.
        """
        head_snake = snake.get_head_position()
        if head_snake == self.position:
            GameObject.BOARD_BACKGROUND_COLOR = BOARD_BACKGROUND_COLOR
            snake.length += 1
            self.position = self.randomize_position()


class BlueApple(Apple):
    """Представляет синее - ядовитое яблоко."""

    def __init__(self):
        super().__init__()
        self.position = self.randomize_position()
        self.body_color = BLUE_APPLE_COLOR

    def ate_apple(self, snake: Snake):
        """
        Съедание ядовитого яблока змейкой.

        При съедании яблока змейка уменьшается, отравляется
        (экран становится белым), пока не съешь нормальное яблоко,
        ядовитое яблоко перемещается в случайную точку на экране.
        Если змейка была длиной 1, то вызывается метод reset()
        и змейка перемещается в центр и меняет направление движения.
        """
        head_snake = snake.get_head_position()
        if head_snake == self.position and len(snake.positions) > 1:
            snake.positions.remove(snake.positions[-1])
            snake.length = len(snake.positions)
            self.position = self.randomize_position()
            GameObject.BOARD_BACKGROUND_COLOR = SICK_SNAKE_COLOR
        elif head_snake == self.position and len(snake.positions) == 1:
            snake.reset()
            GameObject.BOARD_BACKGROUND_COLOR = SICK_SNAKE_COLOR


class GoldenApple(Apple):
    """Представляет золотое яблоко-бустер."""

    def __init__(self):
        super().__init__()
        self.position = self.randomize_position()
        self.body_color = GOLDEN_APPLE_COLOR

    def ate_apple(self, snake: Snake):
        """
        Съедание золотого яблока змейкой.

        При съедании яблока змейка ускоряется на 20, а золотое
        яблоко перемещается в случайную точку на экране.
        """
        head_snake = snake.get_head_position()
        if head_snake == self.position:
            snake.speed += 20
            self.position = self.randomize_position()


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
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Основной игровой цикл."""
    pg.init()
    snake = Snake()
    red_apple = RedApple()
    blue_apple = BlueApple()
    golden_apple = GoldenApple()
    while True:
        clock.tick(snake.speed)
        handle_keys(snake)
        snake.update_direction()
        snake.move()
        red_apple.ate_apple(snake)
        blue_apple.ate_apple(snake)
        golden_apple.ate_apple(snake)
        if snake.collision():
            snake.reset()
        snake.draw()
        red_apple.draw()
        blue_apple.draw()
        golden_apple.draw()
        pg.display.update()

if __name__ == '__main__':
    main()
