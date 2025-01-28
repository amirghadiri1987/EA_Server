from flask import Flask, request, jsonify
import os
import pandas as pd  # For reading and checking CSV file row count
import config

app = Flask(__name__)

# Consistent upload folder definition
UPLOAD_FOLDER = '/home/amir/w/ServerUpload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def hello_world():
    print("Configured upload folder:", config.load_file_upload)
    return "<p>Hello, World!</p>"

@app.route('/process_csv', methods=['POST'])
def process_csv():
    client_id = request.form.get('clientID')
    row_system = request.form.get('rowSystem')
    file = request.files.get('file')

    if not client_id or not row_system or not file:
        return jsonify({'status': 'fail', 'message': 'Missing required inputs'}), 400

    try:
        row_system = int(row_system)  # Ensure rowSystem is an integer
    except ValueError:
        return jsonify({'status': 'fail', 'message': 'rowSystem must be an integer'}), 400

    client_folder = os.path.join(app.config['UPLOAD_FOLDER'], client_id)
    os.makedirs(client_folder, exist_ok=True)

    file_path = os.path.join(client_folder, file.filename)

    if os.path.exists(file_path) and os.path.isfile(file_path):
        # File exists, check row count
        try:
            existing_df = pd.read_csv(file_path)
            existing_row_count = len(existing_df)
        except Exception as e:
            return jsonify({'status': 'fail', 'message': f'Error reading existing file: {str(e)}'}), 500

        if existing_row_count == row_system:
            return jsonify({
                'status': 'success',
                'message': 'File exists and matches rowSystem',
                'rows': existing_row_count,
                'path': file_path
            }), 200
        else:
            # Row counts do not match; upload the new file
            file.save(file_path)
            return jsonify({
                'status': 'success',
                'message': 'File row count mismatch. New file uploaded.',
                'existing_rows': existing_row_count,
                'new_rows': row_system,
                'path': file_path
            }), 200
    else:
        # File does not exist; upload the file
        file.save(file_path)
        return jsonify({
            'status': 'success',
            'message': 'File did not exist. New file uploaded.',
            'new_rows': row_system,
            'path': file_path
        }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
