import math
from collections import OrderedDict
from multiprocessing import Value

"""env setting"""
BULLET_SPEED = 30
BULLET_TRAVEL_DISTANCE = 300  
BLOCK_LENGTH = 50

DISTANCE_SEP_1 = 120
DISTANCE_SEP_2 = 200
DISTANCE_SEP_3 = 320

DISTANCE_CLOSE = "DISTANCE_CLOSE"
DISTANCE_NEAR = "DISTANCE_NEAR"
DISTANCE_MODERATE = "DISTANCE_MODERATE"
DISTANCE_FAR = "DISTANCE_FAR"
DISTANCE_INVALID = "DISTANCE_INVALID"

MAP_WIDTH = 1000
MAP_WIDTH_BLOCKS = int(MAP_WIDTH / BLOCK_LENGTH)
MAP_HEIGHT = 600
MAP_HEIGHT_BLOCKS = int(MAP_WIDTH / BLOCK_LENGTH)

bullet_id = lambda side: "{}_bullet".format(side)

LEFT= "LEFT",
BOTTOMLEFT= "BOTTOMLEFT",
BOTTOM = "BOTTOM",
BOTTOMRIGHT = "BOTTOMRIGHT",
RIGHT = "RIGHT",
TOPRIGHT = "TOPRIGHT",
TOP = "TOP",
TOPLEFT = "TOPLEFT",
LEFT = "LEFT"

GUN_RANGE_BLOCKS = 6

angle_map = OrderedDict([
	(0,   LEFT),
	(45,  BOTTOMLEFT),
	(90,  BOTTOM),
	(135, BOTTOMRIGHT),
	(180, RIGHT),
	(225, TOPRIGHT),
	(270, TOP),
	(315, TOPLEFT),
])

WALL_UNKNOWN = "WALL_UNKNOWN"
WALL_NO_LIFE = "WALL_NO_LIFE"
WALL_ONE_LIFE = "WALL_ONE_LIFE"
WALL_TWO_LIFE = "WALL_TWO_LIFE"
WALL_THREE_LIFE = "WALL_THREE_LIFE"
WALL_FOUR_LIFE = "WALL_FOUR_LIFE"

wall_lives_map = {
	-1: WALL_UNKNOWN,
	0:  WALL_NO_LIFE,
	1:  WALL_ONE_LIFE,
	2:  WALL_TWO_LIFE,
	3:  WALL_THREE_LIFE,
	4:  WALL_FOUR_LIFE
}

def opposite_side(side: str) -> str:
	if side.find("1P") != -1:
		return side.replace("1P", "2P")
	if side.find("2P") != -1:
		return side.replace("2P", "1P")
	raise ValueError("Failed to generate opposing side of {}".format(side))

def id_exists(id: str, target: list):
	for item in target:
		if item["id"] == id:
			return True
	return False

def get_by_id(id: str, target: list):
	for item in target:
		if item["id"] == id:
			return item
	return None

def get_nearest(target: list):
	current_min_dist_squared = float("inf")
	current_min_item = None
	for item in target:
		dist = item["x"]**2 + item["y"]**2 
		if dist < current_min_dist_squared:
			current_min_dist_squared = dist
			current_min_item = item
	return item

def get_degrees(target_y, base_y, target_x, base_x) -> int:
	if target_y == -1 or target_x == -1:
		return -1
	return 180 - int(math.degrees(math.atan2(target_y - base_y, target_x - base_x)))

def get_distance(target_x, base_x, target_y, base_y) -> str:
	if target_y == -1 or target_x == -1:
		return DISTANCE_INVALID
	dist = math.sqrt((abs(target_x - base_x)**2) + (abs(target_y - base_y)**2))
	if dist <= DISTANCE_SEP_1:
		return DISTANCE_CLOSE
	elif DISTANCE_SEP_1 <= dist and dist <= DISTANCE_SEP_2:
		return DISTANCE_NEAR
	elif DISTANCE_SEP_2 <= dist and dist <= DISTANCE_SEP_3:
		return DISTANCE_MODERATE
	else:
		return DISTANCE_FAR

def make_angle_positive(angle: int):
	while angle < 0:
		angle += 360
	return angle

def get_index_difference(arr: list, item_base, item_cmp, positive_index: bool):
	if item_base == item_cmp:
		return 0
	base_index = arr.index(item_base)
	cmp_index = None
	if positive_index:
		try:
			cmp_index = arr[base_index + 1:].index(item_cmp) + 1
		except ValueError:
			cmp_index = len(arr) - base_index + arr.index(item_cmp)
	else:
		try:
			cmp_index = base_index + len(arr[:base_index+1]) - arr[:base_index+1][::-1].index(item_cmp) - 1
		except ValueError:
			cmp_index = len(arr) - (len(arr) - arr[::-1].index(item_cmp) - 1 - base_index)
	return cmp_index

def get_index_difference_lambda(arr: list, item_base, pred, positive_index: bool):
	if pred(item_base):
		return 0
	match_pred = lambda lst: next(index for index, value in enumerate(lst) if pred(value))
	base_index = arr.index(item_base)
	cmp_index = None
	if positive_index:
		try:
			cmp_index = match_pred(arr[base_index + 1:]) + 1
		except StopIteration:
			cmp_index = len(arr) - base_index + match_pred(arr)
	else:
		try:
			cmp_index = base_index - len(arr[:base_index+1]) + match_pred(reversed(arr[:base_index+1])) + 1
		except StopIteration:
			cmp_index = match_pred(reversed(arr)) + base_index + 1
	return cmp_index