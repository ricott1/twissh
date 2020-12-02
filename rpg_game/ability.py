import random, copy

class Ability(object):
    def __init__(self):
        self.description = []
        
    def use(self, user, target):
        if self.is_legal(user):
            self.on_start(user, target)
            
    def on_start(self, user, target):
        user.HB_damage += float(0.2*user.HB*self.MPcost/user.max_MP)
        user.recoil = getattr(user, self.recoil)
        user.MP_damage += self.MPcost
        user.STA -= self.STAcost
        user.action_time = user.ACTION_TIME_DEFAULT
    def on_update(self,*args):
        pass
           
    def on_end(self,*args):
        pass
    def sentence_on_use(self,*args):
        return ""
        
    def is_legal(self, user):
        if (user.is_dead or user.MP < self.MPcost or user.STA < self.STAcost):
            return False
        elif (user.is_muted and self.MPcost):
            return False
        elif (user.HB_damage > 10 * user.HB and self.MPcost):
            return False
        else:
            return True        

class Attack(Ability):
    def __init__(self):
        self.name = "Attack"
        self.has_target = 'single'
        self.MPcost = 0
        self.STAcost = 2
        self.is_active = 0
        self.is_passive = 0
        self.recoil = "MED_RECOIL"
        self.description = ["Basic attack: STA {}".format(self.STAcost)]
        self.type = "offense"
        self.level = 1
        
    def on_start(self, user, target):
        super(Attack,self).on_start(user, target)
        if "weapon" in user.equipment:
            w = user.equipment["weapon"]
            w_dmg = sum([random.randint(1, w.damage) for _ in range(w.dices)])
        else:
            w_dmg = random.randint(1,4)
        if user.on_rythm == 2:
            power = 3 * w_dmg + user.STRmod + user.level
            user.recoil /= 3.
        elif user.on_rythm == 1:
            power = 2 * w_dmg + user.STRmod + user.level
            user.recoil /= 2.
        else:
            power = w_dmg + user.STRmod 
            
        power = max(0, int(round(power - target.RESmod)))
        
        if user.roll() + user.DEXmod + int(user.level/4) > target.AC:
            target.HP_damage += max(0, power)
            target.recoil += 5
            
            user.print_action = self.sentence_on_use(target, str(power) + " dmg")   
        else:
            user.print_action = self.sentence_on_use(target,"miss!")    
        if user not in target.acquiredTargets: 
            target.acquiredTargets.append(user)
        
    def sentence_on_use(self,target, dmg):
        return "Attacks {}: {}".format(target.name, dmg)

class Breath(Ability):
    def __init__(self):
        self.name = "Breath"
        self.has_target = 'all'
        self.MPcost = 10
        self.STAcost = 10
        self.is_active = 0
        self.is_passive = 0
        self.recoil = "MAX_RECOIL"
        self.description = ["Devastating fire breath: STA {} MP {}".format(self.STAcost, self.MPcost)]
        self.type = "special"
        self.level = 3
     
    def on_start(self, user, targets):
        super(Breath,self).on_start(user, None)
        w_dmg = sum([random.randint(1, 6) for _ in range(user.level)])
        
        if user.on_rythm == 2:
            power = 3 * w_dmg + user.MAGmod
            recoil = 50
            user.recoil /= 1.25
        elif user.on_rythm == 1:
            power = 2 * w_dmg + user.MAGmod
            recoil = 25
        else:
            power = w_dmg + user.MAGmod 
            recoil = 10
        
        user.print_action = self.sentence_on_use()   
        for target in targets:
            power = max(0, int(round(power - target.RESmod)))
            if user.roll() + user.DEXmod + int(user.level) > target.AC:
                target.HP_damage += max(0, power)
                target.HB_damage += max(0, power)
                target.recoil += recoil
                user.print_action += "{}:{}  ".format(target.name, str(power) + " dmg")   
            else:
                user.print_action +=  "{}:{}  ".format(target.name, "miss")      
            if user not in target.acquiredTargets: 
                target.acquiredTargets.append(user)
        
    def sentence_on_use(self):
        return "Breaths: "



class Push(Ability):
    def __init__(self):
        self.name = "Push"
        self.has_target = 'single'
        self.MPcost = 0
        self.STAcost = 7
        self.is_active = 0
        self.is_passive = 0
        self.recoil = "SHORT_RECOIL"
        self.description = ["Basic push: STA {}".format(self.STAcost)]
        self.type = "support"
        self.level = 1
        
    def on_start(self, user, target):
        super(Push,self).on_start(user, target)
        if user.on_rythm == 2:
            power = 3 * random.randint(1, 8) + user.STRmod + user.level
        elif user.on_rythm == 1:
            power = 2 * random.randint(1, 8) + user.STRmod + user.level
        else:
            power = random.randint(1, 8) + user.STRmod 
                
        if user.roll() + user.DEXmod + int(user.level/4) > 10:
            target.recoil += power
            
            user.print_action = self.sentence_on_use(target, str(power) + " recoil")   
        else:
            user.print_action = self.sentence_on_use(target,"miss!")    
        if user not in target.acquiredTargets: 
            target.acquiredTargets.append(user)
        
    def sentence_on_use(self,target, dmg):
        return "Pushes {}: {}".format(target.name, dmg)
        
        
