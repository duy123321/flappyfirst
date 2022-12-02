import torch
import random
import numpy as np
from collections import deque
from game import FlappyBirdAI
from snake import SnakeGameAI
from model import Linear_QNet, QTrainer
from helper import plot
import json
# from helper import plot

MAX_MEMORY = 1000000
BATCH_SIZE = 10000
LR = 0.001

class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 # randomness
        self.gamma = 0.95 # discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # popleft()
        self.model = None
        self.trainer = None
        self.model = Linear_QNet(4, 256, 2)#3 might be 2 as it is suppose to be the output size,
        #  also 11 might be changed as that is the input value
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
        self.maxScore = 0


    def get_state(self, game):
        #[y from ground, x from pipe, y from bottom of pipe, velocity of kirby]
        state = [
            # y from ground
            game.kirbY - 700,
            # x from pipe
            80 - game.pipeX,
            # y from bottom of pipe
            game.kirbY - game.heightOfBottom,
            # velocity of kirby
            game.kirbGravity
            ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        #for state, action, reward, nexrt_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = 80 - self.n_games
        final_move = [0,0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0,1)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)#this needs to make move = 0 or 1, so probably predict if jumping or not is ideal, calls foward
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        # print('This is final move: ', final_move)
        return final_move


def train():
    plot_scores = []
    plot_mean_scores = []
    max_score = []
    total_score = 0
    record = 0
    agent = Agent()
    game = FlappyBirdAI()
    while True:
        # get old state
        state_old = agent.get_state(game)

        # get move
        final_move = agent.get_action(state_old)

        # perform move and get new state
        reward, done, score = game.play_step(final_move)
        if reward is False:
            #  with open("data/plot_scores.json", "w") as f:
            #     json.dump({'episodes': [i+1 for i in range(len(plot_scores))],
            #                'scores': plot_scores}, f)
            #  with open("data/plot_mean_scores.json", "w") as f:
            #     json.dump({'episodes': [i+1 for i in range(len(plot_mean_scores))],
            #                'scores': plot_mean_scores}, f)
            #  with open("data/max_score.json", "w") as f:
            #     json.dump({'episodes': [i+1 for i in range(len(max_score))],
            #                'scores': max_score}, f)
            #  exit()
            x = 0
            while True:
                x+= 0
             
        agent.maxScore = max(agent.maxScore, score)
        state_new = agent.get_state(game)
        #

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # # remember
        agent.remember(state_old, final_move, reward, state_new, done)


        if done:
            # train long memory, plot result
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()

            print('Game', agent.n_games, 'Score', score, 'Record:', record)

            plot_scores.append(score)
            max_score.append(agent.maxScore)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores, max_score)


if __name__ == '__main__':
    train()