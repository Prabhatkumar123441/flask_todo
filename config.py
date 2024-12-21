import os



env = os.getenv("ENV", "dev")



class Config(object):
    # def __init__(self):
    httpport = 5000
    if(env == "dev"):
        database = 'DataBase.db' 
        debug = True
    elif(env == "stg"):
        debug = False
    pass
