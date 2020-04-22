import logging

from flask import Flask, request, Response
from logstash_async.formatter import FlaskLogstashFormatter
from logstash_async.handler import AsynchronousLogstashHandler

logstash = logging.getLogger("logstash")
logstash.setLevel(logging.DEBUG)

async_handler = AsynchronousLogstashHandler(
    host='1a4e6d42-11d0-4a3b-a7dd-98e5d495200a-ls.logit.io',
    port=17785,
    ssl_enable=True,
    ssl_verify=False,
    database_path='')

formatter = FlaskLogstashFormatter()
async_handler.setFormatter(formatter)

logstash.addHandler(async_handler)

app = Flask(__name__)
app.logger.addHandler(async_handler)

dp = [0, 1]


@app.route('/')
def index():
    logstash.warning("Placeholder index, call /fibo?n=<int> instead")
    return Response("Placeholder index, call /fibo?n=<int> instead", 400)


@app.route('/fibo/', methods=['GET'])
def fibonacci():
    try:
        n = int(request.args["n"])
    except ValueError:
        logstash.error("{:s} is not an integer".format(request.args["n"]), exc_info=1)
        return Response("{:s} is not an integer".format(request.args["n"]), 400)

    if n < 0:
        logstash.error("{:d} is a negative integer".format(n), n)
        return Response("{:d} is a negative integer".format(n), 400)

    logstash.info("Execute fibonacci for n = {:d}".format(n))
    fibs(n)
    logstash.debug("Fibonacci sequence up to no. {:d} is {:s}".format(n, str(dp[:n+1])))
    return Response(str(dp[:n+1]), 200)


def fibs(n):
    global dp
    if len(dp) >= n+1:
        logstash.debug("Found sequence no. {:d} in DP table = {:d}".format(n, dp[n]))
        return dp[n]

    logstash.info("Execute fibonacci for n = {:d}-1".format(n))
    fibs(n-1)
    logstash.info("Execute fibonacci for n = {:d}-2".format(n))
    fibs(n-2)

    logstash.debug("Save to fibonacci table no. {:d} = {:d} + {:d}".format(n, dp[n-1], dp[n-2]))
    dp.insert(n, dp[n-1] + dp[n-2])


if __name__ == '__main__':
    app.run()
