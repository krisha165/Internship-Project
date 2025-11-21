from flask import Flask, request, jsonify

app = Flask(__name__)

# Example in-memory data
options_data = [
    {"index": "NIFTY", "strike": 23000, "type": "CALL", "expiry": "2025-11-14"}
]

#  GET method – view all options
@app.route('/options', methods=['GET'])
def get_options():
    return jsonify(options_data)

#  POST method – add new option
@app.route('/options', methods=['POST'])
def add_option():
    new_option = request.get_json()  # get JSON data from request
    options_data.append(new_option)
    return jsonify({"message": "Option added successfully!", "data": new_option})

#  Root route
@app.route('/')
def home():
    return "Welcome to the Options API!"

if __name__ == '__main__':
    app.run(debug=True,port=5018)
