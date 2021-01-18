from rpg_game.constants import *
from rpg_game.utils import *
import character


class Strategy(object):
	def __init__(self, _entity):
		self.entity = _entity
		self.attack = 1
		self.defense = 0.5
		self.support = 0
		self.target_type = None

class MonsterStrategy(Strategy):
	def __init__(self, _entity, _target_type):
		super().__init__(_entity)
		self.vision = 8
		self.sprint_range = 5
		self.target_type = _target_type

	@property
	def target(self):
		closest = sorted([ent for ent in self.entity.location.characters if ent is not self.entity and isinstance(ent, self.target_type) and distance(self.entity.position, ent.position) < self.vision], key=lambda ent: distance(self.entity.position, ent.position))
		if closest:
			return closest[0]
		return None

	@property
	def available_actions(self):
		return {k:act for k, act in self.entity.actions.items() if act.requisites(self.entity)}

	def action(self):
		if not self.target:
			return
		actions = self.available_actions
		if "attack" in actions:
			target = actions["attack"].target(self.entity)
			if isinstance(target, self.target_type):
				return "attack"
		xt, yt, zt = self.target.position
		x, y, z = self.entity.position
		dist = distance(self.entity.position, self.target.position)
		if dist == 1:
			if xt < x and "move_up" in actions:
				return "move_up"
			if xt > x and "move_down" in actions:
				return "move_down"
			if yt < y and "move_left" in actions:
				return "move_left"
			if yt > y and "move_right" in actions:
				return "move_right"
		sprint = dist > self.sprint_range
		if (xt - x)**2 >= (yt - y)**2 > 0 and xt < x and "dash_up" in actions and sprint:
			return "dash_up"
		if (xt - x)**2 >= (yt - y)**2 > 0 and xt < x and "move_up" in actions:
			return "move_up"
		if (xt - x)**2 >= (yt - y)**2 > 0 and xt >= x and "dash_down" in actions and sprint:
			return "dash_down"
		if (xt - x)**2 >= (yt - y)**2 > 0 and xt >= x and "move_down" in actions:
			return "move_down"
		if 0<(xt - x)**2 < (yt - y)**2 and yt < y and "dash_left" in actions and sprint:
			return "dash_left"
		if 0<(xt - x)**2 < (yt - y)**2 and yt < y and "move_left" in actions:
			return "move_left"
		if 0<(xt - x)**2 < (yt - y)**2 and yt >= y and "dash_right" in actions and sprint:
			return "dash_right"
		if 0<(xt - x)**2 < (yt - y)**2 and yt >= y and "move_right" in actions:
			return "move_right"
		return None
	