class Dash(Ability):
    def __init__(self):
        self.name = "Dash"
        self.has_target = False
        self.MPcost = 3
        self.STAcost = 0
        self.is_active = 0
        self.is_passive = 0
        self.length = 10.
        self.recoil = "SHORT_RECOIL"
        self.power = 2
        self.mod_power = 0
        self.description = ["Basic dash: MP {}".format(self.MPcost)]
        self.type = "support"
        self.level = 2
    def is_legal(self, user):
    
        if (user.is_dead or user.MP < self.MPcost or user.STA < self.STAcost):
            return False
        if (user.is_muted and self.MPcost):
            return False
        elif self.is_active > 0:
            return False
        else:
            return True     
    def on_start(self, user, target):
        super(Dash,self).on_start(user, target)
        if self.is_active ==0:
            self.is_active = self.length * (1. + user.on_rythm/2.)
            self.mod_power = max(self.power, self.power + user.MAGmod)
            user.print_action = self.sentence_on_use(int(self.is_active), self.mod_power)   
            user.bonus["SPD"] += self.mod_power
    def on_update(self,DELTATIME, user):
        if self.is_active:
            self.is_active -= DELTATIME
            if self.is_active <= 0:
                self.on_end(user)
    def on_end(self,user):
        self.is_active = 0
        #user.action_time = 0
        #user.print_action = ""
        user.bonus["SPD"] -= self.mod_power
    def sentence_on_use(self, seconds, power):
        return "Dashes {}: {:+d} SPD".format(seconds, power)
        
class Frenzy(Ability):
    def __init__(self):
        self.name = "Frenzy"
        self.has_target = False
        self.MPcost = 3
        self.STAcost = 0
        self.is_active = 0
        self.is_passive = 0
        self.length = 30.
        self.recoil = "MED_RECOIL"
        self.power = 2
        self.mod_power = 0
        self.strategy = None
        self.description = ["Basic frenzy".format(self.MPcost)]
        self.type = "support"
        self.level = 2
        
    def is_legal(self, user):
    
        if (user.is_dead or user.MP < self.MPcost or user.STA < self.STAcost):
            return False
        if (user.is_muted and self.MPcost):
            return False
        elif not [c for c in user.location.characters if (not c.is_dead and c.__class__.__name__ != user.__class__.__name__)]:#if hes the last man standing
            return False
        elif self.is_active > 0:
            return False
        else:
            return True      
    def on_start(self, user, target):
        super(Frenzy,self).on_start(user, target)
        if self.is_active ==0:
            self.is_active = self.length * (1. + user.on_rythm/2.)
            self.mod_power = self.power + int(user.level/3)
            self.strategy = user.strategy
            user.strategy = copy.copy(self.strategy)
            user.strategy.alignment = ''
            user.fix_strategy = True
            user.print_action = self.sentence_on_use(int(self.is_active), self.mod_power)   
            user.bonus["STR"] += self.mod_power
            user.bonus["SPD"] += self.mod_power
            user.bonus["HB"] += self.mod_power * 10
    def on_update(self,DELTATIME, user):
        if self.is_active:
            self.is_active -= DELTATIME
            if self.is_active <= 0:
                self.on_end(user)
    def on_end(self,user):
        self.is_active = 0
        user.bonus["STR"] -= self.mod_power
        user.bonus["SPD"] -= self.mod_power
        user.strategy = self.strategy
        user.fix_strategy = False
    def sentence_on_use(self, seconds, power):
        return "Frenzy {}: {:+d} STR, {:+d} SPD, {:+d} HB ".format(seconds, power, power, power*10)      
        
class Poison(Ability):
    def __init__(self):
        self.name = "Poison"
        self.has_target = 'single'
        self.MPcost = 0
        self.STAcost = 3
        self.is_active = 0
        self.is_passive = 0
        self.recoil = "MED_RECOIL"
        self.description = ["Poison attack: STA {}".format(self.STAcost)]
        self.type = "offense"
        self.poisoned = []
        self.length = 2.
        self.level = 2
        
    def on_start(self, user, target):
        super(Poison,self).on_start(user, target)
        if "weapon" in user.equipment:
            w = user.equipment["weapon"]
            w_dmg = sum([random.randint(1, w.damage) for _ in range(w.dices)])
        else:
            w_dmg = random.randint(1,4)
        if user.on_rythm == 2:
            power = 3 * w_dmg + user.STRmod + user.level
            user.recoil /= 3.
            self.poisoned.append([target, self.length * 3])
            target.is_shocked += self.length 
        elif user.on_rythm == 1:
            power = 2 * w_dmg + user.STRmod + user.level
            user.recoil /= 2.
            self.poisoned.append([target, self.length * 2])
        else:
            power = w_dmg + user.STRmod 
            self.poisoned.append([target, self.length])
        power = max(0, int(round(power - target.RESmod)))
        
        if user.roll() + user.DEXmod > target.AC:
            target.HP_damage += max(0, power)
            target.recoil += 5
            
            user.print_action = self.sentence_on_use(target, str(power) + " dmg")   
        else:
            user.print_action = self.sentence_on_use(target,"miss!")    
        if user not in target.acquiredTargets: 
            target.acquiredTargets.append(user)
    def on_update(self,DELTATIME, user):
        for p in self.poisoned:
            p[0].HP_damage += DELTATIME
            p[1] -= DELTATIME
            if p[1] <= 0:
                self.poisoned.remove(p)
    def sentence_on_use(self,target, dmg):
        return "Attacks {}: {}".format(target.name, dmg)
  
