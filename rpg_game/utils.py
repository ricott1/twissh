import uuid, random, collections

RANDOM_NAMES = ("Gorbacioff", "Gundam", "Pesca", "Lukiko","Armando","Mariella","Formaggio","Pancrazio","Tancredi","Swallace","Faminy","Pertis","Pericles","Atheno","Mastella","Ciriaco","Harri","Pantera")

nested_dict = lambda: collections.defaultdict(nested_dict)

def roll3d6():
	return sum([random.randint(1,6) for _ in range(3)])

def roll1d4():
	return random.randint(1,4)

def roll1d20():
	return random.randint(1,20)

def roll(num, dice):
	tot = 0
	for i in range(num):
		tot += random.randint(1,dice) 
	return tot

def random_stats(_levels={}):
    if not _levels:
        data = {"CON" : roll3d6(), "INT" : roll3d6(), "CHA" : roll3d6(), "DEX" : roll3d6(), "STR" : roll3d6(), "WIS" : roll3d6()}
    else:
        data = {k:random_stat(v) for k, v in _levels.items()}
    data["HP"] = random.randint(1,8)
    print("ROLLED", _levels, data)
    return data

def random_stat(_level = 1):
    if _level == 3:
        rolls = sorted([random.randint(1,6) for _ in range(4)])
        return sum(rolls[1:])
    elif _level == 2:
        return roll3d6()
    elif _level == 1:
        rolls = sorted([random.randint(1,6) for _ in range(4)])
        return sum(rolls[:-1])

def random_name():
	return random.sample(RANDOM_NAMES, 1)[0]

def mod(value):
    #return (value-10)//2
    if (value <= 3): return -3
    elif (value <= 5): return -2
    elif (value <= 8): return -1
    elif (value >= 18): return 3
    elif (value >= 16): return 2
    elif (value >= 13): return 1
    return 0

def distance(a, b):
    return sum([(a[i]-b[i])**2 for i in range(len(a))])**0.5

def log(text):
    with open("log.tiac", "a") as f:
        f.write("{}: {}\n".format(time.time(), text))
   
def get_time():
    return datetime.datetime.now().strftime("%H:%M:%S")

def new_id():
	return uuid.uuid4()