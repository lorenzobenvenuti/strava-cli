import api
import json
from util import parse_date
import cache
import logging


#unused
class ApiRepository:

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

    def get_shoes(self):
        athlete = self._client.get_athlete()
        return athlete["shoes"]

    def update_activity(self, id, data):
        self._client.update_activity(id, **data)


class CachedRepository:

    page_size = 30

    def __init__(self, token, cache, update_cache = True):
        self._client = api.Client(token)
        self._cache = cache
        self._run_update_cache = update_cache

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
        max_date = max([parse_date(a['start_date']) for a in activities])
        return int(max_date.timestamp())

    def _init_cache(self):
        logging.getLogger('CachedRepository').debug("Initializing cache")
        activities = self.get_all_activities()
        self._cache.update_activities(activities)

    def _update_cache(self):
        if not self._cache.is_initialized():
            self._init_cache()
            return
        if not self._run_update_cache:
            return
        activities = self._cache.get_activities()
        timestamp = self._get_latest_timestamp(activities)
        logging.getLogger('CachedRepository').debug(
                            "Newest activity in cache {}".format(timestamp))
        new_activities = []
        page = 1
        per_page = 30
        while True:
            logging.getLogger('CachedRepository').info(
                    "Loading page {} of {} elements".format(page, per_page))
            curr_activities = self._client.get_activities_after(
                                                timestamp, page, per_page)
            logging.getLogger('CachedRepository').debug(
                    "{} activities loaded".format(len(curr_activities)))
            page += 1
            new_activities.extend(curr_activities)
            if len(curr_activities) < per_page:
                logging.getLogger('CachedRepository').debug(
                                            "No more activities to load")
                break
        new_activities.reverse()
        self._cache.update_activities(new_activities + activities)

    def get_activities(self):
        self._update_cache()
        return self._cache.get_activities()

    def get_activity(self, id):
        self._update_cache()
        return self._cache.get_activity(id)

    def get_activity_detail(self, id):
        activity_detail = self._cache.get_activity_detail(id)
        if activity_detail is None:
            activity_detail = self._client.get_activity_detail(id)
            self._cache.update_activity_detail(activity_detail)
        return activity_detail

    def get_gps(self, id):
        streams = self._client.get_streams(id)
        activity = self.get_activity(int(id))
        start_time = int(parse_date(activity['start_date']).timestamp())
        streams = zip(*(streams[key]['data'] for key in ('time', 'latlng', 'altitude')))
        return activity, [(time + start_time, point, altitude) for time, point, altitude in streams]

    def get_bikes(self):
        athlete = self._client.get_athlete()
        return athlete["bikes"]

    def get_shoes(self):
        athlete = self._client.get_athlete()
        return athlete["shoes"]

    def _merge_activity(self, activity, data):
        for k, v in data.items():
            if k in activity:
                activity[k] = v

    def update_activity(self, id, data):
        logging.getLogger('CachedRepository').info(
                    "Updating activity {} with data {}".format(id, data))
        self._client.update_activity(id, **data)
        activity = self._cache.get_activity(id)
        if activity is not None:
            self._merge_activity(activity, data)
            self._cache.update_activity(activity)


def get_repository(token, update_cache = True):
    return CachedRepository(token, cache.get_cache(), update_cache)