class Shock(Ability):
    def __init__(self):
        self.name = "Shock"
        self.has_target = 'single'
        self.MPcost = 4
        self.STAcost = 0
        self.is_active = 0
        self.is_passive = 0
        self.recoil = "MED_RECOIL"
        self.description = ["Shock: MP {}".format(self.MPcost)]
        self.type = "support"
        self.length = 2.
        self.level = 2
        
    def on_start(self, user, target):
        super(Shock,self).on_start(user, target)
        
        if user.on_rythm == 2:
            power = max(0, (self.length + user.MAGmod) * 3)
        elif user.on_rythm == 1:
            power = max(0, (self.length + user.MAGmod) * 2)
        else:
            power = max(0, (self.length + user.MAGmod))
        
        if user.roll() + user.MAGmod > 10:
            target.is_shocked += power
            
            user.print_action = self.sentence_on_use(target, power)   
        else:
            user.print_action = self.sentence_on_use(target,"miss!")    
        if user not in target.acquiredTargets: 
            target.acquiredTargets.append(user)
   
    def sentence_on_use(self,target, dmg):
        return "Shocks {}: {}".format(target.name, dmg)     
        
class Confuse(Ability):
    def __init__(self):
        self.name = "Confuse"
        self.has_target = "single"
        self.MPcost = 5
        self.STAcost = 0
        self.is_active = 0
        self.is_passive = 0
        self.recoil = "LONG_RECOIL"
        self.description = ["Confuse: MP {}".format(self.MPcost)]
        self.type = "special"
        self.length = 2.
        self.level = 3
        self.confused = []
        
        
    def on_start(self, user, target):
        super(Confuse,self).on_start(user, target)
        
        if user.on_rythm == 2:
            power = max(0, (self.length + user.MAGmod) * 3)
        elif user.on_rythm == 1:
            power = max(0, (self.length + user.MAGmod) * 2)
        else:
            power = max(0, (self.length + user.MAGmod))
        
        if user.roll() + user.MAGmod > 10:
            self.confused.append([target, self.length * power, str(target.strategy.alignment)])
            target.strategy.alignment = "chaotic"
            target.fix_strategy = True
            
            user.print_action = self.sentence_on_use(target, power)   
        else:
            user.print_action = self.sentence_on_use(target,"miss!")    
        if user not in target.acquiredTargets: 
            target.acquiredTargets.append(user)
            
    def on_update(self,DELTATIME, user):
        for p in self.confused:
            p[1] -= DELTATIME
            if p[1] <= 0:
                p[0].strategy.alignment = p[2]
                p[0].fix_strategy = True
                self.confused.remove(p)
                
    def sentence_on_use(self,target, dmg):
        return "Confuses {}: {}".format(target.name, dmg)    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
  
class Atmen(Ability):
    def __init__(self,character):
        user = character
        self.name = "Atmen"
        self.has_target = False
        self.MPcost = 0
        self.STAcost = 0
        self.is_active = 0
        self.is_passive = 0
        self.description = ["Recatch breath right away"]
    @property
    def MPcost(self):
        self._MPcost = user._MP
        return self._MPcost
    @MPcost.setter
    def MPcost(self, value):
        self._MPcost = value
    
    def on_start(self,target):
        user.isCatchingBreath = (user.MP-user._MP*1.0)/user.MP*user.timeToCatchBreath()
        super(Atmen,self).on_start(target)
        
    def sentence_on_use(self,target):
        return ""    
#this does not work now


#still to write
class Fuse(Ability):
    def __init__(self,character):
        self.name = "Fuse"
        self.has_target = True
        self.MPcost = 0
        self.is_active = 0
        self.is_passive = 0
        user = character
        self.length = 0
    def on_start(self, target):
        super(Meditate,self).on_start(target)
        self.is_active = 0.0001
        user.is_muted = True
        self.length = 5.0
        user.action_time = self.length
    def on_update(self,DELTATIME):
        super(Meditate,self).on_update(DELTATIME)
        if self.is_active:
            self.is_active += DELTATIME
            user.reduceHB(DELTATIME*self.is_active)
        if self.is_active >= self.length:
            self.on_end()
    def on_end(self,*args):
        self.is_active = 0
        user.is_muted = False
    def sentence_on_use(self,*args):
        return "%s is meditating"%user.name




