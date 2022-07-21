import enum
from typing import List
import pygame
import random
pygame.init()

WIDTH, HEIGHT = 700, 500
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong AI")

FPS = 60

WHITE = (255,255,255)
BLACK = (0,0,0)
SCORE_FONT = pygame.font.SysFont("Roboto", 50)

PADDLE_HEIGHT, PADDLE_WIDTH = 20, 100
PADDLE_VELOCITY = 6

BALL_RADIUS = 7

class Ball:
    COLOR = WHITE
    START_VELOCITY = 6

    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.x_vel = self.START_VELOCITY
        self.y_vel = 0
        self.paddle_hit = False

    def draw(self, window):
        self.rect = pygame.draw.circle(window, self.COLOR, (self.x, self.y), self.radius)
    
    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel

    def reset(self):
        self.START_VELOCITY *= -1

        self.x = WIDTH//2
        self.y = HEIGHT//2
        self.y_vel = random.randint(-2, 2)
        self.x_vel = self.START_VELOCITY
        self.paddle_hit = False

# All ball collision cases
def ball_collision(ball: Ball, paddles: List[pygame.Rect]):
    # Ball and paddle collisions
    for paddle in paddles:
        if(pygame.Rect.colliderect(paddle, ball.rect)):
            ball.x_vel *= -1
            if(not ball.paddle_hit):
                ball.x_vel *= 1.5
                ball.paddle_hit = True

            # Divide paddle into 11 segments and determine which segment the ball hits
            y_difference = ball.rect.centery - paddle.y
            segment_hit = y_difference // (paddle.height//11)
            
            # Give the ball y-velocity depending on the segment hit
            new_velocity = (segment_hit - 5) * 2

            ball.y_vel = new_velocity
    
    # Ball and top/bottom edge collisions
    if(ball.rect.top <= 0):
        ball.y_vel *= -1
    if(ball.rect.bottom >= HEIGHT):
        ball.y_vel *= -1

# Paddle movement for 2-player game
def paddle_player_movement(keys, paddle_1: pygame.Rect, paddle_2: pygame.Rect):
    if keys[pygame.K_w] and paddle_1.top >= 0:
        paddle_1.y -= PADDLE_VELOCITY
    if keys[pygame.K_s] and paddle_1.bottom <= HEIGHT:
        paddle_1.y += PADDLE_VELOCITY

    if keys[pygame.K_UP] and paddle_2.top >= 0:
        paddle_2.y -= PADDLE_VELOCITY
    if keys[pygame.K_DOWN] and paddle_2.bottom <= HEIGHT:
        paddle_2.y += PADDLE_VELOCITY

# Reset the ball and paddles to the original position
def reset(ball: Ball, paddles: List[pygame.Rect]):
    ball.reset()
    for paddle in paddles:
        paddle.y = HEIGHT//2 - PADDLE_HEIGHT//2

# Drawing everything in the window
def draw(window: pygame.Surface, paddles: List[pygame.Rect], ball: Ball, left_score: int, right_score: int):
    window.fill(BLACK)

    left_score_text = SCORE_FONT.render(f"{left_score}", True, WHITE)
    right_score_text = SCORE_FONT.render(f"{right_score}", True, WHITE)

    window.blit(left_score_text, ((WIDTH//4 - left_score_text.get_width()//2), 20))
    window.blit(right_score_text, ((WIDTH * (3/4) - right_score_text.get_width()//2), 20))

    for paddle in paddles:
        pygame.draw.rect(window, WHITE, paddle)

    ball.draw(window)

    for i in range(10, HEIGHT, HEIGHT//20):
        pygame.draw.rect(window, WHITE, (WIDTH//2 - 5, i, 10, HEIGHT//40))

    pygame.display.update()

def main():
    run = True
    clock = pygame.time.Clock()

    paddle_1 = pygame.Rect(10, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
    paddle_2 = pygame.Rect(WIDTH - 10 - PADDLE_WIDTH, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)

    ball = Ball(WIDTH//2, HEIGHT//2, BALL_RADIUS)

    left_score = 0
    right_score = 0

    # Runs 60 times per second, determined by FPS
    while run:
        clock.tick(FPS)
        draw(WINDOW, [paddle_1, paddle_2], ball, left_score, right_score)

        # Check for quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        
        # Moving paddles
        keys = pygame.key.get_pressed()
        paddle_player_movement(keys, paddle_1, paddle_2)

        # Check collision and move the ball
        ball_collision(ball, [paddle_1, paddle_2])
        ball.move()

        # Check if either player wins
        if(ball.x <= 0):
            left_score += 1
            ball.reset()
        if(ball.x >= WIDTH):
            right_score += 1
            ball.reset()

    pygame.quit()

if __name__ == '__main__':
    main()