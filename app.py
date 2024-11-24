from flask import Flask, jsonify
from datetime import datetime


app = Flask(__name__)



@app.route("/")
def welcome():
    return "welcome in time_and_date server"

@app.route("/dt", methods=['GET'])
def time_and_date():

    # Get the current date and time
    print("yes this is inside-----")
    current_datetime = datetime.now()

    # Format the date and time as a string
    date_string = current_datetime.strftime('%Y-%m-%d')
    time_string = current_datetime.strftime('%H:%M:%S')

    # Prepare the response
    response = {
        'date': date_string,
        'time': time_string
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
