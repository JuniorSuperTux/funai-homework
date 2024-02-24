import sys, os
sys.path.append(os.path.dirname(__file__))
import math
import env


class GunEnv():
	def __init__(self, side: str) -> None:
		self.action_mapping = [["NONE"], ["AIM_LEFT"], ["AIM_RIGHT"], ["SHOOT"]]
		self.n_actions = len(self.action_mapping)
		
		self.side = side
		self.action = 0 
		self.observation = 0
		self.pre_reward = 0
		self.pre_scene_info = {"x":0, "y":0}
	    
	def set_scene_info(self, Scene_info: dict):
		"""
		Stores the given scene information into the environment.
		
		Parameters:
		scene_info (dict): A dictionary containing environment information.
		"""
		self.scene_info = Scene_info
	
	def reset(self):
		"""
		Resets the environment and returns the initial observation.
		
		Returns:
		observation: The initial state of the environment after reset.
		"""
		observation = self.__get_obs(self.scene_info)
		
		return observation
	
	def step(self, action: int):   
		"""
		Executes a given action in the environment and returns the resulting state.
		
		Parameters:
		action (int): The action to be performed, representing the squid's movement.
		
		Returns:
		observation: The current state of the environment after the action.
		reward (int): The reward obtained as a result of performing the action.
		done (bool): Indicates whether the game has ended (True if ended, False otherwise).
		info (dict): Additional information about the current state.
		"""
		reward = 0
		observation = self.__get_obs(self.scene_info)
		
		reward = self.__get_reward(observation)
		        
		done = self.scene_info["status"] != "GAME_ALIVE"
		
		info = {}
		
		return observation, reward, done, info
	
	##########  to do  ##########
	# TODO BREAKING WALLS ADDS SCORE
	def __get_obs(self, scene_info):
		map_arr = [[ 0 for y in range(env.MAP_HEIGHT_BLOCKS)] for x in range(env.MAP_WIDTH_BLOCKS)]
		observed_arr = [[ env.WALL_UNKNOWN for y in range(env.MAP_HEIGHT_BLOCKS)] for x in range(env.MAP_WIDTH_BLOCKS)]
		for wall in scene_info["walls_info"]:
			map_arr[wall["x"]//env.BLOCK_LENGTH][wall["y"]//env.BLOCK_LENGTH] = wall["lives"]

		corrected_x = scene_info["x"] + (env.BLOCK_LENGTH / 2)
		corrected_y = scene_info["y"] + (env.BLOCK_LENGTH / 2)

		arr_x, arr_y = corrected_x // env.BLOCK_LENGTH, corrected_y // env.BLOCK_LENGTH
		for dx in range(-env.GUN_RANGE_BLOCKS - 2, env.GUN_RANGE_BLOCKS + 3):
			for dy in range(-env.GUN_RANGE_BLOCKS - 2, env.GUN_RANGE_BLOCKS + 3):
				target_x, target_y = arr_x + dx, arr_y + dy
				if 0 <= target_x < env.MAP_WIDTH_BLOCKS and 0 <= target_y <= env.MAP_HEIGHT_BLOCKS:
					observed_arr[target_x][target_y] = env.wall_lives_map[map_arr[target_x][target_y]]

		bullet_info = scene_info["bullets_info"]
		if env.bullet_id(env.opposite_side(self.side)) in bullet_info.keys():
			opponent_bullet = bullet_info[env.bullet_id(env.opposite_side(self.side))]
			bullet_x = opponent_bullet["x"]
			bullet_y = opponent_bullet["y"]

		competitor_info = None
		for item in scene_info["competitor_info"]:
			if item["id"] == env.opposite_side(self.side):
				competitor_info = item


		bullet_x, bullet_y = -1, -1	
		opponent_x, opponent_y = competitor_info["x"], competitor_info["y"]


		observation = {
			"map": observed_arr,
			"opponent": {
				"relative_angle": env.get_degrees(opponent_y, corrected_y, opponent_x, corrected_x),
				"distance": env.get_distance(opponent_x - corrected_x, opponent_y - corrected_y),
			},
			"opponent_bullet": {
				"relative_angle": env.get_degrees(bullet_y, corrected_y, bullet_x, opponent_x),
				"distance": env.get_distance(bullet_x - corrected_x, bullet_y - corrected_y),
				"rotation": env.angle_map[opponent_bullet["rot"]]
			},
		}
		return observation
	    
	    
	##########  to do  ##########
	def __get_reward(self, observation):        
		reward = 0        
		
		
		return reward
	