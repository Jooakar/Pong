from collections import deque
import torch
import random
import numpy as np

from collections import deque
from pong_ai import PongGameAI
from model import Linear_QNet, QTrainer

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:
    def __init__(self, paddle_num = 2):
        self.paddle_num = paddle_num
        self.score = 0
        self.n_games = 0
        self.epsilon = 0
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY)

        self.model = Linear_QNet(8, 256, 3)
        self.trainer = QTrainer(self.model, LR, self.gamma)

    def get_state(self, game: PongGameAI):
        paddle = game.paddle_1 if self.paddle_num == 1 else game.paddle_2
        opponent_paddle = game.paddle_1 if self.paddle_num == 2 else game.paddle_2

        state = [
            (game.ball.x_vel > 0 and self.paddle_num == 2), # ball approaching
            not (game.ball.x_vel > 0 and self.paddle_num == 2), # ball leaving

            game.ball.y_vel > 0, # ball going down
            game.ball.y_vel < 0, # ball going up

            game.ball.y < paddle.y, # ball above own paddle
            game.ball.y > paddle.y, # ball below own paddle

            paddle.y > opponent_paddle.y, # opponent above own paddle
            paddle.y < opponent_paddle.y # opponent below own paddle
        ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, game_over):
        self.memory.append((state, action, reward, next_state, game_over))

    def train_long_memory(self):
        if(len(self.memory) > BATCH_SIZE):
            mini_sample = random.sample(self.memory, k = BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, game_overs = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, game_overs)

    def train_short_memory(self, state, action, reward, next_state, game_over):
        self.trainer.train_step(state, action, reward, next_state, game_over)

    def get_action(self, state):
        self.epsilon = 80 - self.n_games
        final_move = [0,0,0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0,2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move

def train():
    agent_1 = Agent(1)
    agent_2 = Agent(2)
    game = PongGameAI()

    agent_1_highscore = 0
    agent_2_highscore = 0

    while True:
        # Get old state
        state_old = agent_1.get_state(game)
        
        # Get move
        final_move_1 = agent_1.get_action(state_old)
        final_move_2 = agent_2.get_action(state_old)

        score_1, score_2, reward_1, reward_2, game_over = game.play_step([final_move_1, final_move_2])

        state_new = agent_1.get_state(game)
        
        agent_1.score += reward_1
        agent_1.train_short_memory(state_old, final_move_1, reward_1, state_new, game_over)
        agent_1.remember(state_old, final_move_1, reward_1, state_new, game_over)

        agent_2.score += reward_2
        agent_2.train_short_memory(state_old, final_move_2, reward_2, state_new, game_over)
        agent_2.remember(state_old, final_move_2, reward_2, state_new, game_over)

        if(game_over):
            agent_1.n_games += 1
            agent_2.n_games += 1

            agent_1.train_long_memory()
            agent_2.train_long_memory()

            if(game.score_1 >= 10 and agent_1.score > agent_1_highscore):
                agent_1.model.save("left_paddle.pth")
                agent_1_highscore = agent_1.score
            elif(game.score_2 >= 10 and agent_2.score > agent_2_highscore):
                agent_2.model.save("right_paddle.pth")
                agent_2_highscore = agent_2.score

            game.reset()

            print('Game', agent_1.n_games, 'Score', score_1, score_2)

if __name__ == '__main__':
    train()