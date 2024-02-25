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
import env
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
		
		self.movement_state_ = [self.movement_env.observation]
		self.gun_state_ = [self.gun_env.observation]
		
		self.movement_QT = QLearningTable(actions=list(range(self.movement_env.n_actions)))
		self.gun_QT = QLearningTable(actions=list(range(self.gun_env.n_actions)))

		self.gun_refreshed = True
		
		folder_path = './ml/save'
		os.makedirs(folder_path, exist_ok=True)
		
		keep_training = False
		if keep_training:
			self.movement_QT.q_table = pd.read_pickle(f'.\\ml\\save\\movement_qtable_{self.side}.pickle')
			self.gun_QT.q_table = pd.read_pickle(f'.\\ml\\save\\gun_qtable_{self.side}.pickle')
		else:
			self.movement_QT.q_table.to_pickle(f'.\\ml\\save\\movement_qtable_{self.side}.pickle')
			self.gun_QT.q_table.to_pickle(f'.\\ml\\save\\gun_qtable_{self.side}.pickle')
		
		self.movement_action_mapping = self.movement_env.action_mapping
		self.gun_action_mapping = self.gun_env.action_mapping
	
	def update(self, scene_info: dict, keyboard=[], *args, **kwargs):
		"""
		Generate the command according to the received scene information
		"""                
		if scene_info["status"] != "GAME_ALIVE":            
			return "RESET"

		self.gun_env.set_scene_info(scene_info)	
		gun_observation, gun_reward, gun_done, gun_info = self.gun_env.step(self.gun_action)
		self.gun_state_ = [gun_observation]
		gun_action = self.gun_QT.choose_action(str(self.gun_state_))
		if not env.id_exists(env.bullet_id(self.side), scene_info["bullets_info"]) and not self.gun_refreshed:
			self.gun_QT.learn_from_episode()
			self.gun_refreshed = True
		if gun_action == 3: # SHOOT
			self.gun_refreshed = False
		self.gun_QT.store_experience(str(self.gun_state), self.gun_action, gun_reward, str(self.gun_state_))
		self.gun_action = gun_action
		self.gun_state = self.gun_state_

		if self.gun_action == 0: # NONE
			self.movement_env.set_scene_info(scene_info)
			movement_observation, movement_reward, movement_done, movement_info = self.movement_env.step(self.gun_action)
			self.movement_state_ = [movement_observation]
			self.movement_QT.learn(str(self.movement_state), self.movement_action, movement_reward, str(self.movement_state_))
			self.movement_state = self.movement_state_
		if gun_action == 0: # NONE
			movement_action = self.movement_QT.choose_action(str(self.movement_state_))
			self.movement_action = movement_action

		command = self.gun_action_mapping[self.gun_action] if self.gun_action != 0 else self.movement_action_mapping[self.movement_action]
		
		return command
	
	
	def reset(self):
		"""
		Reset the status
		"""
		print(f"reset Game {self.side}")
		self.movement_QT.to_pickle(f'.\\ml\\save\\movement_qtable_{self.side}.pickle')
		self.gun_QT.to_pickle(f'.\\ml\\save\\gun_qtable_{self.side}.pickle')