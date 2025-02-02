import os
import shutil
import csv
import sqlite3
import pandas as pd
import config
from flask import Flask, flash, request, jsonify, Response, redirect, url_for, session, abort
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user 
from werkzeug.utils import secure_filename


app = Flask(__name__)
UPLOAD_FOLDER = config.load_file_upload
ALLOWED_EXTENSIONS = config.allowed_extensions
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# 29

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







# TODO Test function check_row_count in mql5
# ✅ Expose check_row_count as API
def check_row_count(clientID):
    pass


def allowed_file(filename):
    """Check if file has allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in config.allowed_extensions

# Function to check if the file exists
def file_exists(client_id):
    file_path = os.path.join(config.UPLOAD_DIR, client_id, config.CSV_FILENAME)
    return os.path.exists(file_path)

# TODO Test function check_and_upload_file in mql5
# ✅ Expose check_and_upload_file as API
@app.route("/check_file", methods=["POST"])
def check_and_upload():
    client_id = request.form.get("clientID")
    if not client_id:
        return jsonify({"error": "Missing clientID"}), 400

    client_folder = os.path.join(config.UPLOAD_DIR, client_id)
    os.makedirs(client_folder, exist_ok=True)  # Create folder if not exists

    # Check if file exists
    if file_exists(client_id):
        return jsonify({"message": "File already exists"}), 200

    # Check if file is provided
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    # Validate file type
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    # Save file
    file.save(os.path.join(client_folder, config.CSV_FILENAME))
    return jsonify({"message": "File uploaded successfully"}), 201
    






# TODO Test function transfer_to_database in mql5
# ✅ Expose transfer_to_database as API
def transfer_to_database(clientID):
    pass




    







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
