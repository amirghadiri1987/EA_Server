from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Set the base directory to save files
UPLOAD_FOLDER = '/root/EA_Server/ServerUpload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# Set the directory to save files
UPLOAD_FOLDER = '/home/amir/w/EA_Server/ServerUpload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({'status': 'fail', 'message': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'fail', 'message': 'No selected file'}), 400

    # Save the file
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    return jsonify({'status': 'success', 'message': 'File uploaded successfully'}), 200


def upload_data():
    pass


@app.route('/check_test_file', methods=['GET'])
def check_test_file():
    file_path = "/home/amir/w/ServerUpload/1001/test.txt"
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return jsonify({'status': 'success', 'message': 'Test file found', 'path': file_path}), 200
    else:
        return jsonify({'status': 'fail', 'message': 'Test file not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
