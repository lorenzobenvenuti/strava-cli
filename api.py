import logging
import requests
import sys
import time


class Client(object):

    def __init__(self, token, sleep_time = None):
        self._token = token
        self._sleep_time = sleep_time

    def _get_headers(self):
        return {"Authorization": "Bearer {}".format(self._token)}

    def _get(self, url):
        logging.getLogger('Client').debug('http get {}'.format(url))
        r = requests.get(url, headers=self._get_headers())
        self._sleep()
        if r.status_code != 200:
            raise ValueError(r.text)
        return r.json()

    def _put(self, url, data):
        r = requests.put(url, data, headers=self._get_headers())
        self._sleep()
        if r.status_code != 200:
            raise ValueError()

    def update_activity(self, id, **kwargs):
        self._put("https://www.strava.com/api/v3/activities/{}".format(id),
                  dict(kwargs))

    def get_activities_page(self, page, per_page):
        return self._get(
            "https://www.strava.com/api/v3/athlete/activities" +
            "?page={}&per_page={}".format(page, per_page))

    def get_activities_after(self, seconds_from_epoch, page, per_page):
        activities = self._get(
            "https://www.strava.com/api/v3/athlete/activities" +
            "?after={}&page={}&per_page={}".format(
                                        seconds_from_epoch, page, per_page))
        return activities

    def get_activity_detail(self, id):
        return self._get(
            "https://www.strava.com/api/v3/activities/{}".format(id))

    def get_streams(self, id, stream_types):
        return self._get(
            "https://www.strava.com/api/v3/activities/{}/streams?keys={}&key_by_type=true".format(id, ','.join(stream_types)))

    def get_athlete(self):
        return self._get("https://www.strava.com/api/v3/athlete")
    
    def _sleep(self):
        #used because of throttling strava api
        if self._sleep_time is not None and self._sleep_time != 0:
            logging.getLogger('Client').info('sleep {}'.format(self._sleep_time))
            time.sleep(self._sleep_time)

