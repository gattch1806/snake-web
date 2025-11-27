# /// script
# dependencies = ["pygame"]
# ///

import pygame
import random
import asyncio

WIDTH, HEIGHT = 600, 600
CELL = 30
GRID = WIDTH // CELL
FPS = 60

BLACK = (20, 20, 30)
GREEN = (80, 200, 100)
DARK_GREEN = (60, 160, 80)
RED = (220, 80, 80)
WHITE = (240, 240, 240)
GRAY = (60, 60, 80)


class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        center = GRID // 2
        self.body = [(center, center), (center - 1, center), (center - 2, center)]
        self.direction = (1, 0)
        self.grow = False

    def set_direction(self, new_dir):
        if new_dir[0] != -self.direction[0] or new_dir[1] != -self.direction[1]:
            self.direction = new_dir

    def move(self):
        head_x, head_y = self.body[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        self.grow = False

    def check_collision(self):
        head = self.body[0]
        if head[0] < 0 or head[0] >= GRID or head[1] < 0 or head[1] >= GRID:
            return True
        if head in self.body[1:]:
            return True
        return False

    def draw(self, screen):
        for i, segment in enumerate(self.body):
            x = segment[0] * CELL
            y = segment[1] * CELL
            color = GREEN if i == 0 else DARK_GREEN
            pygame.draw.rect(screen, color, (x + 2, y + 2, CELL - 4, CELL - 4), border_radius=8)


class Apple:
    def __init__(self):
        self.position = (5, 5)

    def spawn(self, snake_body):
        while True:
            pos = (random.randint(0, GRID - 1), random.randint(0, GRID - 1))
            if pos not in snake_body:
                self.position = pos
                break

    def draw(self, screen):
        x = self.position[0] * CELL
        y = self.position[1] * CELL
        pygame.draw.rect(screen, RED, (x + 2, y + 2, CELL - 4, CELL - 4), border_radius=8)


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)
        self.snake = Snake()
        self.apple = Apple()
        self.apple.spawn(self.snake.body)
        self.score = 0
        self.best_score = 0
        self.state = "menu"
        self.move_timer = 0
        self.move_delay = 0.12

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if self.state == "menu":
                if event.key == pygame.K_SPACE:
                    self.start_game()
            elif self.state == "playing":
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.snake.set_direction((0, -1))
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.snake.set_direction((0, 1))
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.snake.set_direction((-1, 0))
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.snake.set_direction((1, 0))
            elif self.state == "gameover":
                if event.key == pygame.K_SPACE:
                    self.start_game()
                elif event.key == pygame.K_ESCAPE:
                    self.state = "menu"

    def start_game(self):
        self.snake.reset()
        self.apple.spawn(self.snake.body)
        self.score = 0
        self.move_timer = 0
        self.move_delay = 0.12
        self.state = "playing"

    def update(self, dt):
        if self.state != "playing":
            return
        self.move_timer += dt
        if self.move_timer >= self.move_delay:
            self.move_timer = 0
            self.snake.move()
            if self.snake.check_collision():
                self.best_score = max(self.best_score, self.score)
                self.state = "gameover"
                return
            if self.snake.body[0] == self.apple.position:
                self.snake.grow = True
                self.score += 10
                self.apple.spawn(self.snake.body)
                self.move_delay = max(0.05, self.move_delay * 0.95)

    def draw_grid(self):
        for x in range(0, WIDTH, CELL):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL):
            pygame.draw.line(self.screen, GRAY, (0, y), (WIDTH, y))

    def draw_text_center(self, text, font, y, color=WHITE):
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(WIDTH // 2, y))
        self.screen.blit(surface, rect)

    def draw(self):
        self.screen.fill(BLACK)
        self.draw_grid()
        if self.state == "menu":
            self.draw_text_center("SNAKE", self.font, HEIGHT // 2 - 60)
            self.draw_text_center("WASD or Arrow Keys", self.small_font, HEIGHT // 2)
            self.draw_text_center("Press SPACE to start", self.small_font, HEIGHT // 2 + 40)
        elif self.state == "playing":
            self.apple.draw(self.screen)
            self.snake.draw(self.screen)
            score_text = self.small_font.render(f"Score: {self.score}", True, WHITE)
            self.screen.blit(score_text, (10, 10))
        elif self.state == "gameover":
            self.apple.draw(self.screen)
            self.snake.draw(self.screen)
            self.draw_text_center("GAME OVER", self.font, HEIGHT // 2 - 60)
            self.draw_text_center(f"Score: {self.score}  Best: {self.best_score}", self.small_font, HEIGHT // 2)
            self.draw_text_center("SPACE - restart, ESC - menu", self.small_font, HEIGHT // 2 + 40)


async def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()
    game = Game(screen)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_input(event)

        game.update(dt)
        game.draw()
        pygame.display.flip()

        await asyncio.sleep(0)

    pygame.quit()


asyncio.run(main())