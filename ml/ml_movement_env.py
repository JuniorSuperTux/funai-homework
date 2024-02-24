import sys, os
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
		
		reward = self.__get_reward(observation)
		        
		done = self.scene_info["status"] != "GAME_ALIVE"
		
		info = {}
		
		return observation, reward, done, info
	
	##########  to do  ##########
	def __get_obs(self, scene_info):      

		map_arr = [[ 0 for y in range(env.MAP_HEIGHT_BLOCKS)] for x in range(env.MAP_WIDTH_BLOCKS)]
		for wall in scene_info["walls_info"]:
			map_arr[wall["x"]//env.BLOCK_LENGTH][wall["y"]//env.BLOCK_LENGTH] = wall["lives"]
		corrected_x = scene_info["x"] + (env.BLOCK_LENGTH / 2)
		corrected_y = scene_info["y"] + (env.BLOCK_LENGTH / 2)
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
		if env.bullet_id(env.opposite_side(self.side)) in bullet_info.keys():
			opponent_bullet = bullet_info[env.bullet_id(env.opposite_side(self.side))]
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

		observation = {
			# Unsure if this helps
			"blurred": {
				"top_left": sum(map(sum, map_arr[0:arr_x][0:arr_y])),
				"bottom_left": sum(map(sum, map_arr[0:arr_x][arr_y+1:-1])),
				"top_right": sum(map(sum, map_arr[arr_y+1:-1][0:arr_y])),
				"bottom_right": sum(map(sum, map_arr[arr_x+1, -1][arr_y+1:-1]))
			},
			"angle": env.angle_map[scene_info["angle"]],
			"nearby": {
				"top_left":     bool(topleft | top),
				"bottom_left":  bool(bottomleft | bottom),
				"top_right":    bool(topright | left),
				"bottom_right": bool(bottomright | right),
				"top":    bool(top),
				"bottom": bool(bottom),
				"left":   bool(left),
				"right":  bool(right)
			},
			"opponent": {
				"relative_angle": env.get_degrees(opponent_y, corrected_y, opponent_x, corrected_x),
				"distance": env.get_distance(opponent_x - corrected_x, opponent_y - corrected_y),
				"gun_angle": env.angle_map[competitor_info["gun_angle"]]
			},
			"opponent_bullet": {
				"relative_angle": env.get_degrees(bullet_y, corrected_y, bullet_x, opponent_x),
				"distance": env.get_distance(bullet_x - corrected_x, bullet_y - corrected_y),
				"rotation": env.angle_map[opponent_bullet["rot"]]
			},
			"oil_station": {
				"relative_angle": env.get_degrees(oil_station_y, corrected_y, oil_station_x, corrected_x),
				"distance": env.get_distance(oil_station_x - corrected_x, oil_station_y - corrected_y)
			},
			"bullet_station": {
				"relative_angle": env.get_degrees(bullet_station_y, corrected_y, bullet_station_x, corrected_x),
				"distance": env.get_distance(bullet_station_x - corrected_x, bullet_station_y - corrected_y)
			}
		}
		return observation
	    
	    
	##########  to do  ##########
	def __get_reward(self, observation):        
		reward = 0        
		
		
		return reward
