from flask import Flask, request, jsonify
from pandas import read_csv
import os
import sqlite3
import pandas as pd  # For reading and checking CSV file row count
import config

app = Flask(__name__)

# 8

@app.route("/")
def hello_world():
    print("Configured upload folder:", config.load_file_upload)
    return "<p>Hello, World!</p>"



def import_database_from_excell(clientID):
    """ gets an excel file name and imports lookup data (data and failures) from it"""
    
    filepath = f"{config.load_file_upload}/{clientID}/{config.name_file_upload}"
    
    # Create connection and table if it doesn't exist
    conn = sqlite3.connect(config.database_file_path)
    cur = conn.cursor()

    # Drop the table if it already exists (to avoid errors on reruns)
    cur.execute('DROP TABLE IF EXISTS Trade_Transaction')

    # Create table
    cur.execute("""CREATE TABLE IF NOT EXISTS Trade_Transaction(
        id INTEGER PRIMARY KEY,
        open_time DATE,
        symbol TEXT,
        magic_number INTEGER,
        type TEXT,
        volume REAL,
        open_price REAL,
        sl REAL,
        tp REAL,
        close_price REAL,
        close_time DATE,
        commission REAL,
        swap REAL,
        profit REAL,
        profit_points REAL,
        duration TEXT,
        open_comment TEXT,
        close_comment TEXT);""")
    
    # Commit the table creation changes
    conn.commit()

    # Read CSV
    df = pd.read_csv(filepath)

    # Ensure that the number of columns is correct for each row
    for index, row in df.iterrows():
        print(f"Row {index}: {row}")
        if len(row) == 17:  # Check if the row has 17 columns
            cur.execute('''INSERT INTO Trade_Transaction (open_time, symbol, magic_number, type, volume, open_price, sl, tp, close_price, close_time, commission, swap, profit, profit_points, duration, open_comment, close_comment)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                        (row['Open Time'], row['Symbol'], row['Magic Number'], row['Type'], row['Volume'], row['Open Price'], row['S/L'], row['T/P'], row['Close Price'], 
                        row['Close Time'], row['Commission'], row['Swap'], row['Profit'], row['Profit Points'], row['Duration'], row['Open Comment'], row['Close Comment']))
        else:
            print(f"Skipping row {index} with incorrect number of columns. Length: {len(row)}")

    # Commit the data insertion and close the connection
    conn.commit()
    conn.close()










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
    import_database_from_excell(1001)
