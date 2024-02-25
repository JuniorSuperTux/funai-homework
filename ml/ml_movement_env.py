from collections import OrderedDict
import sys, os

from numpy.random import f

sys.path.append(os.path.dirname(__file__))
import env

class MovementEnv():
	def __init__(self, side: str) -> None:                                                                        
		self.action_mapping = [["NONE"], ["TURN_LEFT"], ["TURN_RIGHT"], ["FORWARD"], ["BACKWARD"]]
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
		
		reward = self.__get_reward(observation, self.action_mapping[action][0])
		        
		done = self.scene_info["status"] != "GAME_ALIVE"
		
		info = {}
		
		return observation, reward, done, info
	
	##########  to do  ##########
	def __get_obs(self, scene_info):      

		map_arr = [[ 0 for y in range(env.MAP_HEIGHT_BLOCKS)] for x in range(env.MAP_WIDTH_BLOCKS)]
		for wall in scene_info["walls_info"]:
			map_arr[wall["x"]//env.BLOCK_LENGTH][wall["y"]//env.BLOCK_LENGTH] = wall["lives"]
		corrected_x = int(scene_info["x"] + (env.BLOCK_LENGTH / 2))
		corrected_y = int(scene_info["y"] + (env.BLOCK_LENGTH / 2))
		arr_x, arr_y = corrected_x // env.BLOCK_LENGTH, corrected_y // env.BLOCK_LENGTH

		bottom = bool(map_arr[arr_x][arr_y+1]) if arr_y + 1 < env.MAP_HEIGHT_BLOCKS else True
		top = bool(map_arr[arr_x][arr_y-1]) if arr_y - 1 >= 0 else True
		right = bool(map_arr[arr_x+1][arr_y]) if arr_x + 1 < env.MAP_WIDTH_BLOCKS else True
		left = bool(map_arr[arr_x-1][arr_y]) if arr_x - 1 >= 0 else True
		topleft = bool(map_arr[arr_x-1][arr_y+1]) if arr_x - 1 >= 0 and arr_y + 1 < env.MAP_HEIGHT_BLOCKS else True
		topright = bool(map_arr[arr_x+1][arr_y+1]) if arr_x + 1 < env.MAP_WIDTH_BLOCKS and arr_y + 1 < env.MAP_HEIGHT_BLOCKS else True
		bottomleft = bool(map_arr[arr_x-1][arr_y-1]) if arr_x - 1 >= 0 and arr_y - 1 >= 0 else True
		bottomright = bool(map_arr[arr_x+1][arr_y-1]) if arr_x + 1 < env.MAP_WIDTH_BLOCKS and arr_y - 1 >= 0 else True

		competitor_info = None
		for item in scene_info["competitor_info"]:
			if item["id"] == env.opposite_side(self.side):
				competitor_info = item
		
		opponent_x, opponent_y = competitor_info["x"], competitor_info["y"]
		bullet_x, bullet_y = -1, -1
		oil_station_x, oil_station_y = -1, -1
		bullet_station_x, bullet_station_y = -1, -1
		bullet_info = scene_info["bullets_info"]
		oil_station_info = env.get_nearest(scene_info["oil_stations_info"])
		bullet_station_info = env.get_nearest(scene_info["bullet_stations_info"])
		opponent_bullet = None
		if env.id_exists(env.bullet_id(env.opposite_side(self.side)), bullet_info):
			opponent_bullet = env.get_by_id(env.bullet_id(env.opposite_side(self.side)), bullet_info)
			bullet_x = opponent_bullet["x"]
			bullet_y = opponent_bullet["y"]
		if oil_station_info is not None:
			oil_station_x = oil_station_info["x"]
			oil_station_y = oil_station_info["y"]
		if bullet_station_info is not None:
			bullet_station_x = bullet_station_info["x"]
			bullet_station_y = bullet_station_info["y"]

#		damaged_walls = [wall for wall in scene_info["walls_info"] if wall["lives"] != 4]
#		nearest_damanged_wall = env.get_nearest(damaged_walls)

		observation = OrderedDict([
			# Unsure if this helps
			("top_left_walls", sum(map(sum, map_arr[0:arr_x][0:arr_y]))),
			("top_left_spaces", (arr_x - 0) * (arr_y - 0)),
			("bottom_left_walls", sum(map(sum, map_arr[0:arr_x][arr_y+1:]))),
			("bottom_left_spaces", (arr_x - 0) * (env.MAP_HEIGHT_BLOCKS - arr_y)),
			("top_right_walls", sum(map(sum, map_arr[arr_x+1:][0:arr_y]))),
			("top_right_spaces", (env.MAP_WIDTH_BLOCKS - arr_x) * (arr_y - 0)),
			("bottom_right_walls", sum(map(sum, map_arr[arr_x+1:][arr_y+1:]))),
			("bottom_right_spaces", (env.MAP_WIDTH_BLOCKS - arr_x) * (env.MAP_HEIGHT_BLOCKS - arr_y)),

			("angle", env.angle_map[env.make_angle_positive(scene_info["angle"])]),
			("bullet_cnt", scene_info["power"]),
			("oil_cnt", scene_info["oil"] // 10),

			("TOPLEFT",     bool(topleft | top | left)),
			("BOTTOMLEFT",  bool(bottomleft | bottom | left)),
			("TOPRIGHT",    bool(topright | top | right)),
			("BOTTOMRIGHT", bool(bottomright | bottom | right)),
			("TOP",    bool(top)),
			("BOTTOM", bool(bottom)),
			("LEFT",   bool(left)),
			("RIGHT",  bool(right)),

			("opponent_relative_angle", env.get_degrees(opponent_y, corrected_y, opponent_x, corrected_x)),
			("opponent_distance", env.get_distance(opponent_x, corrected_x, opponent_y, corrected_y)),
			("opponent_gun_angle", env.angle_map[env.make_angle_positive(competitor_info["gun_angle"])]),

			("bullet_relative_angle", env.get_degrees(bullet_y, corrected_y, bullet_x, opponent_x)),
			("bullet_distance", env.get_distance(bullet_x, corrected_x, bullet_y, corrected_y)),
			("bullet_rotation", env.angle_map[env.make_angle_positive(opponent_bullet["rot"])] if opponent_bullet else -1),

			("oil_station_relative_angle", env.get_degrees(oil_station_y, corrected_y, oil_station_x, corrected_x)),
			("oil_station_distance", env.get_distance(oil_station_x, corrected_x, oil_station_y, corrected_y)),

			("relative_angle", env.get_degrees(bullet_station_y, corrected_y, bullet_station_x, corrected_x)),
			("distance", env.get_distance(bullet_station_x, corrected_x, bullet_station_y, corrected_y)),
		])
		return observation
	    
	    
	##########  to do  ##########
	def __get_reward(self, observation, action):
		def opposite_angle(angle: str):
			index = env.angle_map.values().index(angle)
			index += 4
			if index > 7: index -= 7
			return env.angle_map.values()[index]
		def to_angle(angle: str):
			return env.angle_map.keys()[env.angle_map.values().index(angle)]
		
		if observation[observation["angle"]]:
			if action == "FORWARD":
				reward += -10
			elif action == "BACKWARD":
				if observation[opposite_angle]:
					reward += -10
			else:
				turn_left_dist = env.get_index_difference_lambda(env.angle_map.values(), observation["angle"], lambda x: not observation[opposite_angle(x)], True) # ++Index
				turn_right_dist = env.get_index_difference_lambda(env.angle_map.values(), observation["angle"], lambda x: not observation[opposite_angle(x)], False) # --Index
				if turn_right_dist < turn_left_dist:
					if action == "TURN_RIGHT":
						reward += 10
					elif action == "TURN_LEFT":
						reward += 5
				elif turn_right_dist > turn_left_dist:
					if action == "TURN_LEFT":
						reward += 10
					elif action == "TURN_RIGHT":
						reward += 5
				else:
					reward += 5

		
				
		reward = 0
		return reward
