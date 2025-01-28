from flask import Flask, request, jsonify
import os
import pandas as pd  # For reading and checking CSV file row count
import config

app = Flask(__name__)

@app.route("/")
def hello_world():
    print("Configured upload folder:", config.load_file_upload)
    return "<p>Hello, World!</p>"



# 1. Check if the CSV file exists in the directory for a specific client
@app.route('/check_csv', methods=['GET'])
def check_csv():
    client_id = request.args.get('clientID')  # Get clientID from the request
    if not client_id:
        return jsonify({'status': 'fail', 'message': 'Missing clientID'}), 400

    # Construct the path using the clientID
    file_path = os.path.join(config.load_file_upload, client_id, f"{config.name_file_upload}.csv")

    if os.path.exists(file_path) and os.path.isfile(file_path):
        print(f"CSV file exists for client {client_id} at {file_path}")
        return jsonify({
            'status': 'success',
            'message': f"File found for client {client_id} at {file_path}",
            'file_path': file_path
        }), 200
    else:
        print(f"CSV file not found for client {client_id} at {file_path}")
        return jsonify({
            'status': 'fail',
            'message': f"File not found for client {client_id} at {file_path}"
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
    pass

    
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
