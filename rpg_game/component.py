from rpg_game.constants import *

class Counter(object):
    def __init__(self, name=None, entity=None, on_end=lambda:None)
        self.name = name
        self.entity = entity
        self._value = value
        self.on_end = on_end

    def on_set(self, *args):
        pass

    def on_update(self, *args):
        if self.value > 0:
            self.value -= COUNTER_MULTI * _deltatime
            if self.value == 0:
                self.on_end()

    @property
    def value(self):
        return self._value  

    @value.setter
    def value(self, val):
        self._value = max(0, min(COUNTER_MAX, val))
        

class Component(object):
    """docstring for Component"""
    def __init__(self, name=None, entity=None):
        self.name = name
        self.entity = entity
        self.actions = {}
        self.counters = {}

    def on_update(self, *args):
        for key in self.counters:
            self.counters[key].on_update()

    def on_set(self):
        for key, act in self.actions.items():
            setattr(self.entity, key, lambda action=act, **kwargs: action.use(self.entity, **kwargs))

    @classmethod
    def requisites(cls, *args):
        return True


class Entity(object):
    def __init__(self, _name="", _id=None, _location=None, _position=(), _extra_position = []):
        self.name = _name
        self.id = _id if _id else new_id()
        self.components = {}

        if _location and not _position:
            _position = _location.free_position(_layer, _extra_position)
        self.position = _position
        self.extra_position = _extra_position
        self.location = _location

    def set_component(self, _component: Component):
        if comp.requisites(self):
            comp = component(self)
            comp.on_set()
            self.components[component.name] = comp
            setattr(self, component.name, comp)
        else:
            print("Invalid component", comp)

    def has_component(self, _name: str):
        return _name in self.components

    def on_update(self):
        for key, comp in self.components.items():
            comp.on_update()

    def destroy(self):
        """Destroy body"""
        if self.location:
            self.location.unregister(self)

    @property
    def positions(self):
        x, y, z = self.position
        #don't transform coordinates
        if self.direction == "down":
            _extra_positions = [(x, y, z) for x, y, z in self.extra_position]
        elif self.direction == "up":
            _extra_positions = [(-x, -y, z) for x, y, z in self.extra_position]
        elif self.direction == "right":
            _extra_positions = [(y, -x, z) for x, y, z in self.extra_position]
        elif self.direction == "left":
            _extra_positions = [(-y, x, z) for x, y, z in self.extra_position]
        return [(x+xp, y+yp, z+zp) for xp, yp, zp in [(0,0,0)] + _extra_positions]

    @location.setter
    def location(self, _location):
        if self.location:
            self.location.unregister(self)
        self.location = _location
        self.location.register(self)


class HitBox(Component):
    def __init__(self, entity, _hp = 10):
        import characteristic
        super().__init__(name="hit_box", entity=entity)
        self.HP = Characteristic("hit points", "HP", _hp, _min = 0, _max=9999)  
        self.counters = {"dead":Counter(name="dead", entity=entity, on_end=lambda : self.entity.destroy)}    

    def on_set(self):
        setattr(self.entity, "dmg_reduction", property(self.HP.dmg_reduction))
        setattr(self.entity, "hp", property(lambda: self.HP.value))
        setattr(self.entity, "is_dead", property(lambda: True if self.HP.value <=0 else False))
        setattr(self.entity, "restore", lambda: self.HP._dmg = 0)
        setattr(self.entity, "hit", lambda dmg: self.hit(dmg))

    def hit(self, dmg):
        self.HP._dmg += max(1, dmg - self.dmg_reduction())
        if self.entity.is_dead:
            self.set_death()

    def set_death(self):
        self.entity.redraw = True
        self.entity.print_action = f"{self.entity.name} is dead"
        self.counters["dead"] = DEATH_INTERVAL

    def dmg_reduction(self):
        tot = 0
        for part, eqp in self.entity.equipment.items():
            if eqp and hasattr(eqp, "dmg_reduction"):
                tot += eqp.dmg_reduction
        return tot
       
class MovingBody(Component):
 	"""docstring for ClassName"""
 	def __init__(self, entity):
 		super().__init__(name="body", entity=entity)
 		self.direction = "down"
 		self.actions = {"move_up": action.MoveUp, "move_down": action.MoveDown, "move_left": action.MoveLeft, "move_right": action.MoveRight}

        self.counters = {key:Counter(name=key, entity=entity) for key in self.actions}

class GameClass(Component):
    def __init__(self, entity):
        import action
        super().__init__(name="class", entity=entity)
        self.actions = {"attack" : action.Attack}

        self.counters = {key:Counter(name=key, entity=entity) for key in self.actions}

class Inventory(Component):
    def __init__(self, entity):
        import action
        super().__init__(name="inventory", entity=entity)
        self.actions = {"pick_up": action.PickUp, "drop": action.Drop}

        self.counters = {key:Counter(name=key, entity=entity) for key in self.actions}

    def add_inventory(self, obj):
        free = self.inventory.free_position(_layer=0)
        if not free:
            print("Inventory full")
            return
        # obj.location.unregister(obj)
        obj.position = free
        obj.location = self.inventory
        
    def remove_inventory(self, obj):
        if obj.is_equipped:
            for _type in obj.type:
                if self.equipment[_type] == obj:
                    self.unequip(_type)
                    break
        # obj.location.unregister(obj)
        x, y, z = self.position
        obj.position = (x, y, 0)
        obj.location = self.location
            
    def equip(self, obj, _type):
        if _type not in obj.type:
            return
        if not obj.is_equipment:
            return
        self.unequip(_type)
        self.equipment[_type] = obj
        obj.on_equip()
        
    def unequip(self, _type):
        if self.equipment[_type]:
            self.equipment[_type].on_unequip()
        self.equipment[_type] = None

class Graphic(Component):
    """docstring for Graphic"""
    def __init__(self, entity, _marker="."):
        super().__init__(name="graphic", entity=entity)
        self._marker = _marker
    
    def on_set(self):
        setattr(self.entity, "marker", property(self.marker))

    def marker(self):
        return [self._marker for _ in self.entity.positions]

class DirectionalGraphic(Component):
    """docstring for Graphic"""
    def __init__(self, entity, _marker={"up":"▲", "down":"▼", "left":"◀", "right":"▶"}):
        super().__init__(entity=entity)
    
    def on_set(self):
        setattr(self.entity, "marker", property(self.marker))

    def marker(self):
        return [self._marker[self.entity.direction] for _ in self.entity.positions]

    @classmethod
    def requisites(self, entity):
        return hasattr(entity, "direction")
        

