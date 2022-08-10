from typing import List
import numpy as np
import pygame

pygame.init()
TEXT_FONT = pygame.font.SysFont("Roboto", 50)

WIDTH, HEIGHT = 700, 500

FPS = 240

WHITE = (255,255,255)
BLACK = (0,0,0)
BLUE = (0,0,255)

PADDLE_HEIGHT, PADDLE_WIDTH = 100, 20
PADDLE_VELOCITY = 6

BALL_RADIUS = 7

WINNING_SCORE = 10

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
        # pygame.draw.circle returns a rect around the ball, works as hitbox
        self.rect = pygame.draw.circle(
            window, self.COLOR, (self.x, self.y), self.radius)

    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel

    def reset(self):
        self.START_VELOCITY *= -1

        self.x = WIDTH//2
        self.y = HEIGHT//2
        self.y_vel = 0
        self.x_vel = self.START_VELOCITY
        self.paddle_hit = False

class PongGameAI:
    def __init__(self, w=640, h=480):
        self.display = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pong AI")
        
        self.w = w
        self.h = h

        self.frame_iteration = 0

        self.clock = pygame.time.Clock()

        self.paddle_1 = pygame.Rect(
            10, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.paddle_2 = pygame.Rect(WIDTH - 10 - PADDLE_WIDTH, HEIGHT //
                               2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)

        self.ball = Ball(WIDTH//2, HEIGHT//2, BALL_RADIUS)

        self.score_1 = 0
        self.score_2 = 0

    # All ball collision cases
    def ball_collision(self):
        paddle_num = 1
        paddle_hit = 0
        # Ball and paddle collisions
        for paddle in [self.paddle_1, self.paddle_2]:
            if(pygame.Rect.colliderect(paddle, self.ball.rect)):
                paddle_hit = paddle_num

                self.ball.x_vel *= -1
                if(not self.ball.paddle_hit):
                    self.ball.x_vel *= 1.5
                    self.ball.paddle_hit = True

                # Divide paddle into 11 segments and determine which segment the ball hits
                y_difference = self.ball.rect.centery - paddle.y
                segment_hit = y_difference // (paddle.height//20)
                
                # Give the ball y-velocity depending on the segment hit
                new_velocity = (segment_hit - 10) * 1.5

                self.ball.y_vel = new_velocity

            paddle_num += 1
        
        # Ball and top/bottom edge collisions
        if(self.ball.rect.top <= 0):
            self.ball.y_vel *= -1
        if(self.ball.rect.bottom >= HEIGHT):
            self.ball.y_vel *= -1

        return paddle_hit

    # Paddle movement for AI, action [up, stay, down]
    def paddle_movement(self, actions):
        if np.array_equal(actions[0], [1,0,0]) and self.paddle_1.top >= 0:
            self.paddle_1.y -= PADDLE_VELOCITY
        if np.array_equal(actions[0], [0,0,1]) and self.paddle_1.bottom <= HEIGHT:
            self.paddle_1.y += PADDLE_VELOCITY

        if np.array_equal(actions[1], [1, 0, 0]) and self.paddle_2.top >= 0:
            self.paddle_2.y -= PADDLE_VELOCITY
        if np.array_equal(actions[1], [0, 0, 1]) and self.paddle_2.bottom <= HEIGHT:
            self.paddle_2.y += PADDLE_VELOCITY

    def reset(self):
        self.score_1 = self.score_2 = 0
        self.paddle_1.y = self.paddle_2.y = HEIGHT//2 - PADDLE_HEIGHT//2
        self.ball.reset()
        self.frame_iteration = 0

    # Drawing everything in the window
    def update_ui(self):
        self.display.fill(BLACK)
        # Dotted line in the middle
        for i in range(10, HEIGHT, HEIGHT//20):
            pygame.draw.rect(self.display, WHITE, (WIDTH//2 - 5, i, 10, HEIGHT//40))

        # Score texts
        left_score_text = TEXT_FONT.render(f"{self.score_1}", True, WHITE)
        right_score_text = TEXT_FONT.render(f"{self.score_2}", True, WHITE)
        self.display.blit(left_score_text, ((WIDTH//4 - left_score_text.get_width()//2), 20))
        self.display.blit(right_score_text, ((WIDTH * (3/4) - right_score_text.get_width()//2), 20))

        for paddle in [self.paddle_1, self.paddle_2]:
            pygame.draw.rect(self.display, WHITE, paddle)

        self.ball.draw(self.display)   

        pygame.display.update()

    def play_step(self, action):
        self.frame_iteration += 1
        reward_1 = 0
        reward_2 = 0
        collisions = 0

        # Check for quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        self.update_ui()

        # Moving paddles
        self.paddle_movement(action)

        # Check collision and move the ball
        hit_paddle = self.ball_collision()
        if (hit_paddle != 0):
            collisions += 1
            reward_1 = 1 if hit_paddle == 1 else 0
            reward_2 = 1 if hit_paddle == 2 else 0

        self.ball.move()
        self.clock.tick(FPS)

        # Check if either player wins
        if(self.ball.x >= WIDTH):
            reward_1 = 10
            reward_2 = -10
            self.score_1 += 1
            self.ball.reset()
        if(self.ball.x <= 0):
            reward_2 = 10
            reward_1 = -10
            self.score_2 += 1
            self.ball.reset()

        game_over = False
        if(self.score_1 >= 10):
            reward_1 = 20
            reward_2 = -20
            game_over = True
        if(self.score_2 >= 10):
            reward_2 = 20
            reward_1 = -20
            game_over = True

        if(collisions >= 50):
            reward_1 = -10
            reward_2 = -10
            game_over = True

        return self.score_1, self.score_2, reward_1, reward_2, game_over