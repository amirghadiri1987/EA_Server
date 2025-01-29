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
    # Get the clientID and fileName from the query parameters
    client_id = request.args.get('clientID')
    file_name = request.args.get('fileName')

    if not client_id or not file_name:
        return jsonify({'status': 'fail', 'message': 'Missing clientID or fileName'}), 400

    # Build the file path
    file_path = os.path.join(config.load_file_upload, client_id, file_name)
    print(f"Checking file at path: {file_path}")  # Debugging print statement

    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"File {file_name} not found for client {client_id}")  # Debugging print statement
        return jsonify({
            'status': 'fail',
            'message': f"File {file_name} not found for client {client_id}",
            'file_path': file_path
        }), 404

    try:
        # Read the CSV file using pandas
        df = pd.read_csv(file_path, encoding='utf-8')
        print(f"CSV file loaded successfully: {file_name}")  # Debugging print statement
        
        # Count all rows in the first column (including empty rows)
        first_column_count = len(df.iloc[:, 0])  # Use len() to count all rows
        first_column_count = int(first_column_count)  # Convert to regular Python int
        print(f"Row count in first column: {first_column_count}")  # Debugging print statement

        return jsonify({
            'status': 'success',
            'message': f"File {file_name} processed successfully",
            'client_id 2': client_id,
            'file_name': file_name,
            'first_column_row_count': first_column_count
        }), 200
    except Exception as e:
        print(f"Error processing file: {str(e)}")  # Debugging print statement
        return jsonify({
            'status': 'fail',
            'message': f"Error processing file: {str(e)}"
        }), 500









# 3. Upload CSV to directory by clientID
@app.route('/process_csv', methods=['POST'])
def process_csv():
    pass

# 4. Transfer data to CSV file.
@app.route('/append_csv', methods=['POST'])
def append_csv():
    pass

    
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
