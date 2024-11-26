from flask import Flask, request, jsonify
from gevent.pywsgi import WSGIServer

app = Flask(__name__)

# Helper function for each operation
def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

def multiply(x, y):
    return x * y

def divide(x, y):
    if y == 0:
        return "Error: Division by zero"
    return x / y

# Route for addition
@app.route('/add', methods=['GET', 'POST'])
def add_route():
    data = request.get_json() if request.method == 'POST' else request.args
    try:
        x = float(data['x'])
        y = float(data['y'])
        result = add(x, y)
        return jsonify({"operation": "add", "result": result})
    except (KeyError, ValueError):
        return jsonify({"error": "Invalid input, please provide x and y as numbers"}), 400

# Route for subtraction
@app.route('/subtract', methods=['GET', 'POST'])
def subtract_route():
    data = request.get_json() if request.method == 'POST' else request.args
    try:
        x = float(data['x'])
        y = float(data['y'])
        result = subtract(x, y)
        return jsonify({"operation": "subtract", "result": result})
    except (KeyError, ValueError):
        return jsonify({"error": "Invalid input, please provide x and y as numbers"}), 400

# Route for multiplication
@app.route('/multiply', methods=['GET', 'POST'])
def multiply_route():
    data = request.get_json() if request.method == 'POST' else request.args
    try:
        x = float(data['x'])
        y = float(data['y'])
        result = multiply(x, y)
        return jsonify({"operation": "multiply", "result": result})
    except (KeyError, ValueError):
        return jsonify({"error": "Invalid input, please provide x and y as numbers"}), 400

# Route for division
@app.route('/divide', methods=['GET', 'POST'])
def divide_route():
    data = request.get_json() if request.method == 'POST' else request.args
    try:
        x = float(data['x'])
        y = float(data['y'])
        result = divide(x, y)
        return jsonify({"operation": "divide", "result": result})
    except (KeyError, ValueError):
        return jsonify({"error": "Invalid input, please provide x and y as numbers"}), 400

if __name__ == "__main__":
    # app.run()
    http_port = 5000
    httpd = WSGIServer(("0.0.0.0", http_port), app.wsgi_app, spawn=5)
    httpd.serve_forever()
