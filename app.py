from flask import Flask, request, jsonify
import os
import pandas as pd  # w For reading and checking CSV file row count
import config

app = Flask(__name__)

# Consistent upload folder definition
UPLOAD_FOLDER = '/home/amir/w/ServerUpload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def hello_world():
    print("Configured upload folder:", config.load_file_upload)
    return "<p>Hello, World!</p>"

# upload file CSV to directory upload clinetID
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

    # Check if the file exists
    if os.path.exists(file_path) and os.path.isfile(file_path):
        try:
            # File exists, compare row count
            existing_df = pd.read_csv(file_path)
            existing_row_count = len(existing_df)

            if existing_row_count == row_system:
                # File exists and row count matches, no need to replace
                return jsonify({
                    'status': 'success',
                    'message': 'File exists and matches rowSystem',
                    'rows': existing_row_count,
                    'path': file_path
                }), 200
            else:
                # Row counts do not match, replace the file
                file.save(file_path)
                return jsonify({
                    'status': 'success',
                    'message': 'File row count mismatch. New file uploaded.',
                    'existing_rows': existing_row_count,
                    'new_rows': row_system,
                    'path': file_path
                }), 200
        except Exception as e:
            return jsonify({'status': 'fail', 'message': f'Error reading existing file: {str(e)}'}), 500
    else:
        # File does not exist; upload the new file
        try:
            file.save(file_path)
            return jsonify({
                'status': 'success',
                'message': 'File did not exist. New file uploaded.',
                'new_rows': row_system,
                'path': file_path
            }), 200
        except Exception as e:
            return jsonify({'status': 'fail', 'message': f'Error saving new file: {str(e)}'}), 500







# append dato to file csv
@app.route('/append_csv', methods=['POST'])
def append_csv():
    client_id = request.form.get('clientID')
    row_system = request.form.get('rowSystem')
    data = request.form.get('data')  # CSV-like data to append

    if not client_id or not row_system or not data:
        return jsonify({'status': 'fail', 'message': 'Missing clientID, rowSystem, or data'}), 400

    try:
        row_system = int(row_system)  # Ensure rowSystem is an integer
    except ValueError:
        return jsonify({'status': 'fail', 'message': 'rowSystem must be an integer'}), 400

    client_folder = os.path.join(app.config['UPLOAD_FOLDER'], client_id)
    os.makedirs(client_folder, exist_ok=True)

    file_path = os.path.join(client_folder, 'Trade_Transaction.csv')

    # Convert data string to DataFrame (CSV data)
    try:
        new_data = pd.read_csv(pd.compat.StringIO(data), header=None)
    except Exception as e:
        return jsonify({'status': 'fail', 'message': f'Error parsing data: {str(e)}'}), 400

    # If the file exists, check row count and append data; otherwise, create a new file
    if os.path.exists(file_path):
        try:
            existing_data = pd.read_csv(file_path)
            existing_row_count = len(existing_data)

            if existing_row_count != row_system:
                # Row counts do not match, upload the new file (replace existing one)
                return process_csv()  # Call process_csv to upload the entire file
            else:
                # Row counts match, append data to the existing file
                updated_data = pd.concat([existing_data, new_data], ignore_index=True)
        except Exception as e:
            return jsonify({'status': 'fail', 'message': f'Error reading existing file: {str(e)}'}), 500
    else:
        # File does not exist; create a new file with the provided rows
        updated_data = new_data

    # Save updated data to the file
    try:
        updated_data.to_csv(file_path, index=False)
        return jsonify({'status': 'success', 'message': 'Data appended successfully', 'path': file_path}), 200
    except Exception as e:
        return jsonify({'status': 'fail', 'message': f'Error saving file: {str(e)}'}), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
