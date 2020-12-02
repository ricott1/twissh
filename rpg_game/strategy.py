import random
import numpy as np
class Strategy(object):
    def __init__(self):
        self.name = ''
        self.alignment = 'legal' #attacks enemy, 'racist'attacks other races, 'neutral' doesnt attack, crazy attacks all, ally helps player
        self.target = 'weak' #attacks the weakest, 'strong', the strongest, 'cinic' the dying one
        self.priority = {}
    def pick_target(self, char, targets):#targets are all characters in a room, player+villains
        targets = [e for e in targets if (not e.is_dead and char != e and e.location == char.location)]
        if self.alignment == 'legal':
            targets = [e for e in targets if (e.__class__.__name__ != char.__class__.__name__ and e.strategy.alignment not in ('ally', 'passive'))]
        if self.alignment == 'racist':
            targets = [e for e in targets if (e.race != char.race)]
        if self.alignment == 'ally':
            targets = [e for e in targets if (e.__class__.__name__ != 'Player') and e.strategy.alignment not in ('ally', 'passive')]
        if self.alignment == 'chaotic':
            pass
        if self.alignment == 'passive':
            targets = []
        
        if targets:
            if self.target == 'strong':
                targets = sorted([t for t in targets], key = lambda t: t.level, reverse = True)        
            elif self.target == 'weak':
                targets = sorted([t for t in targets], key = lambda t: t.level)    
            elif self.target == 'cinic':
                targets = sorted([t for t in targets], key = lambda t: t.STA)        
            return targets
        else:
            return False
        
    def pick_ability(self, abilities):
        totp = sum([self.priority[k] for k in abilities])
        kind = np.random.choice([k for k in abilities], p = [self.priority[k]/totp for k in abilities])
        return kind
        
class Balanced(Strategy):
    def __init__(self):
        self.name = 'Balanced'
        self.description = 'A balanced strategy'
        self.alignment = 'legal' #attacks enemy, 'chaotic'attacks all, 'passive' doesnt attack
        self.target = 'weak' #attacks the weakest, 'strong', the strongest, 'cinic' the dying one
        self.priority = {'offense' : 0.45, 'defense' : 0.15, 'support' : 0.2, 'race special': 0.1, 'job special': 0.1}
        
class Aggressive(Strategy):
    def __init__(self):
        self.name = 'Aggressive'
        self.description = 'An aggressive strategy'
        self.alignment = 'legal' #attacks enemy, 'chaotic'attacks all, 'passive' doesnt attack
        self.target = 'cinic' #attacks the weakest, 'strong', the strongest, 'cinic' the dying one
        self.priority = {'offense' : 0.55, 'defense' : 0.1, 'support' : 0.15, 'race special': 0.1, 'job special': 0.1}    
        
class Student(Strategy):
    def __init__(self):
        self.name = 'Student'
        self.description = 'The student strategy'
        self.alignment = 'legal' #attacks enemy, 'chaotic'attacks all, 'passive' doesnt attack
        self.target = 'weak' #attacks the weakest, 'strong', the strongest, 'cinic' the dying one
        self.priority = {'offense' : 0.4, 'defense' : 0.25, 'support' : 0.25, 'race special': 0.05, 'job special': 0.05}
        
class Wanderer(Strategy):
    def __init__(self):
        self.name = 'Wanderer'
        self.description = 'The wanderer strategy'
        self.alignment = 'legal' #attacks enemy, 'chaotic'attacks all, 'passive' doesnt attack
        self.target = 'strong' #attacks the weakest, 'strong', the strongest, 'cinic' the dying one
        self.priority = {'offense' : 0.5, 'defense' : 0.05, 'support' : 0.15, 'race special': 0.1, 'job special': 0.2}    

class Protector(Strategy):
    def __init__(self):
        self.name = 'Protector'
        self.description = 'The Protector strategy'
        self.alignment = 'legal' #attacks enemy, 'chaotic'attacks all, 'passive' doesnt attack
        self.target = 'cinic' #attacks the weakest, 'strong', the strongest, 'cinic' the dying one
        self.priority = {'offense' : 0.4, 'defense' : 0.15, 'support' : 0.05, 'race special': 0.3, 'job special': 0.1}   
       
class Barbarian(Strategy):
    def __init__(self):
        self.name = 'Barbarian'
        self.description = 'The Barbarian strategy'
        self.alignment = 'legal' #attacks enemy, 'chaotic'attacks all, 'passive' doesnt attack
        self.target = 'strong' #attacks the weakest, 'strong', the strongest, 'cinic' the dying one
        self.priority = {'offense' : 0.55, 'defense' : 0.0, 'support' : 0.1, 'race special': 0.15, 'job special': 0.2}#i should fix all the possible kinds of abilitites and put them here      




def get_strategies():
    return {"Balanced" : Balanced(), "Aggressive" : Aggressive()}
