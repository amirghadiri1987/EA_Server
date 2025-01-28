from flask import Flask, request, jsonify
import os
import pandas as pd  # For reading and checking CSV file row count
import config

app = Flask(__name__)



# 1. Is there a CSV file in the directory?
@app.route('/check_csv', methods=['GET'])
def check_csv():
    directory_path = config.load_file_upload  # Get the directory path from config
    print(f"Checking directory: {directory_path}")  # Debugging: Print directory being checked

    # Check if directory exists
    if not os.path.exists(directory_path):
        print(f"Directory {directory_path} does not exist.")  # Debugging: Print error if directory doesn't exist
        return jsonify({'status': 'fail', 'message': f'Directory {directory_path} does not exist.'}), 400

    # Get a list of CSV files in the directory
    csv_files = [f for f in os.listdir(directory_path) if f.endswith('.csv')]
    print(f"CSV files found: {csv_files}")  # Debugging: Print list of CSV files found

    # If CSV files exist, return their names
    if csv_files:
        return jsonify({
            'status': 'success',
            'message': f'Found {len(csv_files)} CSV file(s).',
            'files': csv_files
        }), 200
    else:
        print(f"No CSV files found in the directory.")  # Debugging: Print if no CSV files are found
        return jsonify({
            'status': 'fail',
            'message': 'No CSV files found in the directory.'
        }), 404







# 2. Count the number of rows in the first column.
@app.route('/count_rows_csv', methods=['POST'])
def count_rows_csv():
    pass

# 1. Upload CSV to directory by clientID
@app.route('/process_csv', methods=['POST'])
def process_csv():
    pass

# 3. Transfer data to CSV file.
@app.route('/append_csv', methods=['POST'])
def append_csv():

    
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
