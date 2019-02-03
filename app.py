from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route("/results/<name>")
def results(name):
    return name

if __name__ == '__main__':
    app.run()
