from flask import Flask, render_template, request, abort, Response

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('')


@app.route('/api/<path:sub_api>', methods=['GET', 'POST'])
def api(sub_api):
    pass


if __name__ == '__main__':
    app.run()
