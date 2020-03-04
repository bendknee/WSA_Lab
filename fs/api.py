import requests as r


# Infralabs' OAuth
def authorized(bearer_token):
    url = "http://oauth.infralabs.cs.ui.ac.id/oauth/resource"

    headers = {
        'Authorization': bearer_token,
        'Cache-Control': "no-cache",
        'Connection': "keep-alive",
    }

    response = r.get(url=url, headers=headers)
    if response.status_code == 200:
        return True

    return False
