import requests as r


def numbers_api(request):
    params = dict()
    header = {"Content-Type": "application/json"}

    if "number" not in request:
        raise r.RequestException()
    if "type" in request:
        params["type"] = request["type"]
    if "notfound" in request:
        params["notfound"] = request["notfound"]

    resp = r.get(
        url="http://numbersapi.com/" + request["number"],
        params=params,
        headers=header,
    )

    return resp.json()

