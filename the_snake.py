from random import choice, randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет фона
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет красного яблока
RED_COLOR = (255, 0, 0)

# Цвет красного яблока
BLUE_COLOR = (0, 0, 255)

# Цвет красного яблока
GOLDEN_COLOR = (255, 215, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для объектов игры."""

    board_background_color: tuple = BOARD_BACKGROUND_COLOR

    def __init__(self):
        self.position: tuple = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color: tuple = None

    def draw(self):
        """Заглушка для метода отрисовки."""
        pass


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
        направление движения.
        """
        self.positions = [self.position]
        self.length = 1
        self.direction = choice([UP, DOWN, LEFT, RIGHT])

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
            self.positions.remove(self.last)

    def collision(self):
        """
        Описывает поведение при столкновении головы с хвостом.

        В случае столкновения вызвает метод reset()
        для сброса параметров змейки.
        """
        head_snake_position = self.get_head_position()
        for snake_segment_position in self.positions[1:]:
            if head_snake_position == snake_segment_position:
                self.reset()

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
        for position in self.positions:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen,
                             GameObject.board_background_color, last_rect)


class Apple(GameObject):
    """Представляет яблоки, перемещает и рисует их."""

    def __init__(self):
        super().__init__()
        self.position = None
        self.body_color = None

    def randomize_position(self) -> tuple:
        """
        Вычисляет координаты случайным образом,
        возвращает кортеж из координат.
        """
        apple_x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
        apple_y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        return apple_x, apple_y

    def draw(self):
        """Отрисовывает яблоко."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class RedApple(Apple):
    """Представляет красное, вкусное яблоко."""

    def __init__(self):
        super().__init__()
        self.position = self.randomize_position()
        self.body_color = RED_COLOR

    def ate_apple(self, snake: Snake):
        """
        Съедание красного яблока змейкой.

        При съедании яблока змейка растёт, излечивается от отравления
        (фон становится чёрным), а яблоко перемещается в случайную
        точку на экране.
        """
        head_snake = snake.get_head_position()
        if head_snake == self.position:
            GameObject.board_background_color = BOARD_BACKGROUND_COLOR
            snake.length += 1
            self.position = self.randomize_position()


class BlueApple(Apple):
    """Представляет синее - ядовитое яблоко."""

    def __init__(self):
        super().__init__()
        self.position = self.randomize_position()
        self.body_color = BLUE_COLOR

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
            GameObject.board_background_color = (255, 255, 255)
        elif head_snake == self.position and len(snake.positions) == 1:
            snake.reset()
            GameObject.board_background_color = (255, 255, 255)


class GoldenApple(Apple):
    """Представляет золотое яблоко-бустер."""

    def __init__(self):
        super().__init__()
        self.position = self.randomize_position()
        self.body_color = GOLDEN_COLOR

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
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Основной игровой цикл."""
    pygame.init()
    snake = Snake()
    red_apple = RedApple()
    blue_apple = BlueApple()
    golden_apple = GoldenApple()
    while True:
        clock.tick(snake.speed)
        handle_keys(snake)
        snake.update_direction()
        red_apple.ate_apple(snake)
        blue_apple.ate_apple(snake)
        golden_apple.ate_apple(snake)
        snake.move()
        snake.collision()
        screen.fill(GameObject.board_background_color)
        snake.draw()
        red_apple.draw()
        blue_apple.draw()
        golden_apple.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
