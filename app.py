from flask import Flask, request, jsonify
import os
import shutil
import sqlite3
import pandas as pd
import config

app = Flask(__name__)

# 12
# TODO some health check url
@app.route("/v1/ok")
def health_check():
    ret = {'message': 'ok'}
    return jsonify(ret), 200

# TODO Fix simple welcome page 
@app.route("/")
def hello_world():
    print("Configured upload folder:", config.load_file_upload)
    return "<p>Hello, World!</p>"

# TODO Test function check_and_upload_file in mql5
def check_and_upload_file(clientID):
    """Check if the Excel file exists on the server and upload it if not."""
    
    # File path on the client's system and on the server
    client_file_path = f"{config.load_file_upload}/{clientID}/{config.name_file_upload}"
    server_file_path = f"{config.load_file_upload}/{clientID}/{config.name_file_upload}"

    if not os.path.exists(server_file_path):  # Check if file exists on server
        print(f"File not found on server. Uploading file for client {clientID}...")
        
        # Logic to upload file from client system to server (may depend on how the client is transferring the file)
        # For example, copying the file from a local directory
        shutil.copy(client_file_path, server_file_path)
        print("File uploaded successfully.")
    else:
        print(f"File already exists on the server for client {clientID}.")



# TODO Test function transfer_to_database in mql5
def transfer_to_database(clientID):
    """Transfers data from the uploaded Excel file to the database efficiently, with progress updates."""
    
    filepath = f"{config.load_file_upload}/{clientID}/{config.name_file_upload}"
    
    if not os.path.exists(filepath):
        print(f"[ERROR] File not found: {filepath}")
        return
    
    print(f"[INFO] Starting database transfer for client {clientID}...")

    # Create connection and optimize performance settings
    conn = sqlite3.connect(config.database_file_path)
    cur = conn.cursor()
    
    cur.execute("PRAGMA synchronous = OFF;")  
    cur.execute("PRAGMA journal_mode = WAL;")  

    # Create table if not exists
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

    conn.commit()
    print("[INFO] Database and table are ready.")

    # Read the CSV file
    df = pd.read_csv(filepath)
    print(f"[INFO] Found {len(df)} rows in the CSV file.")

    batch_size = 100
    data_batch = []

    for index, row in df.iterrows():
        data_batch.append((
            row['Open Time'], row['Symbol'], row['Magic Number'], row['Type'], row['Volume'], 
            row['Open Price'], row['S/L'], row['T/P'], row['Close Price'], row['Close Time'], 
            row['Commission'], row['Swap'], row['Profit'], row['Profit Points'], row['Duration'], 
            row['Open Comment'], row['Close Comment']
        ))

        # Commit every batch_size rows
        if len(data_batch) >= batch_size:
            cur.executemany('''INSERT INTO Trade_Transaction (open_time, symbol, magic_number, type, volume, open_price, sl, tp, close_price, close_time, commission, swap, profit, profit_points, duration, open_comment, close_comment)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data_batch)
            conn.commit()
            print(f"[INFO] Inserted {batch_size} rows into the database.")
            data_batch = []  

    # Insert any remaining data
    if data_batch:
        cur.executemany('''INSERT INTO Trade_Transaction (open_time, symbol, magic_number, type, volume, open_price, sl, tp, close_price, close_time, commission, swap, profit, profit_points, duration, open_comment, close_comment)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data_batch)
        conn.commit()
        print(f"[INFO] Inserted final {len(data_batch)} rows into the database.")

    conn.close()
    print("[SUCCESS] Data transfer completed successfully!")


    
# TODO Test function check_row_count in mql5
def check_row_count(clientID):
    """Check if the number of rows in the database matches the number of rows in the Excel file."""
    
    # File path on the server
    filepath = f"{config.load_file_upload}/{clientID}/{config.name_file_upload}"
    
    # Read the CSV file
    df = pd.read_csv(filepath)
    client_row_count = len(df)

    # Connect to the database
    conn = sqlite3.connect(config.database_file_path)
    cur = conn.cursor()

    # Get the row count from the database
    cur.execute("SELECT COUNT(*) FROM Trade_Transaction")
    db_row_count = cur.fetchone()[0]
    
    # Close the connection
    conn.close()

    # If the row counts don't match, re-upload and re-process the file
    if client_row_count != db_row_count:
        print(f"Row count mismatch: Client has {client_row_count} rows, database has {db_row_count} rows.")
        check_and_upload_file(clientID)
        transfer_to_database(clientID)
    else:
        print("Row count matches, no need to re-upload.")



# TODO Test function upload_transaction_to_db in mql5
def upload_transaction_to_db(transaction_data):
    """Upload a single transaction to the database."""
    
    conn = sqlite3.connect(config.database_file_path)
    cur = conn.cursor()

    cur.execute('''INSERT INTO Trade_Transaction (open_time, symbol, magic_number, type, volume, open_price, sl, tp, close_price, close_time, commission, swap, profit, profit_points, duration, open_comment, close_comment)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                   (transaction_data['Open Time'], transaction_data['Symbol'], transaction_data['Magic Number'], 
                    transaction_data['Type'], transaction_data['Volume'], transaction_data['Open Price'], 
                    transaction_data['S/L'], transaction_data['T/P'], transaction_data['Close Price'], 
                    transaction_data['Close Time'], transaction_data['Commission'], transaction_data['Swap'], 
                    transaction_data['Profit'], transaction_data['Profit Points'], transaction_data['Duration'], 
                    transaction_data['Open Comment'], transaction_data['Close Comment']))

    conn.commit()
    conn.close()

# Upload a single transaction (when a transaction is completed)
transaction_data = {
    'Open Time': '2025.01.08 08:08:15',
    'Symbol': 'BTCUSD.',
    'Magic Number': 11085,
    'Type': 'buy',
    'Volume': 0.01,
    'Open Price': 96501.4,
    'S/L': None,
    'T/P': None,
    'Close Price': 96491.3,
    'Close Time': '2025.01.08 08:10:04',
    'Commission': -0.78,
    'Swap': 0,
    'Profit': -0.1,
    'Profit Points': -1010,
    'Duration': '0:01:49',
    'Open Comment': 'Break EA 651',
    'Close Comment': ''
}




    
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
    transfer_to_database(1001)
    check_row_count(1001)
