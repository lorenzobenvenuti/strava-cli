import requests
import os.path
import os
import api
import json

class AbstractRepository(object):

    def get_activities(self):
        raise NotImplementedError()

    def update_activity(self, id, values):
        raise NotImplementedError()

    def get_bikes(self):
        raise NotImplementedError()

class ApiRepository(AbstractRepository):

    page_size = 30

    def __init__(self, token):
        self._client = api.Client(token)

    def get_activities(self):
        all_activities = []
        page = 1
        while True:
            activities = self._client.get_activities(page, ApiRepository.page_size)
            all_activities.extend(activities)
            num = len(activities)
            if num < ApiRepository.page_size or num == 0:
                break
            page += 1
        return all_activities

    def get_bikes(self):
        athlete = self._client.get_athlete()
        return athlete["bikes"]

class CachedRepository(AbstractRepository):

    def __init__(self, delegate):
        self._delegate = delegate

    def _get_empty_cache(self):
        return { 'activities': None, 'bikes': None }

    def _get_cache(self):
        cache_dir = os.path.join(os.path.expanduser('~'), ".strava-cli")
        if not os.path.exists(cache_dir):
            return self._get_empty_cache()
        cache_file = os.path.join(cache_dir, "cache.json")
        if not os.path.exists(cache_file):
            return self._get_empty_cache()
        with open(cache_file) as json_data:
            return json.load(json_data)

    def _save_cache(self, cache):
        cache_dir = os.path.join(os.path.expanduser('~'), ".strava-cli")
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        with open(os.path.join(cache_dir, 'cache.json'), 'w') as outfile:
            json.dump(cache, outfile)

    def get_activities(self):
        cache = self._get_cache()
        if cache["activities"] == None:
            cache["activities"] = self._delegate.get_activities()
            self._save_cache(cache)
        return cache["activities"]

    def get_bikes(self):
        cache = self._get_cache()
        if cache["bikes"] == None:
            cache["bikes"] = self._delegate.get_bikes()
            self._save_cache(cache)
        return cache["bikes"]
