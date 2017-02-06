import requests

class Client(object):

    def __init__(self, token):
        self._token = token

    def _perform_request(self, url):
        r = requests.get(url, headers={ "Authorization": "Bearer {}".format(self._token) })
        if r.status_code != 200:
            raise StandardError()
        return r.json()

    def get_activities(self, page, per_page):
        return self._perform_request("https://www.strava.com/api/v3/athlete/activities?page={}&per_page={}".format(page, per_page))

    def get_athlete(self):
        return self._perform_request("https://www.strava.com/api/v3/athlete")
