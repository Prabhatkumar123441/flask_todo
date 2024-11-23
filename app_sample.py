from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_bcrypt import Bcrypt
from datetime import timedelta

# Initialize the Flask app
app = Flask(__name__)

# Configure the app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'supersecretkey'  # Change this to a strong secret in production
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

# Define a User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

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

# Initialize the database
@app.before_first_request
def create_tables():
    db.create_all()

# Route to register a new user
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # Check if username exists
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists!"}), 400
    
    # Hash the password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    # Create new user
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully!"}), 201

# Route to login and get JWT token
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    # Check if user exists and password is correct
    if user and bcrypt.check_password_hash(user.password, password):
        # Create a JWT token
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    
    return jsonify({"message": "Invalid credentials"}), 401

# Protected route that requires a valid token
@app.route('/protected', methods=['GET'])
@printheaders
@jwt_required()
def protected():
    return jsonify(message="This is a protected route")

# Route to get all users (requires token)
@app.route('/users', methods=['GET'])
@printheaders
@jwt_required()
def get_users():
    users = User.query.all()
    users_list = [{"id": user.id, "username": user.username} for user in users]
    return jsonify(users=users_list), 200

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
