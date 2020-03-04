from flask import Flask, render_template

UPLOAD_DIR = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('')


if __name__ == '__main__':
    app.run()
