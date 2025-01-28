from flask import Flask, request, jsonify
import os
import pandas as pd  # For reading and checking CSV file row count
import config

app = Flask(__name__)



# 1. Check if the CSV file exists in the directory
@app.route('/check_csv', methods=['GET'])
def check_csv():
    file_path = os.path.join(config.load_file_upload, f"{config.name_file_upload}.csv")  # Construct the full file path

    if os.path.exists(file_path) and os.path.isfile(file_path):
        print(f"CSV file exists at {file_path}")
        return jsonify({
            'status': 'success',
            'message': f"File found at {file_path}",
            'file_path': file_path
        }), 200
    else:
        print(f"CSV file not found at {file_path}")
        return jsonify({
            'status': 'fail',
            'message': f"File not found at {file_path}"
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
