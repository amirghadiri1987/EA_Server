from flask import Flask, request, jsonify
from pandas import read_csv
import os
import sqlite3
import pandas as pd  # For reading and checking CSV file row count
import config

app = Flask(__name__)
# 3
@app.route("/")
def hello_world():
    print("Configured upload folder:", config.load_file_upload)
    return "<p>Hello, World!</p>"

def create_database():
    conn = sqlite3.connect(config.database_file_path)
    cur  = conn.cursor()

    # df contains lookup data in the form of
    # Row Open Time	Symbol	Magic Number	Type	Volume	Open Price	S/L	T/P	Close Price	Close Time	Commission	Swap	Profit	Profit Points	Duration	Open Comment	Close Comment

    # Create the table if it doesn't exist
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Trade_Transaction (
            id INTEGER PRIMARY KEY,
            open_time TEXT,
            symbol TEXT,
            magic_number INTEGER,
            type TEXT,
            volume REAL,
            open_price REAL,
            sl REAL,
            tp REAL,
            close_price REAL,
            close_time TEXT,
            commission REAL,
            swap REAL,
            profit REAL,
            profit_points REAL,
            duration TEXT,
            open_comment TEXT,
            close_comment TEXT
        )
    ''')


    conn.close()

    print("Database and table created successfully!")

def import_database_from_excell():
    """ gets on excell file name and imports lookup data (data and failures) from it"""
    
    # Use the file path from config
    filepath = f"{config.load_file_upload}/{config.name_file_upload}"

    # Read Excel file using pandas (you might need to use read_csv instead)
    df = pd.read_csv(filepath)  # If it's a CSV, use read_csv

    # Connect to the database
    conn = sqlite3.connect(config.database_file_path)
    cur = conn.cursor()

    # Iterate through rows of the DataFrame and insert into the database
    for index, row in df.iterrows():
        cur.execute('''
            INSERT INTO Trade_Transaction (
                open_time, symbol, magic_number, type, volume, open_price, 
                sl, tp, close_price, close_time, commission, swap, 
                profit, profit_points, duration, open_comment, close_comment
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row['Open Time'], row['Symbol'], row['Magic Number'], row['Type'],
            row['Volume'], row['Open Price'], row['S/L'], row['T/P'],
            row['Close Price'], row['Close Time'], row['Commission'], row['Swap'],
            row['Profit'], row['Profit Points'], row['Duration'], row['Open Comment'],
            row['Close Comment']
        ))

    # Commit and close the connection
    conn.commit()
    conn.close()
    print("Data imported successfully!")










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
    create_database()
    import_database_from_excell()
