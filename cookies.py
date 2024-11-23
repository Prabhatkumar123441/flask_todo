from flask import Flask, request, make_response, redirect, url_for
from datetime import timedelta, datetime

app = Flask(__name__)

# Set a secret key for session security (necessary if using sessions)
app.secret_key = 'your_secret_key'

# Route to set a cookie
@app.route('/set_cookie')
def set_cookie():
    resp = make_response("Cookie has been set!")  # Create a response object
    expires = datetime.now() + timedelta(days=1)  # Set cookie to expire in 1 day
    # Set a cookie named 'username', value 'john_doe' with expiration and security options
    resp.set_cookie('username', 'john_doe', expires=expires, httponly=True, secure=True, samesite='Lax')
    return resp

# Route to retrieve the cookie
@app.route('/get_cookie')
def get_cookie():
    username = request.cookies.get('username')  # Retrieve the 'username' cookie
    if username:
        return f'Welcome back, {username}!'
    else:
        return 'No cookie found!'

# Route to delete the cookie
@app.route('/delete_cookie')
def delete_cookie():
    resp = make_response("Cookie has been deleted!")  # Create a response object
    resp.delete_cookie('username')  # Delete the 'username' cookie
    return resp

# Route to check if the cookie exists
@app.route('/dashboard')
def dashboard():
    username = request.cookies.get('username')  # Get 'username' cookie
    print("username---",username)
    if username:
        return f'Hello, {username}, welcome to your dashboard!'
    else:
        return redirect(url_for('login'))  # Redirect to login if no cookie is found

# Simulated login route (just sets a cookie)
@app.route('/login')
def login():
    resp = make_response("You are logged in!")
    expires = datetime.now() + timedelta(days=1)
    resp.set_cookie('username', 'john_doe', expires=expires, httponly=True, secure=True, samesite='Lax')
    return resp

if __name__ == '__main__':
    app.run(debug=True)
