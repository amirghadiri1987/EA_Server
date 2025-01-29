from flask import Flask, request, jsonify
import os
import pandas as pd  # For reading and checking CSV file row count
import config

app = Flask(__name__)

@app.route("/")
def hello_world():
    print("Configured upload folder:", config.load_file_upload)
    return "<p>Hello, World!</p>"




# 1. Is there a CSV file in the directory?
@app.route('/check_csv', methods=['GET'])
def check_csv():
    client_id = request.args.get('clientID')
    file_name = request.args.get('fileName')

    if not client_id or not file_name:
        return jsonify({'status': 'fail', 'message': 'Missing clientID or fileName'}), 400

    file_path = os.path.join(config.load_file_upload, client_id, file_name)

    if os.path.exists(file_path):
        return jsonify({
            'status': 'success',
            'message': f"File {file_name} found for client {client_id}",
            'file_path': file_path
        }), 200
    else:
        return jsonify({
            'status': 'fail',
            'message': f"File {file_name} not found for client {client_id}",
            'file_path': file_path
        }), 404


# 2. Count the number of rows in the first column.
@app.route('/count_rows_csv', methods=['GET'])
def count_rows_csv():
    pass













# 3. Upload CSV to directory by clientID
# Set the upload folder from config
UPLOAD_FOLDER = config.load_file_upload
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route('/process_csv', methods=['POST'])
def process_csv():
    client_id = request.form.get('clientID')

    if not client_id:
        return jsonify({'status': 'fail', 'message': 'Missing clientID'}), 400

    if 'file' not in request.files:
        return jsonify({'status': 'fail', 'message': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'fail', 'message': 'No selected file'}), 400

    # Define the client-specific directory
    client_folder = os.path.join(app.config['UPLOAD_FOLDER'], client_id)
    os.makedirs(client_folder, exist_ok=True)  # Ensure directory exists

    # Save the file
    file_path = os.path.join(client_folder, file.filename)
    file.save(file_path)

    print(f"File uploaded: {file_path}")  # Debugging print

    return jsonify({
        'status': 'success',
        'message': 'File uploaded successfully',
        'path': file_path
    }), 200







# 4. Transfer data to CSV file.
@app.route('/append_csv', methods=['POST'])
def append_csv():
    pass

    
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
