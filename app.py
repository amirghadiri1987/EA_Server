from flask import Flask, request, jsonify
import os
import pandas as pd  # For reading and checking CSV file row count
import config

app = Flask(__name__)

@app.route("/")
def hello_world():
    print("Configured upload folder:", config.load_file_upload)
    return "<p>Hello, World!</p>"



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




@app.route('/count_rows_csv', methods=['POST'])
def count_rows_csv():
    # Get the clientID and fileName from the request data
    client_id = request.form.get('clientID')
    file_name = request.form.get('fileName')

    if not client_id or not file_name:
        return jsonify({'status': 'fail', 'message': 'Missing clientID or fileName'}), 400

    # Build the file path
    file_path = os.path.join(config.load_file_upload, client_id, file_name)

    # Check if the file exists
    if not os.path.exists(file_path):
        return jsonify({
            'status': 'fail',
            'message': f"File {file_name} not found for client {client_id}",
            'file_path': file_path
        }), 404

    try:
        # Read the CSV file using pandas and count the rows in the first column
        df = pd.read_csv(file_path, encoding='utf-8')
        # Count the non-empty entries in the first column (usually column 0)
        first_column_count = df.iloc[:, 0].dropna().count()

        return jsonify({
            'status': 'success',
            'message': f"File {file_name} processed successfully",
            'client_id': client_id,
            'file_name': file_name,
            'first_column_row_count': first_column_count
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'fail',
            'message': f"Error processing file: {str(e)}"
        }), 500



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
