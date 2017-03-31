import api
import json
import time
from util import parse_date
import cache


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

    def __init__(self, token, cache):
        self._client = api.Client(token)
        self._cache = cache

    def get_all_activities(self):
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

    def _get_latest_timestamp(self, activities):
        if not activities:
            return 0
        max_date = max([parse_date(a['start_date_local']) for a in activities])
        return time.mktime(max_date.timetuple())

    def get_activities(self):
        cache = self._cache.load()
        if cache is None:
            cache = {}
            cache["activities"] = self.get_all_activities()
        else:
            timestamp = self._get_latest_timestamp(cache["activities"])
            new_activities = self._client.get_activities_after(timestamp)
            cache["activities"] = new_activities + cache["activities"]
        self._cache.update(cache)
        return cache['activities']

    def get_bikes(self):
        athlete = self._client.get_athlete()
        return athlete["bikes"]


def get_repository(token):
    return CachedRepository(token, cache.get_cache())
