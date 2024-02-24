"""
The template of the main script of the machine learning process
"""
import pygame
import os
import sys
import pickle
from datetime import datetime
import numpy as np
import pandas as pd
import math
sys.path.append(os.path.dirname(__file__))
from env import *
from ml.ml_movement_env import MovementEnv
from ml.ml_gun_env import GunEnv
from QT import QLearningTable


class MLPlay:
    def __init__(self, ai_name, *args, **kwargs):
        """
        Constructor

        @param side A string "1P" or "2P" indicates that the `MLPlay` is used by
               which side.
        """        
        self.side = ai_name
        print(f"Initial Game {ai_name} ml script")
        self.time = 0

        self.movement_env = MovementEnv(self.side)
        self.gun_env = GunEnv(self.side)

        self.movement_action = self.movement_env.action
        self.gun_action = self.gun_env.action

        self.movement_state = [self.movement_env.observation]
        self.gun_state = [self.gun_env.observation]

        self.movement_QT = QLearningTable(actions=list(range(self.movement_env.n_actions)), e_greedy=0)
        self.gun_QT = QLearningTable(actions=list(range(self.gun_env.n_actions)), e_greedy=0)
        
        folder_path = os.path.dirname(__file__) + '/save'                              
        self.movement_QT.q_table = pd.read_pickle(folder_path+'/movement_qtable.pickle')
        self.gun_QT.q_table = pd.read_pickle(folder_path+'/gun_qtable.pickle')
        
        self.movement_action_mapping = self.movement_env.action_mapping
        self.gun_action_mapping = self.gun_env.action_mapping


    def update(self, scene_info: dict, keyboard=[], *args, **kwargs):
        """
        Generate the command according to the received scene information
        """
        
        
        if scene_info["status"] != "GAME_ALIVE":            
            return "RESET"
        
        self.env.set_scene_info(scene_info)        
        self.movement_env.set_scene_info(scene_info)
        self.gun_env.set_scene_info(scene_info)

        movement_observation, movement_reward, movement_done, movement_info = self.movement_env.step(self.action)
        gun_observation, gun_reward, gun_done, gun_info = self.gun_env.step(self.action)

        self.movement_state = [movement_observation]
        self.gun_state = [gun_observation]
        movement_action = self.movement_QT.choose_action(str(self.movement_state))
        gun_action = self.gun_QT.choose_action(str(self.gun_state))
        
        self.movement_action = movement_action
        self.gun_action = gun_action
        
        # FIXME TODO CHANGE HERE
        command = self.action_mapping[action]
              
        return command


    def reset(self):
        """
        Reset the status
        """
        print(f"reset Game {self.side}")
        
    
    