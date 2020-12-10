import uuid, random

RANDOM_NAMES = ("Gorbacioff", "Gundam", "Pesca", "Lukiko","Armando","Mariella","Formaggio","Pancrazio","Tancredi","Swallace","Faminy","Pertis","Pericles","Atheno","Mastella","Ciriaco")


def quick_data():
    WIS, CON, INT, CHA, DEX, STR = [sum([random.randint(1,6) for l in range(3)]) for x in range(6)]
    HP = random.randint(1,8)
    data = {"name" : random.sample(RANDOM_NAMES, 1)[0], "CON" : CON, "INT" : INT, "HP" : HP, "CHA" : CHA, "DEX" : DEX + 6, "STR" : STR + 6, 
    "WIS" : WIS}
    return data

def mod(value):
    return (value-10)//2

def log(text):
    with open("log.tiac", "a") as f:
        f.write("{}: {}\n".format(time.time(), text))
   
def get_time():
    return datetime.datetime.now().strftime("%H:%M:%S")

def new_id():
	return uuid.uuid4()