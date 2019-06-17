from flask import Flask, request
app = Flask(__name__)


@app.route('/')
def index():
    data = request.args.to_dict()
    if 'name' in data.keys():
        return f"<h1>Hello {data['name']}!</h1>"
    return '<h1>Hello World!</h1>'
