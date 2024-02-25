"""
The template of the main script of the machine learning process
"""
     
from calendar import c
import sys
import os
sys.path.append(os.path.dirname(__file__))
import pygame
import env

class MLPlay:
	def __init__(self, ai_name, *args, **kwargs):
		"""
		Constructor
		
		@param ai_name A string "1P" or "2P" indicates that the `MLPlay` is used by
		       which side.
		"""
		self.side = ai_name
		print(f"Initial Game {ai_name} ml script")
		self.time = 0

	def update(self, scene_info: dict, keyboard=[], *args, **kwargs):
		#if self.side == "2P":
		#    print("POsition {} {}".format(scene_info["x"] + 25, scene_info["y"] + 25))
#		if self.side == "2P":
#			print(scene_info["bullets_info"])        
		corrected_x = scene_info["x"] + int(env.BLOCK_LENGTH / 2)
		corrected_y = scene_info["y"] + int(env.BLOCK_LENGTH / 2)
		
		competitor_info = None
		for item in scene_info["competitor_info"]:
			if item["id"] == env.opposite_side(self.side):
				competitor_info = item
		
		if self.side == "1P":
			print(competitor_info["gun_angle"])
		opponent_x, opponent_y = competitor_info["x"], competitor_info["y"]
#		if self.side == "2P":
#			print("GUN_DEGREE:{}, CAR_DEGREE: {}".format(scene_info["gun_angle"], env.get_degrees(opponent_y, corrected_y, opponent_x, corrected_x)))
		"""
		Generate the command according to the received scene information
		"""
		# if scene_info["used_frame"] == 1:
		#     print(f"{self.side}_scene_info_{scene_info.keys()}")
		#     if scene_info["id"] == "1P":
		#         print(f'1P_competitor_info{scene_info["competitor_info"]}')
		#     else:
		#         print(f'2P_competitor_info{scene_info["competitor_info"]}')
		# print(keyboard)        
		if scene_info["status"] != "GAME_ALIVE":
			# print(scene_info)
			return "RESET"        
		command = []
		if self.side == "1P":
			if pygame.K_RIGHT in keyboard:
				command.append("TURN_RIGHT")
			elif pygame.K_LEFT in keyboard:
				command.append("TURN_LEFT")
			elif pygame.K_UP in keyboard:
				command.append("FORWARD")
			elif pygame.K_DOWN in keyboard:
				command.append("BACKWARD")
			
			if pygame.K_z in keyboard:
				command.append("AIM_LEFT")
			elif pygame.K_x in keyboard:
				command.append("AIM_RIGHT")
			
			if pygame.K_m in keyboard:
				command.append("SHOOT")
			# debug
			if pygame.K_b in keyboard:
				command.append("DEBUG")
			# paused
			if pygame.K_t in keyboard:
				command.append("PAUSED")
		elif self.side == "2P" or self.side == "4P":
			if pygame.K_d in keyboard:
				command.append("TURN_RIGHT")
			elif pygame.K_a in keyboard:
				command.append("TURN_LEFT")
			elif pygame.K_w in keyboard:
				command.append("FORWARD")
			elif pygame.K_s in keyboard:
				command.append("BACKWARD")
			
			if pygame.K_q in keyboard:
				command.append("AIM_LEFT")
			elif pygame.K_e in keyboard:
				command.append("AIM_RIGHT")
			
			if pygame.K_f in keyboard:
				command.append("SHOOT")
		
		if not command:
			command.append("NONE")

		command.append("AIM_LEFT")

		return command
	
	def reset(self):
		"""
		Reset the status
		"""
		print(f"reset Game {self.side}")
