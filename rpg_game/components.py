from zope.interface import Interface, Attribute, implementer

class IBody(Interface):
	"""implements rigid body properties"""
	layer = Attribute('The layer')
	position = Attribute('The position tuple')
	location = Attribute('Location')
	weight = Attribute('Weight')
	direction = Attribute('Direction')

    def destroy():
        """Destroy body"""

    def move(direction):
        """Move the body"""

    def change_location(location):
    	"""Change the location"""


implementer(IBody)
class WalkingBody(Adapter):

    layer = 1
	position = (0, 0)
	location = None
	weight = 0
	direction = "up"

	def destroy(self):
        """Destroy body"""
        x, y = self.position
        self.location.clear(self.position, self.layer)

       """Move the body"""
        self.direction = direction
        x, y = self.position 
        new_x = x + int(self.direction=="right") - int(self.direction=="left")
        new_y = y + int(self.direction=="down") - int(self.direction=="up")
        if self.location.is_empty((new_x, new_y), self.layer):
            self.location.clear(self.position, self.layer)
            self.position = (new_x, new_y)
            self.location.register(self)

    def change_location(self, location):
    	self.location.clear(self.position, self.layer)
    	self.location = location

implementer(IBody)
class FixedBody(Adapter):

    layer = 1
	position = (0, 0)
	location = None
	weight = 0
	direction = None

	def destroy(self):
        """Destroy body"""
        self.location.clear(self.position, self.layer)

    def move(self, direction):
        """Cannot move the body"""
        pass

    def change_location(self, location):
    	"""Cannot change location"""
    	pass

implementer(IBody)
class PickableBody(Adapter):

    layer = 0
	position = (0, 0)
	location = None
	weight = 0
	direction = None

	def destroy(self):
        """Destroy body"""
        self.location.clear(self.position, self.layer)

    def move(self, direction):
        """Cannot move the body"""
        pass

    def change_location(self, location):
    	self.location.clear(self.position, self.layer)
    	self.location = location


implementer(IBody)
class FlyingBody(Adapter):

    layer = 2
	position = (0, 0)
	location = None
	weight = 0
	direction = "up"

	def destroy(self):
        """Destroy body"""
        self.location.clear(self.position, self.layer)

    def move(self, direction):
        """Move the body"""
        self.direction = direction
        x, y = self.position 
        new_x = x + int(self.direction=="right") - int(self.direction=="left")
        new_y = y + int(self.direction=="down") - int(self.direction=="up")
        if self.location.is_empty((new_x, new_y), self.layer):
            self.location.clear(self.position, self.layer)
            self.position = (new_x, new_y)
            self.location.register(self)

    def change_location(self, location):
    	self.location.clear(self.position, self.layer)
    	self.location = location
    	self.location.register(self)


