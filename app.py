from flask import Flask, render_template, request, abort, Response

from api import numbers_api

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/<path:sub_api>', methods=['GET', 'POST'])
def api(sub_api):
    if sub_api == 'numbers':
        try:
            return render_template('index.html', fact=numbers_api(request.args))
        except IOError:
            abort(Response("Bad Request Exception: Missing number parameter", status=400))


if __name__ == '__main__':
    app.run()
