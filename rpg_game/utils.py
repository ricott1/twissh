
def mod(value):
    return (value-10)//2

def log(text):
    with open("log.tiac", "a") as f:
        f.write("{}: {}\n".format(time.time(), text))
   