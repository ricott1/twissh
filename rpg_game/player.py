import uuid

class Player(object):
	"""docstring for Player"""
	def __init__(self, _name, _id):
		super(Player, self).__init__()
		self.name = _name
		self.id = _id


def newPlayer(_name):
	return Player(_name, uuid.uuid())
