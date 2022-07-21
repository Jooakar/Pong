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


PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100
BALL_RADIUS = 7

class Paddle:
    COLOR = WHITE
    VELOCITY = 6
    
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
    
    def draw(self, window):
        pygame.draw.rect(window, WHITE, self.rect)

    def move(self, up=True):
        if(up):
            self.rect.y -= self.VELOCITY
        else:
            self.rect.y += self.VELOCITY

    def reset(self):
        self.rect.y = HEIGHT//2 - PADDLE_HEIGHT//2

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
def ball_collision(ball: Ball, paddles: List[Paddle]):
    # Ball and paddle collisions
    for paddle in paddles:
        if(pygame.Rect.colliderect(paddle.rect, ball.rect)):
            ball.x_vel *= -1
            if(not ball.paddle_hit):
                ball.x_vel *= 1.5
                ball.paddle_hit = True

            # Divide paddle into 11 segments and determine which segment the ball hits
            y_difference = ball.rect.centery - paddle.rect.y
            segment_hit = y_difference // (paddle.rect.height//11)
            
            # Give the ball y-velocity depending on the segment hit
            new_velocity = (segment_hit - 5) * 2

            ball.y_vel = new_velocity
    
    # Ball and top/bottom edge collisions
    if(ball.rect.top <= 0):
        ball.y_vel *= -1
    if(ball.rect.bottom >= HEIGHT):
        ball.y_vel *= -1

# Paddle movement for 2-player game
def paddle_movement(keys, left_paddle: Paddle, right_paddle: Paddle):
    if keys[pygame.K_w] and left_paddle.rect.top >= 0:
        left_paddle.move(up=True)
    if keys[pygame.K_s] and left_paddle.rect.bottom <= HEIGHT:
        left_paddle.move(up=False)

    if keys[pygame.K_UP] and right_paddle.rect.top >= 0:
        right_paddle.move(up=True)
    if keys[pygame.K_DOWN] and right_paddle.rect.bottom <= HEIGHT:
        right_paddle.move(up=False)

# Reset the ball and paddles to the original position
def reset(ball: Ball, paddles: List[Paddle]):
    ball.reset()
    for paddle in paddles:
        paddle.reset()

# Drawing everything in the window
def draw(window: pygame.Surface, paddles: List[Paddle], ball: Ball, left_score: int, right_score: int):
    window.fill(BLACK)

    left_score_text = SCORE_FONT.render(f"{left_score}", True, WHITE)
    right_score_text = SCORE_FONT.render(f"{right_score}", True, WHITE)

    window.blit(left_score_text, ((WIDTH//4 - left_score_text.get_width()//2), 20))
    window.blit(right_score_text, ((WIDTH * (3/4) - right_score_text.get_width()//2), 20))

    for paddle in paddles:
        paddle.draw(window)

    ball.draw(window)

    for i in range(10, HEIGHT, HEIGHT//20):
        pygame.draw.rect(window, WHITE, (WIDTH//2 - 5, i, 10, HEIGHT//40))

    pygame.display.update()

def main():
    run = True
    clock = pygame.time.Clock()

    left_paddle = Paddle(10, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
    right_paddle = Paddle(WIDTH - 10 - PADDLE_WIDTH, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = Ball(WIDTH//2, HEIGHT//2, BALL_RADIUS)

    left_score = 0
    right_score = 0

    # Runs 60 times per second, determined by FPS
    while run:
        clock.tick(FPS)
        draw(WINDOW, [left_paddle, right_paddle], ball, left_score, right_score)

        # Check for quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        
        # Moving paddles
        keys = pygame.key.get_pressed()
        paddle_movement(keys, left_paddle, right_paddle)

        # Check collision and move the ball
        ball_collision(ball, [left_paddle, right_paddle])
        ball.move()

        # Check if either player wins
        if(ball.x <= 0):
            left_score += 1
            ball.reset()
            clock.tick(5)
        if(ball.x >= WIDTH):
            right_score += 1
            ball.reset()
            clock.tick(5)

    pygame.quit()

if __name__ == '__main__':
    main()