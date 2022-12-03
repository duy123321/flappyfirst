from os import stat
from re import X
from telnetlib import STATUS
from typing import final
import torch
import random
import numpy as np
from collections import deque
from gameQ import FlappyBirdAIQ
import json
# from helper import plot


class AgentQ:

    def __init__(self):
        self.train = train  # train or run
        self.discount_factor = 0.95  # q-learning discount factor
        self.alpha = 0.7  # learning rate
        # self.epsilon = 0.1  # chance to explore vs take local optimum
        self.reward = {0: 0, 1: -1000}  # reward function, focus on only not dying

        # Stabilize and converge to optimal policy
        self.alpha_decay = 0.00003  # 20,000 episodes to fully decay
        # self.epsilon_decay = 0.00001  # 10,000 episodes to not explore anymore

        # Save states
        self.episode = 0 # number of game attempts
        self.previous_action = 0
        self.previous_state = "0_0_0_0"  # initial position (x0: distasnce to pipe, y0: height from bottom pipe, vel: velocity of bird, y1:height from ground) 
        self.moves = [] # a list of moves that the bird did
        self.scores = []
        self.max_score = 0

        self.q_values = {}  # q-table[state][action] decides which action to take by comparing q-values
        self.load_qvalues()
        self.load_training_states()

    def init_qvalues(self, state):
        """
        Initialise q values if state not yet seen.
        :param state: current state
        """
        if self.q_values.get(state) is None:
            self.q_values[state] = [0, 0, 0] # [Q of no action, Q of flap action, Times experienced this state]

    def load_qvalues(self):
        """Load q values and from json file."""
        print("Loading Q-table states from json file...")
        try:
            with open("data/q_values_resume.json", "r") as f:
                self.q_values = json.load(f)
        except IOError:
            self.init_qvalues(self.previous_state)

    def load_training_states(self):
        """Load current training state from json file."""
        if self.train:
            print("Loading training states from json file...")
            try:
                with open("data/training_values_resume.json", "r") as f:
                    training_state = json.load(f)
                    self.episode = training_state['episodes'][-1]
                    self.scores = training_state['scores']
                    self.alpha = max(self.alpha - self.alpha_decay * self.episode, 0.1)
                    # self.epsilon = max(self.epsilon - self.epsilon_decay * self.episode, 0)
                    self.max_score = max(self.scores)
            except IOError:
                pass



    def get_state(self, game):
        # state = (
        #     # x0: distance from pipe
        #     int(game.pipeX - 80),
        #     # y0: height from bottom of pipe
        #     int(game.heightOfBottom - game.kirbY),
        #     # velocity of kirby
        #     int(game.kirbGravity),
        #     # y1 height from ground
        #     int(700 - game.kirbY),
        # )
        state = str(int(game.pipeX - 80)) + "_" + str(int(game.heightOfBottom - game.kirbY)) + "_" + str(int(game.kirbGravity)) + "_" + str(int(700 - game.kirbY))
        self.init_qvalues(state)
        return state

    #This function if higher score is reached, set values as 0 for all moves in history (this is before the bird dies)
    def end_episode(self, game):
        pass
        

    def updateQVals(self, game, score):
        #incremet the episode count
        self.episode += 1
        #get the scores and save if the score is better
        self.scores.append(score)
        self.max_score = max(score, self.max_score)

        history = list(reversed(self.moves)) # get list of moves performed
        #tell if bird died from top of the map or the top of the pipe
        high_death_flag = True if game.kirbY < (game.heightOfBottom - 300) else False
        countMove, last_flap = 0, True


        for move in history:
            countMove += 5
            state, action, new_state = move
            self.q_values[state][2] += 1  # number of times this state has been seen
            curr_reward = self.reward[0]
            if countMove <= 5:
                # Penalise last 2 states before dying
                curr_reward = self.reward[1]
                if action: # true if no action flap occured
                    last_flap = False
            elif (last_flap or high_death_flag) and action:
                    # Penalise flapping
                    curr_reward = self.reward[1]
                    last_flap = False
                    high_death_flag = False
            self.q_values[state][action] = (1 - self.alpha) * (self.q_values[state][action]) + \
                                               self.alpha * (curr_reward + self.discount_factor *
                                                             max(self.q_values[new_state][0:2]))
            # print("Move: ", move)
            # print("Q Value: ", self.q_values[state][action])
        if self.alpha > 0.1:
                self.alpha = max(self.alpha_decay - self.alpha_decay, 0.1)
        print(self.episode, self.max_score)
        # print('-------------------------------------------------------------')

    def get_action(self, state):
        # print(state)
        if self.train:
            self.moves.append((self.previous_state, self.previous_action, state))  # add the experience to history
            self.reduce_moves()
            self.previous_state = state  # update the last_state with the current state

            # Epsilon greedy policy for action, chance to explore
            # Remove since exploration is not efficient or required for this agent and environment
            # if random.random() <= self.epsilon:
            #     self.previous_action = random.choice([0, 1])
            #     return self.previous_action

        # Best action with respect to current state, default is 0 (do nothing), 1 is flap
        self.previous_action = 0 if self.q_values[state][0] >= self.q_values[state][1] else 1
        return self.previous_action
    
    def reduce_moves(self, reduce_len=1000000):
        """
        Reduce length of moves if greater than reduce_len.
        :param reduce_len: reduce moves in memory if greater than this length, default 1 million
        """
        if len(self.moves) > reduce_len:
            history = list(reversed(self.moves[:reduce_len]))
            for move in history:
                state, action, new_state = move
                # Save q_values with default of 0 reward (bird not yet died)
                self.q_values[state][action] = (1 - self.alpha) * (self.q_values[state][action]) + \
                                               self.alpha * (self.reward[0] + self.discount_factor *
                                                             max(self.q_values[new_state][0:2]))
            self.moves = self.moves[reduce_len:]

    def save_qvalues(self):
        """Save q values to json file."""
        if self.train:
            print(f"Saving Q-table with {len(self.q_values.keys())} states to file...")
            with open("data/q_values_resume.json", "w") as f:
                json.dump(self.q_values, f)

    def save_training_states(self):
        if self.train:
            """Save current training state to json file."""
            print(f"Saving training states with {self.episode} episodes to file...")
            with open("data/training_values_resume.json", "w") as f:
                json.dump({'episodes': [i+1 for i in range(self.episode)],
                           'scores': self.scores}, f)


def train():
    agent = AgentQ()
    game = FlappyBirdAIQ()
    stat = True
    while stat:
         state_old = agent.get_state(game)

         final_move = agent.get_action(state_old)

         reward, done, score, stat = game.play_step(final_move)

         if reward is False:
             agent.save_qvalues()
             agent.save_training_states()
             exit

         if done or score > 100000:
             agent.updateQVals(game, score)
             game.reset()
        


if __name__ == '__main__':
    train()