from flask import Flask, request, Response

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return Response(str(float(request.args["x"]) * float(request.args["y"])), status=200)


if __name__ == '__main__':
    app.run()
