from config import Config
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, abort
import sqlite3 as sql
import sqlite3
from servers.flask.responsebuilder import ResponseBuilder
from config  import Config
from datetime import timedelta
import os 
from functools import wraps
from gevent.pywsgi import WSGIServer




class FlaskServer(object):
    app = Flask(__name__, template_folder = os.path.abspath('./templates'), 
    static_folder=os.path.abspath('./static'))
    app.debug = True
    app.secret_key = 'your_secret_key'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
    available_emails = set()
    todos = []
    

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


    @app.route("/hello", methods = ['GET'])
    @printheaders
    def hello():
        return ResponseBuilder.jsonresponsebuilder("Flask server is running", 200)
    


    @app.route('/update', methods=['POST'])
    @printheaders
    def update():
        data = request.get_json()
        todo = data.get('todo')
        description = data.get('description')


    @app.route('/delete/<todo>/<des>')
    @printheaders
    def delete_row(todo,des):
        conn = sqlite3.connect(Config().database)
        cursor = conn.cursor()
        
        # Get the todo based on the index
        # cursor.execute("SELECT todo FROM todos LIMIT ?, 1", (index - 1,))
        query = f"DELETE FROM todos WHERE todo = '{todo}' and description = '{des}' and username = '{session['username']}'"
        cursor.execute(query)
        conn.commit()
        # print('number of rows deleted', cursor.rowcount)
        conn.close()
            
        return redirect('/user')


    @app.route("/delete_all_todos",methods = ['DELETE'])
    @printheaders
    def delete_all_todos():
        global todos
        FlaskServer.todos.clear()
        if session['username']:
            username = session['username']
            conn = sqlite3.connect(Config().database)
            cursor = conn.cursor()
            

            # Check if 'todos' table exists
            cursor.execute("DELETE FROM todos WHERE username = ?", (username,))
            conn.commit()
            cursor.execute("SELECT todo, description FROM todos WHERE username = ?", (username,))
            FlaskServer.todos = cursor.fetchall()
            conn.close()
            FlaskServer.todos = []
            return jsonify({"message": "All todos deleted successfully."}), 200
        

    @app.route('/add_todo', methods=['POST'])
    @printheaders
    def add_todo():
        # Get the form data
        todo = request.form['todo']
        description = request.form['description']
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

        # Insert the data into 'todos' table
        cursor.execute("SELECT todo, description FROM todos WHERE username = ? and todo = ?", (username,todo))
        FlaskServer.todos = cursor.fetchall()
        if len(FlaskServer.todos) == 0:
        
            cursor.execute("INSERT INTO todos (todo, description, username) VALUES (?, ?, ?)", (todo, description, username))
            conn.commit()
        cursor.execute("SELECT todo, description FROM todos WHERE username = ?", (username,))
        FlaskServer.todos = cursor.fetchall()

        # Close the Config().database connection
        conn.close()
        # todos.append((todo,description))


        return  render_template('user_space.html',todos = FlaskServer.todos,username = username)
        
    @app.route('/')
    @printheaders
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
                FlaskServer.todos = cursor.fetchall()

                # Close the Config().database connection
                conn.close()
                return  render_template('user_space.html',todos = FlaskServer.todos,username = session['username'])
            else:
                conn = sqlite3.connect(Config().database)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users ")
                users = cursor.fetchall()
                conn.close()

                if users:
                    for user in users:
                        FlaskServer.available_emails.add(user[0])

        
            return render_template('home.html')

        else:
            conn = sqlite3.connect(Config().database)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users ")
            users = cursor.fetchall()
            conn.close()

            if users:
                for user in users:
                    FlaskServer.available_emails.add(user[0])

        
            return render_template('home.html')


    @app.route('/register')
    @printheaders
    def register():
        return  render_template('register.html')

    @app.route('/get_all_todos')
    @printheaders
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
        FlaskServer.todos = cursor.fetchall()
        return  jsonify(FlaskServer.todos)


    @app.route('/add_new_user',methods = ['POST', 'GET'])
    @printheaders
    def add_new_user():
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        if username and password:
            conn = sqlite3.connect(Config().database)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            conn.close()
            if not user:
                conn = sqlite3.connect(Config().database)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (email, username, password) VALUES (?, ?, ?)", (email, username, password))
                conn.commit()
                conn.close()
                FlaskServer.available_emails.add(email)
                message= "You have successfully registered, Now you can login"
                return render_template('home.html',message = message)
            else:
                message = "This username is already in Config().database, Please choose another one."
                return render_template('register.html',message = message)
        else:
            message = "Username and Password can not be empty"
            return render_template('register.html',message = message)


    @app.route('/user')
    @printheaders
    def user():
        # username = request.args.get('username')
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
        FlaskServer.todos = cursor.fetchall()
        message = "successfull login"
        flash(message)
        return  render_template('user_space.html',todos = FlaskServer.todos,username = username)


    @app.route('/login',methods = ['POST', 'GET'])
    @printheaders
    def login():
        username = request.form['username']
        if username[0].isdigit():
            abort(400)
            
        password = request.form['password']

        conn = sqlite3.connect(Config().database)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['username'] = username
            # return redirect(url_for('dashboard'))
            return redirect('/user')
        else:
            # return jsonify({'message': 'Invalid username or password'})
            message =   'Invalid username or password'
            return render_template('home.html',message=message)


    @app.route('/logout')
    @printheaders
    def logout():
        if session['username']:
            session['username'] = None
        return redirect('/')


    @app.route('/check_email_availability')
    @printheaders
    def check_email_availability():
        email = request.args.get('email')
        if email in FlaskServer.available_emails:
            return jsonify({'available': False})
        else:
            return jsonify({'available': True})


    @app.errorhandler(400)
    @printheaders
    def bad_request(error):
        # Perform the redirection here
        message =   'Interger is not allow in first place of username'
        return render_template('home.html',message=message)



    def run(self):
        FlaskServer.create_table()
        port = Config().httpport
        # FlaskServer.app.run(debug = True)
        flask_wsgi_server = WSGIServer(("0.0.0.0", port),FlaskServer.app.wsgi_app, spawn=10)
        flask_wsgi_server.serve_forever()