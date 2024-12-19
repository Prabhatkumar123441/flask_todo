import os



env = os.getenv("ENV", "dev")



class Config(object):
    def __init__(self):
        self.httpport = 5000
        if(env == "dev"):
            self.database = 'DataBase.db' 
            self.debug = True
        elif(env == "stg"):
            self.debug = True
            pass
