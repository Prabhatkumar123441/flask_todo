import logging
from logging.handlers import RotatingFileHandler
from servers.flask.log.logtype import LogLevel

# Set up a rotating file handler



class Log(object):
    __instance = None

    @staticmethod
    def getinstance():
        if not Log.__instance:
            Log().init_logger()
        return Log.__instance

    def init_logger(self):
        if Log.__instance == None:
            self.logger = logging.getLogger(__name__)
            LOG_FILENAME = 'app.log'
            file_handler = RotatingFileHandler(LOG_FILENAME, maxBytes=52428800, backupCount=3)
                    

            # file_handler.setLevel(logging.DEBUG)


            # Create a custom log format
            formatter = logging.Formatter('%(asctime)s : %(thread)d : %(levelname)s : %(lineno)d : %(message)s')
            file_handler.setFormatter(formatter)
            self.logger.setLevel(logging.DEBUG)
            self.logger.addHandler(file_handler)
            Log.__instance = self
            # self.write_log(LogLevel.DEBUG, "this is starting point of flask app","run" )

    
    def write_log(self, logtype, log, function):
        try:
            if logtype == LogLevel.DEBUG:
                self.logger.debug(f"{log}, {function}")
            elif logtype == LogLevel.INFO:
                self.logger.info(f"{log}, {function}")
            elif logtype == LogLevel.ERROR:
                self.logger.error(f"{log}, {function}", exc_info=True)
        except Exception as e:
            self.logger.write_log(("Exception occurred %s" % str(e)), LogLevel.ERROR, "write_log")
        
