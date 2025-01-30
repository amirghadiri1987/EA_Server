from flask import Flask, request, jsonify
from pandas import read_csv
import os
import pandas as pd  # For reading and checking CSV file row count
import config

app = Flask(__name__)

@app.route("/")
def hello_world():
    print("Configured upload folder:", config.load_file_upload)
    return "<p>Hello, World!</p>"


def import_database_from_excell(filepath):
    """ gets on excell file name and imports lookup data (data and failures) from it"""
    # df contains lookup data in the form of
    # Row Open Time	Symbol	Magic Number	Type	Volume	Open Price	S/L	T/P	Close Price	Close Time	Commission	Swap	Profit	Profit Points	Duration	Open Comment	Close Comment
    df = read_csv(filepath) 
    for index, row in df.iterrows():
        #print(row["Symbol"])
        pass

    








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

    # Get the path from the config where files should be uploaded
    client_folder = os.path.join(config.load_file_upload, client_id)
    
    # Ensure that the directory exists
    os.makedirs(client_folder, exist_ok=True)

    # Define the path where the file will be saved
    file_path = os.path.join(client_folder, file.filename)
    
    # Save the file
    file.save(file_path)

    # Respond with success message and file path
    return jsonify({
        'status': 'success',
        'message': 'File uploaded successfully',
        'file_path': file_path
    }), 200








# 4. Transfer data to CSV file.
@app.route('/append_csv', methods=['POST'])
def append_csv():
    pass

    
if __name__ == "__main__":
    #app.run(debug=True, host='0.0.0.0', port=5000)
    import_database_from_excell('/home/amir/w/ServerUpload/1001/Trade_Transaction.csv')
