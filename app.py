from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Set the base directory to save files
UPLOAD_FOLDER = '/root/EA_Server/ServerUpload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    pass


def upload_data():
    pass


@app.route('/check_test_file', methods=['GET'])
def check_test_file():
    print("Received request for file check")
    file_path = "/home/amir/w/ServerUpload/1001/test.txt"
    print(f"Checking path: {file_path}")
    if os.path.exists(file_path) and os.path.isfile(file_path):
        print("File found!")
        return jsonify({'status': 'success', 'message': 'Test file found', 'path': file_path}), 200
    else:
        print("File not found!")
        return jsonify({'status': 'fail', 'message': 'Test file not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
