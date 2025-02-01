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


# 18

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
# ✅ Expose check_and_upload_file as API
@app.route("/check_file", methods=["GET"])
def check_and_upload_file():
    clientID = request.args.get("clientID")
    if not clientID:
        return jsonify({"error": "Missing clientID parameter"}), 400

    client_file_path = f"{config.load_file_upload}/{clientID}/{config.name_file_upload}"
    server_file_path = f"{config.load_file_upload}/{clientID}/{config.name_file_upload}"

    if os.path.exists(server_file_path):
        print(f"[INFO] File already exists on the server for client {clientID}.")
        return jsonify({"message": "File exists"}), 200
    else:
        print(f"[WARNING] File not found on server. Uploading for client {clientID}...")
        try:
            shutil.copy(client_file_path, server_file_path)
            print("[SUCCESS] File uploaded successfully.")
            return jsonify({"message": "File uploaded"}), 200
        except Exception as e:
            print(f"[ERROR] Failed to upload file: {e}")
            return jsonify({"error": f"Upload failed: {e}"}), 500




# TODO Test function transfer_to_database in mql5
# ✅ Expose transfer_to_database as API
@app.route("/transfer_to_database", methods=["POST"])
def transfer_to_database():
    clientID = request.form.get("clientID")
    if not clientID:
        return jsonify({"error": "Missing clientID parameter"}), 400

    filepath = f"{config.load_file_upload}/{clientID}/{config.name_file_upload}"
    if not os.path.exists(filepath):
        return jsonify({"error": f"File not found: {filepath}"}), 404

    print(f"[INFO] Starting database transfer for client {clientID}...")

    # Connect to SQLite database
    conn = sqlite3.connect(config.database_file_path)
    cur = conn.cursor()

    # Optimize performance settings
    cur.execute("PRAGMA synchronous = OFF;")  
    cur.execute("PRAGMA journal_mode = WAL;")  

    # Create table if not exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Trade_Transaction(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            close_comment TEXT,
            UNIQUE (open_time, symbol, magic_number, type, volume, open_price, close_price, close_time)
        );
    """)

    conn.commit()

    # Read CSV file
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

        if len(data_batch) >= batch_size:
            try:
                cur.executemany('''INSERT OR IGNORE INTO Trade_Transaction 
                    (open_time, symbol, magic_number, type, volume, open_price, sl, tp, close_price, close_time, 
                    commission, swap, profit, profit_points, duration, open_comment, close_comment)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data_batch)
                conn.commit()
                print(f"[INFO] Inserted {batch_size} rows (excluding duplicates).")
            except Exception as e:
                print(f"[ERROR] Failed to insert batch: {e}")
            data_batch = []  

    # Insert remaining data
    if data_batch:
        try:
            cur.executemany('''INSERT OR IGNORE INTO Trade_Transaction 
                (open_time, symbol, magic_number, type, volume, open_price, sl, tp, close_price, close_time, 
                commission, swap, profit, profit_points, duration, open_comment, close_comment)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data_batch)
            conn.commit()
            print(f"[INFO] Inserted final {len(data_batch)} rows (excluding duplicates).")
        except Exception as e:
            print(f"[ERROR] Failed to insert final batch: {e}")

    conn.close()
    print("[SUCCESS] Data transfer completed successfully.")
    return jsonify({"message": "Data transfer completed successfully"}), 200





    
# TODO Test function check_row_count in mql5
# ✅ Expose check_row_count as API
@app.route("/check_row_count", methods=["GET"])
def check_row_count():
    clientID = request.args.get("clientID")
    if not clientID:
        return jsonify({"error": "Missing clientID parameter"}), 400

    filepath = f"{config.load_file_upload}/{clientID}/{config.name_file_upload}"
    if not os.path.exists(filepath):
        return jsonify({"error": f"File not found: {filepath}"}), 404  

    # Read file row count
    df = pd.read_csv(filepath)
    client_row_count = len(df)

    # Get row count from database
    conn = sqlite3.connect(config.database_file_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM Trade_Transaction")
    db_row_count = cur.fetchone()[0]
    conn.close()

    if client_row_count != db_row_count:
        print(f"[WARNING] Row count mismatch: CSV={client_row_count}, DB={db_row_count}. Reprocessing...")
        transfer_to_database(clientID)  # Reprocess if mismatch
    else:
        print("[INFO] Row count matches. No reprocessing needed.")

    return jsonify({"client_row_count": client_row_count, "db_row_count": db_row_count, "match": client_row_count == db_row_count}), 200





# TODO Test function upload_transaction_to_db in mql5
# ✅ Expose upload_transaction_to_db as API
@app.route("/upload_transaction", methods=["POST"])
def upload_transaction_to_db():
    transaction_data = request.json
    if not transaction_data:
        return jsonify({"error": "Missing transaction data"}), 400

    conn = sqlite3.connect(config.database_file_path)
    cur = conn.cursor()

    cur.execute('''INSERT INTO Trade_Transaction 
        (open_time, symbol, magic_number, type, volume, open_price, sl, tp, close_price, close_time, commission, swap, profit, profit_points, duration, open_comment, close_comment)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
        (transaction_data['Open Time'], transaction_data['Symbol'], transaction_data['Magic Number'], 
         transaction_data['Type'], transaction_data['Volume'], transaction_data['Open Price'], 
         transaction_data['S/L'], transaction_data['T/P'], transaction_data['Close Price'], 
         transaction_data['Close Time'], transaction_data['Commission'], transaction_data['Swap'], 
         transaction_data['Profit'], transaction_data['Profit Points'], transaction_data['Duration'], 
         transaction_data['Open Comment'], transaction_data['Close Comment']))

    conn.commit()
    conn.close()
    return jsonify({"message": "Transaction uploaded successfully"}), 200




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
