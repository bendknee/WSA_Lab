import uuid

from flask import Flask, render_template, request, redirect, url_for, json

from utils.broker import BrokerUtils, MODE_DIRECT, CHANNEL_DOWNLOAD

FORM_SIZE = 10

app = Flask(__name__)


@app.route('/')
def index():
    return redirect(url_for("form"))


@app.route('/form')
def form():
    return render_template('form.html')


@app.route('/execute', methods=['POST'])
def place_order():
    if len(request.form) != FORM_SIZE:
        return redirect(url_for("form"))

    broker = BrokerUtils(MODE_DIRECT)
    process_id = str(uuid.uuid4())

    for i in range(FORM_SIZE):
        url = request.form.get("link-{:d}".format(i)).rstrip('/')
        payload = {'process_id': process_id, 'url': url}
        broker.send(json.dumps(payload), CHANNEL_DOWNLOAD)

    payload = {'process_id': process_id, 'host_ip': request.host_url, 'client_ip': request.remote_addr}
    broker.send(json.dumps(payload), CHANNEL_DOWNLOAD)
    return redirect(url_for("progress", process_id=process_id))


@app.route('/progress/<uuid:process_id>')
def progress(process_id):
    return render_template('progress.html', route=process_id)


if __name__ == '__main__':
    app.run()
