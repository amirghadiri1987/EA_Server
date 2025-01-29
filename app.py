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
    client_id = request.args.get('clientID')
    file_name = request.args.get('fileName')

    if not client_id or not file_name:
        return jsonify({'status': 'fail', 'message': 'Missing clientID or fileName'}), 400

    file_path = os.path.join(config.load_file_upload, client_id, file_name)
    print(f"Checking file at path: {file_path}")  # Debugging print

    if not os.path.exists(file_path):
        print(f"File {file_name} not found for client {client_id}")  # Debugging print
        return jsonify({
            'status': 'fail',
            'message': f"File {file_name} not found for client {client_id}",
            'file_path': file_path
        }), 404

    try:
        # Read ONLY the first column ("Open Time") as a string
        df = pd.read_csv(file_path, usecols=[0], dtype=str, header=0)  
        df.columns = ['Open Time']  # Ensure correct column naming

        # Remove empty rows (strip spaces & drop NaN values)
        count_open_time = df['Open Time'].dropna().str.strip().ne('').sum()

        print("\n--- First 10 values in 'Open Time' column ---")  
        print(df['Open Time'].head(10))  # Print first 10 values for debugging
        print(f"\nTotal non-empty rows in 'Open Time': {count_open_time}")  # Debugging print

        return jsonify({
            'status': 'success',
            'message': f"File {file_name} processed successfully",
            'client_id 12': client_id,
            'file_name': file_name,
            'open_time_row_count': count_open_time
        }), 200
    except Exception as e:
        print(f"Error processing file: {str(e)}")  # Debugging print
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
