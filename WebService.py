from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods = ['GET'])
def search():
    name = request.args.get('name')
    if name and name != '':
        message = request.args.get('message')
        return f"Hello {name}! {message}"

if __name__ == '__main__':
    app.run(debug = True)