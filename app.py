from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Consistent upload folder definition
UPLOAD_FOLDER = '/home/amir/w/EA_Server/ServerUpload'  # Or '/root/EA_Server/ServerUpload' if needed
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    client_id = request.form.get('clientID')
    if not client_id:
        return jsonify({'status': 'fail', 'message': 'Missing clientID'}), 400

    if 'file' not in request.files:
        return jsonify({'status': 'fail', 'message': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'fail', 'message': 'No selected file'}), 400

    client_folder = os.path.join(app.config['UPLOAD_FOLDER'], client_id)
    os.makedirs(client_folder, exist_ok=True)

    file_path = os.path.join(client_folder, file.filename)
    file.save(file_path)

    return jsonify({'status': 'success', 'message': 'File uploaded successfully', 'path': file_path}), 200



@app.route('/check_file', methods=['GET'])  # More generic endpoint name
def check_file():
    client_id = request.args.get('clientID')  # Get clientID as a query parameter
    filename = request.args.get('filename')  # Get filename as a query parameter

    if not client_id or not filename:
        return jsonify({'status': 'fail', 'message': 'Missing clientID or filename'}), 400


    file_path = os.path.join(app.config['UPLOAD_FOLDER'], client_id, filename)


    if os.path.exists(file_path) and os.path.isfile(file_path):
        return jsonify({'status': 'success', 'message': 'File found', 'path': file_path}), 200
    else:
        return jsonify({'status': 'fail', 'message': 'File not found'}), 404



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
