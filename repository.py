import os.path
import os
import api
import json
import time


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
            activities = self._client.get_activities_page(
                page, ApiRepository.page_size)
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

    page_size = 30

    def __init__(self, token):
        self._client = api.Client(token)

    def _get_cache(self):
        cache_dir = os.path.join(os.path.expanduser('~'), ".strava-cli")
        if not os.path.exists(cache_dir):
            return None
        cache_file = os.path.join(cache_dir, "activities.json")
        if not os.path.exists(cache_file):
            return None
        with open(cache_file) as json_data:
            return json.load(json_data)

    def _save_cache(self, cache):
        cache_dir = os.path.join(os.path.expanduser('~'), ".strava-cli")
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        with open(os.path.join(cache_dir, 'activities.json'), 'w') as outfile:
            json.dump(cache, outfile)

    def get_all_activities(self, client):
        all_activities = []
        page = 1
        num = CachedRepository.page_size
        while num == CachedRepository.page_size:
            activities = self._client.get_activities_page(
                page, CachedRepository.page_size)
            all_activities.extend(activities)
            num = len(activities)
            page += 1
        return all_activities

    def get_activities(self):
        cache = self._get_cache()
        now = int(time.time())
        if cache is None:
            cache = {}
            cache["activities"] = self.get_all_activities(client)
        else:
            new_activities = self._client.get_activities_after(now)
            cache["activities"] = new_activities + cache["activities"]
        cache["timestamp"] = now
        self._save_cache(cache)
        return cache['activities']

    def get_bikes(self):
        athlete = self._client.get_athlete()
        return athlete["bikes"]


def get_repository(token):
    return CachedRepository(token)
