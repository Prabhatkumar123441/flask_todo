from flask import Flask, render_template, request, jsonify, session, redirect, abort, make_response, url_for
import sqlite3
from datetime import timedelta
from functools import wraps
from flask.views import MethodView

app = Flask(__name__)

app.secret_key = 'your_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)


DATABASE = 'DataBase.db'

todos = []


available_emails = set()

def create_table():
    conn = sqlite3.connect(DATABASE)
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



@app.route('/')
@printheaders
def home():
    username = request.cookies.get("username")
    print("username---in cookies",username)
    if "username" in session:
        if session['username']:
            username = session['username']# Replace with the actual username

            # Connect to the SQLite database
            conn = sqlite3.connect(DATABASE)
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

            # Close the database connection
            conn.close()
            return  render_template('user_space.html',todos = todos,username = session['username'])
        else:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users ")
            users = cursor.fetchall()
            conn.close()

            if users:
                for user in users:
                    available_emails.add(user[0])

    
        return render_template('home.html')
        
        # response = make_response(render_template('home.html'))  # Renders an HTML page
        # response.set_cookie('username', username, max_age=600)  # Expires in 1 hour
        # return response

    else:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ")
        users = cursor.fetchall()
        conn.close()

        if users:
            for user in users:
                available_emails.add(user[0])

    
        return render_template('home.html')


@app.route('/register')
@printheaders
def register():
   print("user want to create new account--")
   return render_template('register.html')

# @app.route("/check_cookies")
# def check_cookies():
#     response = request.args['response']
#     username_new = request.args['username']
#     print("response, username_new --- ",response, username_new)
#     # username = response.cookies.get('username')
#     # print("old and new user name --- ",username, username_new )
#     if "cookies" not in response:
#         response.set_cookie('username', username_new , max_age=300)
    
#     return response


@app.route('/login',methods = ['POST', 'GET'])
@printheaders
def login():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        # session.permanent = True
        session['username'] = username
        print(len(session.keys()))
        return redirect('/user')
    else:
        # return jsonify({'message': 'Invalid username or password'})
        message =   'Invalid username or password'
        return render_template('home.html',message=message)


@app.route('/user')
@printheaders
def user():
    # username = request.args.get('username')
    if 'username' in session:
        username = session['username']
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='todos'")
        table_exists = cursor.fetchone()

        # If 'todos' table doesn't exist, create it
        # app.logger.debug("Log---",username)
        if not table_exists:
            cursor.execute("CREATE TABLE IF NOT EXISTS todos (todo TEXT UNIQUE, description TEXT, username TEXT)")
        cursor.execute("SELECT todo, description FROM todos WHERE username = ?", (username,))
        todos = cursor.fetchall()
        
        return  render_template('user_space.html',todos = todos, username = username)

        # response = make_response(render_template('user_space.html',todos = todos, username = username))  # Renders an HTML page
        # # response.set_cookie('username', username, max_age=300)  # Expires in 1 hour
        # # return redirect('/check_cookies')
        # return redirect(url_for(".check_cookies", response = response, username = username))
    else:
        return redirect('/')


@app.route('/add_new_user',methods = ['POST', 'GET'])
@printheaders
def add_new_user():
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    if username and password:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? or email = ?", (username,email))
        user = cursor.fetchone()
        conn.close()
        if not user:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (email, username, password) VALUES (?, ?, ?)", (email, username, password))
            conn.commit()
            conn.close()
            available_emails.add(email)
            message= "You have successfully registered, Now you can login"
            return render_template('home.html',message = message)
        else:
            print(f"{user}  user is already exist table")
            message = "This username is already in database, Please choose another one."
            return render_template('register.html',message = message)
    else:
        message = "Username and Password can not be empty"
        return render_template('register.html',message = message)


@app.route('/update', methods=['POST'])
@printheaders
def update():
    data = request.get_json()
    todo = data.get('todo')
    description = data.get('description')
    

@app.route('/delete/<todo>/<des>')
@printheaders
def delete_row(todo,des):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get the todo based on the index
    # cursor.execute("SELECT todo FROM todos LIMIT ?, 1", (index - 1,))
    query = f"DELETE FROM todos WHERE todo = '{todo}' and description = '{des}' and username = '{session['username']}'"
    cursor.execute(query)
    conn.commit()
    # print('number of rows deleted', cursor.rowcount)
    conn.close()
        
    return redirect('/user')


@app.route("/delete_all",methods=['DELETE'])
def delete_all_todos():
    global todos
    todos.clear()
    if session['username']:
        username = session['username']
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        

        # Check if 'todos' table exists
        cursor.execute("DELETE FROM todos WHERE username = ?", (username,))
        conn.commit()
        cursor.execute("SELECT todo, description FROM todos WHERE username = ?", (username,))
        todos = cursor.fetchall()
        conn.close()
        todos = []
        return jsonify({"message": "All todos deleted successfully."}), 200


@app.route('/logout')
@printheaders
def logout():
   print("session---",session)
   print(len(session.keys()))
   for ky in session.keys():
       print("ky--- ",ky)
   if "username" in  session:
      del session['username']
   return redirect('/')


@app.route('/add_todo', methods=['POST'])
@printheaders
def add_todo():
    # Get the form data
    todo = request.form['todo']
    description = request.form['description']
    username = session['username']# Replace with the actual username

    # Connect to the SQLite database
    conn = sqlite3.connect(DATABASE)
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

    # Close the database connection
    conn.close()
    # todos.append((todo,description))


    return  render_template('user_space.html',todos = todos)
    

@app.route('/check_email_availability')
@printheaders
def check_email_availability():
    email = request.args.get('email')
    print("emails --- ",email,available_emails)
    if email in available_emails:
        return jsonify({'available': False})
    else:
        return jsonify({'available': True})


@app.errorhandler(400)
def bad_request(error):
    # Perform the redirection here
    message =   'Integer is not allow in first place of username'
    return render_template('home.html',message=message)



if __name__ == '__main__':
   create_table()
   app.run(debug = True)