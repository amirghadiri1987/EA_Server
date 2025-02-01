from flask import Flask, flash, request, jsonify, Response, redirect, url_for, session, abort
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user 
from werkzeug.utils import secure_filename
import os
import shutil
import sqlite3
import pandas as pd
import config

app = Flask(__name__)
UPLOAD_FOLDER = config.load_file_upload
ALLOWED_EXTENSIONS = config.allowed_extensions
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# 12

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# config
app.config.update(
    SECRET_KEY = config.SECRET_KEY
)
# silly user model
class User(UserMixin):

    def __init__(self, id):
        self.id = id
        
        
    def __repr__(self):
        return "%d" % (self.id)


# create some users with ids 1 to 20       
user = User(0)


# some protected url
@app.route('/')
@login_required
def home():
    return Response("Hello World!")


# somewhere to login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST': #TODO: stop the brute force
        username = request.form['username']
        password = request.form['password']        
        if password == config.PASSWORD and username == config.USERNAME:
            login_user(user)
            return redirect('/') 
        else:
            return abort(401)
    else:
        return Response('''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=password name=password>
            <p><input type=submit value=Login>
        </form>
        ''')


# somewhere to logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return Response('<p>Logged out</p>')


# handle login failed
@app.errorhandler(401)
def page_not_found(error):
    return Response('<p>Login failed</p>')
    
    
# callback to reload the user object        
@login_manager.user_loader
def load_user(userid):
    return User(userid)














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
    """Ensure the transaction file exists on the server; upload if missing."""
    
    client_file_path = f"{config.load_file_upload}/{clientID}/{config.name_file_upload}"
    server_file_path = f"{config.load_file_upload}/{clientID}/{config.name_file_upload}"

    if os.path.exists(server_file_path):
        print(f"[INFO] File already exists on the server for client {clientID}.")
        return True  # File exists
    else:
        print(f"[WARNING] File not found on server. Uploading for client {clientID}...")
        try:
            shutil.copy(client_file_path, server_file_path)
            print("[SUCCESS] File uploaded successfully.")
            return True  # File uploaded
        except Exception as e:
            print(f"[ERROR] Failed to upload file: {e}")
            return False  # Upload failed




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
    check_and_upload_file(1001)
    app.run(debug=True, host='0.0.0.0', port=5000)
