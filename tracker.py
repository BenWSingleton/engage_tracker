from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/health", methods=['GET'])
def health():
    return jsonify("App is running"), 200

@app.route("/send_update", methods=['POST'])
def send_update():
    return