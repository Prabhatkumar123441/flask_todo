from flask import Blueprint, request, redirect, session, render_template, jsonify, flash
from functools import wraps
import sqlite3
from servers.flask.responsebuilder import ResponseBuilder
from config  import Config
from flask_pydantic import validate
from pydantic import BaseModel, Field
from servers.flask.log.logger import Log
from servers.flask.log.logtype import LogLevel

class TodoForm(BaseModel):
    todo: str = Field(..., max_length=100)
    description: str = Field(..., max_length=255)

todos = []

user_r = Blueprint("user", __name__)


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

@user_r.route('/delete/<todo>/<des>')
@printheaders
@session_required
def delete_row(todo,des):
    conn = sqlite3.connect(Config.database)
    cursor = conn.cursor()
    
    # Get the todo based on the index
    # cursor.execute("SELECT todo FROM todos LIMIT ?, 1", (index - 1,))
    query = f"DELETE FROM todos WHERE todo = '{todo}' and description = '{des}' and username = '{session['username']}'"
    cursor.execute(query)
    conn.commit()
    # print('number of rows deleted', cursor.rowcount)
    conn.close()
        
    return redirect('/user')

@user_r.route("/delete_all_todos",methods = ['DELETE'])
@printheaders
@session_required
def delete_all_todos():
    global todos
    todos.clear()
    if session['username']:
        username = session['username']
        conn = sqlite3.connect(Config.database)
        cursor = conn.cursor()
        

        # Check if 'todos' table exists
        cursor.execute("DELETE FROM todos WHERE username = ?", (username,))
        conn.commit()
        cursor.execute("SELECT todo, description FROM todos WHERE username = ?", (username,))
        todos = cursor.fetchall()
        conn.close()
        todos = []
        return jsonify({"message": "All todos deleted successfully."}), 200

@user_r.route('/add_todo', methods=['POST'])
@printheaders
@session_required
@validate(form=TodoForm)
def add_todo(form: TodoForm):

    
    # Get the form data
    todo = request.form['todo']
    description = request.form['description']

    Log().getinstance().write_log(LogLevel.DEBUG, "todo = %s,description = %s"%(todo,description),"add_todo" )
    if "username" in session:
        username = session['username']# Replace with the actual username

        # Connect to the SQLite Config.database
        conn = sqlite3.connect(Config.database)
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
        todos = cursor.fetchall()
        if len(todos) == 0:
        
            cursor.execute("INSERT INTO todos (todo, description, username) VALUES (?, ?, ?)", (todo, description, username))
            conn.commit()
        cursor.execute("SELECT todo, description FROM todos WHERE username = ?", (username,))
        todos = cursor.fetchall()

        # Close the Config.database connection
        conn.close()
        # todos.append((todo,description))


        return  render_template('user_space.html',todos = todos, username = username)
    else:
        return redirect('/')
    
@user_r.route('/user')
@printheaders
@session_required
def user():
    # username = request.args.get('username')
    username = session['username']
    conn = sqlite3.connect(Config.database)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='todos'")
    table_exists = cursor.fetchone()

    # If 'todos' table doesn't exist, create it
    # app.logger.debug("Log---",username)
    if not table_exists:
        cursor.execute("CREATE TABLE IF NOT EXISTS todos (todo TEXT UNIQUE, description TEXT, username TEXT)")
    cursor.execute("SELECT todo, description FROM todos WHERE username = ?", (username,))
    todos = cursor.fetchall()
    message = "successfull login"
    flash(message)
    return render_template('user_space.html',todos = todos,username = username)


@user_r.route('/logout')
@printheaders
@session_required
def logout():
    if session['username']:
        session['username'] = None
    return redirect('/')