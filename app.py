from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
	
# @app.route("/check")
# def check_File():
# 	pass

# def upload_file():
# 	pass

# de upload_data():
# 	pass


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
