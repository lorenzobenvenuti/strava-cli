import os
import os.path
import json
import config
import tempfile


class AbstractCache(object):

    def is_initialized(self):
        raise NotImplementedError

    def get_activities(self):
        raise NotImplementedError

    def update_activities(self, activities):
        raise NotImplementedError

    def get_activity(self, id):
        return next((activity for activity in self.get_activities() if activity['id'] == id), None)

    def update_activity_detail(self, activity_detail):
        raise NotImplementedError

    def get_activity_detail(self, id):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError


class JsonCache(AbstractCache):

    def __init__(self, directory, file_name):
        self._dir = directory
        self._file = os.path.join(directory, file_name)
        self._cache = None

    def _cache_file(self):
        return self._file

    def is_initialized(self):
        return os.path.exists(self._cache_file())

    def _load_cache_from_file(self):
        if not self.is_initialized():
            return {}
        with open(self._cache_file()) as json_data:
            return json.load(json_data)

    def _get_cache(self):
        if self._cache is None:
            self._cache = self._load_cache_from_file()
        self._cache.setdefault('activities', [])
        self._cache.setdefault('activity_details', {})
        return self._cache

    def _update_cache(self, cache):
        if not os.path.exists(self._dir):
            os.makedirs(self._dir)
        with tempfile.NamedTemporaryFile(dir=self._dir, mode='w') as outfile:
            json.dump(cache, outfile)
            #minor race case
            if self.is_initialized():
                os.remove(self._cache_file())
            os.link(outfile.name, self._cache_file())

    def get_activities(self):
        return self._get_cache()['activities']

    def update_activities(self, activities):
        cache = self._get_cache()
        cache['activities'] = activities
        self._update_cache(cache)

    def update_activity(self, activity):
        a = self.get_activity(activity['id'])
        if a is not None:
            for k, v in activity.items():
                a[k] = v
        self._update_cache(self._get_cache())

    def update_activity_detail(self, activity_detail):
        cache = self._get_cache()
        cache['activity_details'][activity_detail['id']] = activity_detail
        self._update_cache(cache)

    def get_activity_detail(self, id):
        return self._get_cache()['activity_details'].get(str(id))

    def clear(self):
        cache_file = self._cache_file()
        if os.path.exists(cache_file):
            os.remove(cache_file)
        self._cache = {}


def get_cache():
    return JsonCache(config.get_strava_cli_dir(), 'activities.json')
