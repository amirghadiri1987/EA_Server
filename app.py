from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    pass


def upload_data():
    pass


def chech_csv():
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
