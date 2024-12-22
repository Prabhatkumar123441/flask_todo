from config import Config
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, abort
import sqlite3
from servers.flask.responsebuilder import ResponseBuilder
from config  import Config
from datetime import timedelta
import os 
from functools import wraps
from gevent.pywsgi import WSGIServer
from servers.flask.route.registration_route import available_emails
from servers.flask.route.user_route import todos

from servers.flask.route.user_route import user_r
from servers.flask.route.login_route import login_r
from servers.flask.route.registration_route import registration_r


from servers.flask.log.logger import Log
from servers.flask.log.logtype import LogLevel



class FlaskServer(object):
    app = Flask(__name__, template_folder = os.path.abspath('./templates'), static_folder = os.path.abspath('./static'))
    app.debug = True
    app.secret_key = 'your_secret_key'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)

    app.register_blueprint(user_r)
    app.register_blueprint(login_r)
    app.register_blueprint(registration_r)
    

    def __init__(self):
        pass


    def create_table():
        conn = sqlite3.connect(Config().database)
        cursor = conn.cursor()
        
        cursor.execute("CREATE TABLE IF NOT EXISTS users (email TEXT, username TEXT, password TEXT)")
        conn.commit()
        conn.close()
    

    def printheaders(f):
        @wraps(f)
        def printallheaders(*args, **kwargs):
            headers = dict(request.headers)
            client_ip = request.remote_addr
            print("URL: %s" % request.base_url)
            print("Request IP: %s" % client_ip)
            print("Headers:")
            print(headers)
            return f(*args, **kwargs)
        return printallheaders

     
    def session_required(f):
        @wraps(f) 
        def decorator_function(*args, **kwargs):
            if 'username' not in session : 
                return render_template('home.html')
            return f(*args, **kwargs)
        return decorator_function

    @app.route("/hello", methods = ['GET'])
    @printheaders
    def hello():
        return ResponseBuilder.jsonresponsebuilder("Flask server is running", 200)
    

    @app.route('/update', methods=['POST'])
    @printheaders
    @session_required
    def update():
        data = request.get_json()
        todo = data.get('todo')
        description = data.get('description')

        
    @app.route('/')
    @printheaders
    @session_required
    def home():
        
        if "username" in session:
            if session['username']:
                username = session['username']# Replace with the actual username

                # Connect to the SQLite Config().database
                conn = sqlite3.connect(Config().database)
                cursor = conn.cursor()
                

                # Check if 'todos' table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='todos'")
                table_exists = cursor.fetchone()

                # If 'todos' table doesn't exist, create it
                if not table_exists:
                    cursor.execute("CREATE TABLE IF NOT EXISTS users (email TEXT, username TEXT, password TEXT)")
                    cursor.execute("CREATE TABLE IF NOT EXISTS todos (todo TEXT UNIQUE, description TEXT, username TEXT)")
                    # cursor.execute("CREATE TABLE todos (id INTEGER PRIMARY KEY AUTOINCREMENT, todo TEXT, description TEXT, username TEXT)")

                # # Insert the data into 'todos' table
                # cursor.execute("SELECT todo, description FROM todos WHERE username = ? and todo = ?", (username,todo))
                # todos = cursor.fetchall()
                # if len(todos) == 0:
                
                #     cursor.execute("INSERT INTO todos (todo, description, username) VALUES (?, ?, ?)", (todo, description, username))
                #     conn.commit()
                cursor.execute("SELECT todo, description FROM todos WHERE username = ?", (username,))
                todos = cursor.fetchall()

                # Close the Config().database connection
                conn.close()
                return  render_template('user_space.html',todos = todos,username = session['username'])
            else:
                conn = sqlite3.connect(Config().database)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users ")
                users = cursor.fetchall()
                conn.close()

                if users:
                    for user in users:
                        available_emails.add(user[0])

        
            return render_template('home.html')

        else:
            conn = sqlite3.connect(Config().database)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users ")
            users = cursor.fetchall()
            conn.close()

            if users:
                for user in users:
                    available_emails.add(user[0])

        
            return render_template('home.html')


    @app.route('/get_all_todos')
    @printheaders
    @session_required
    def get_all_todos():
        username = session['username']
        conn = sqlite3.connect(Config().database)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='todos'")
        table_exists = cursor.fetchone()

        # If 'todos' table doesn't exist, create it
        # app.logger.debug("Log---",username)
        if not table_exists:
            cursor.execute("CREATE TABLE IF NOT EXISTS todos (todo TEXT UNIQUE, description TEXT, username TEXT)")
        cursor.execute("SELECT todo, description FROM todos WHERE username = ?", (username,))
        todos = cursor.fetchall()
        return  jsonify(todos)


    @app.route('/check_email_availability')
    @printheaders
    def check_email_availability():
        email = request.args.get('email')
        if email in available_emails:
            return jsonify({'available': False})
        else:
            return jsonify({'available': True})


    def run(self):
        Log().init_logger()
        Log().getinstance().write_log(LogLevel.DEBUG, "this is starting point of flask app","run" )
        FlaskServer.create_table()
        port = Config.httpport
        if Config.debug:
            # FlaskServer.app.run(port = port, debug = True)
            FlaskServer.app.run(host = "0.0.0.0", port = port, debug = True)
        else:
            flask_wsgi_server = WSGIServer(("0.0.0.0", port),FlaskServer.app.wsgi_app, spawn=10)
            flask_wsgi_server.serve_forever()