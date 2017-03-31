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

    def update_activity(self, id, data):
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

    def update_activity(self, id, data):
        self._client.update_activity(id, **data)


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

    def _init_cache(self):
        activities = self.get_all_activities()
        self._cache.update_activities(activities)

    def _update_cache(self):
        activities = self._cache.get_activities()
        timestamp = self._get_latest_timestamp(activities)
        new_activities = self._client.get_activities_after(timestamp)
        self._cache.update_activities(new_activities + activities)

    def get_activities(self):
        activities = self._cache.get_activities()
        if not self._cache.is_initialized():
            self._init_cache()
        else:
            self._update_cache()
        return self._cache.get_activities()

    def get_bikes(self):
        athlete = self._client.get_athlete()
        return athlete["bikes"]

    def _merge_activity(self, activity, data):
        for k, v in data.items():
            if k in activity:
                activity[k] = v

    def update_activity(self, id, data):
        self._client.update_activity(id, **data)
        activity = self._cache.get_activity(id)
        if activity is not None:
            self._merge_activity(activity, data)
            self._cache.update_activity(activity)


def get_repository(token):
    return CachedRepository(token, cache.get_cache())
