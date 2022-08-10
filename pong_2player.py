from typing import List
import pygame

pygame.init()
TEXT_FONT = pygame.font.SysFont("Roboto", 50)

WIDTH, HEIGHT = 700, 500

FPS = 60

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

class PongGame:
    def __init__(self, w=640, h=480):
        self.display = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pong AI")
        
        self.w = w
        self.h = h

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
        # Ball and paddle collisions
        for paddle in [self.paddle_1, self.paddle_2]:
            if(pygame.Rect.colliderect(paddle, self.ball.rect)):
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
        
        # Ball and top/bottom edge collisions
        if(self.ball.rect.top <= 0):
            self.ball.y_vel *= -1
        if(self.ball.rect.bottom >= HEIGHT):
            self.ball.y_vel *= -1

    # Paddle movement for 2-player game
    def paddle_player_movement(self, keys):
        if keys[pygame.K_w] and self.paddle_1.top >= 0:
            self.paddle_1.y -= PADDLE_VELOCITY
        if keys[pygame.K_s] and self.paddle_1.bottom <= HEIGHT:
            self.paddle_1.y += PADDLE_VELOCITY

        if keys[pygame.K_UP] and self.paddle_2.top >= 0:
            self.paddle_2.y -= PADDLE_VELOCITY
        if keys[pygame.K_DOWN] and self.paddle_2.bottom <= HEIGHT:
            self.paddle_2.y += PADDLE_VELOCITY

    def reset(self):
        self.score_1 = self.score_2 = 0
        self.paddle_1.y = self.paddle_2.y = HEIGHT//2 - PADDLE_HEIGHT//2
        self.ball.reset()

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

    def play_step(self):
        # Check for quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset()

        self.update_ui()

        # Moving paddles
        keys = pygame.key.get_pressed()
        self.paddle_player_movement(keys)

        # Check collision and move the ball
        self.ball_collision()
        self.ball.move()
        
        self.clock.tick(FPS)

        # Check if either player wins
        if(self.ball.x <= 0):
            self.score_1 += 1
            self.ball.reset()
        if(self.ball.x >= WIDTH):
            self.score_2 += 1
            self.ball.reset()

        return self.score_1, self.score_2

if __name__ == '__main__':
    game = PongGame()

    while True:
        score_1, score_2 = game.play_step()
        
        if(score_1 >= 10 or score_2 >= 10):
            win_text = "Player 1 wins!" if score_1 >= 10 else "Player 2 wins!"

            win_text_render = TEXT_FONT.render(win_text, True, BLUE)
            game.display.blit(win_text_render, (WIDTH//2 - win_text_render.get_width() //
                        2, HEIGHT//2 - win_text_render.get_height()//2))
            pygame.display.update()
            pygame.time.delay(5000)

            game.reset()

    pygame.quit()
