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

# Function to count rows in the first column
def count_rows_first_column(file_path):
    try:
        # Read the CSV file
        df = pd.read_csv(file_path, encoding='utf-8')
        # Count non-empty rows in the first column
        first_column = df.iloc[:, 0]  # Get the first column
        row_count = first_column.notna().sum()  # Count non-empty values
        return row_count
    except Exception as e:
        print(f"Error counting rows in the first column: {str(e)}")
        return -1  # Return -1 to indicate an error

# 1. Upload CSV to directory by clientID
@app.route('/process_csv', methods=['POST'])
def process_csv():
    # Get data from the request
    client_id = request.form.get('clientID')
    row_system = request.form.get('rowSystem')  # Expected row count from the client
    file = request.files.get('file')

    # Check for missing required fields
    if not client_id or not row_system or not file:
        return jsonify({'status': 'fail', 'message': 'Missing required inputs'}), 400

    try:
        row_system = int(row_system)  # Ensure rowSystem is an integer
    except ValueError:
        return jsonify({'status': 'fail', 'message': 'rowSystem must be an integer'}), 400

    # Create folder for the client if not exists
    client_folder = os.path.join(app.config['UPLOAD_FOLDER'], client_id)
    os.makedirs(client_folder, exist_ok=True)

    file_path = os.path.join(client_folder, file.filename)

    # Debugging: Check if file exists and print row count
    if os.path.exists(file_path) and os.path.isfile(file_path):
        try:
            # Count rows in the first column
            first_column_row_count = count_rows_first_column(file_path)
            if first_column_row_count == -1:
                return jsonify({'status': 'fail', 'message': 'Error counting rows in the first column'}), 500

            print(f"File found at {file_path} with {first_column_row_count} rows in the first column.")

            # Compare row count
            if first_column_row_count == row_system:
                return jsonify({
                    'status': 'success',
                    'message': 'File exists and matches rowSystem',
                    'rows': first_column_row_count,
                    'path': file_path
                }), 200
            else:
                # Row count mismatch; replace the file
                file.save(file_path)
                print(f"Row count mismatch. Server rows: {first_column_row_count}, Client rows: {row_system}. File replaced.")
                return jsonify({
                    'status': 'success',
                    'message': 'File row count mismatch. New file uploaded.',
                    'existing_rows': first_column_row_count,
                    'new_rows': row_system,
                    'path': file_path
                }), 200
        except Exception as e:
            print(f"Unexpected error while reading file: {str(e)}")
            return jsonify({'status': 'fail', 'message': f'Error reading existing file: {str(e)}'}), 500
    else:
        # File does not exist; upload the file
        try:
            file.save(file_path)
            print(f"New file uploaded to {file_path}.")
            return jsonify({
                'status': 'success',
                'message': 'File did not exist. New file uploaded.',
                'new_rows': row_system,
                'path': file_path
            }), 200
        except Exception as e:
            print(f"Error saving file {file_path}: {str(e)}")
            return jsonify({'status': 'fail', 'message': f'Error saving new file: {str(e)}'}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
