from config import Config

if not Config().debug:
    from gevent import monkey #  by using this module we can change the behaviour of standard python libraries synchronous to asynchronous
    monkey.patch_all()


from servers.flask.flaskserver import FlaskServer

if __name__ ==  '__main__':
    FlaskServer().run()