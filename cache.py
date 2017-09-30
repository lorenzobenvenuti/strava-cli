import os
import os.path
import json
import config


class AbstractCache(object):

    def is_initialized(self):
        raise NotImplementedError

    def get_activities(self):
        raise NotImplementedError

    def update_activities(self, activities):
        raise NotImplementedError

    def update_activity(self, activity):
        raise NotImplementedError

    def get_activity(self, id):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError


class JsonCache(AbstractCache):

    def __init__(self, directory, file_name):
        self._dir = directory
        self._file = file_name
        self._cache = None

    def _cache_file(self):
        return os.path.join(self._dir, self._file)

    def is_initialized(self):
        if not os.path.exists(self._dir):
            return False
        if not os.path.exists(self._cache_file()):
            return False
        return True

    def _empty_cache(self):
        cache = {}
        cache['activities'] = []
        return cache

    def _load_cache_from_file(self):
        if not self.is_initialized():
            return self._empty_cache()
        with open(self._cache_file()) as json_data:
            return json.load(json_data)

    def _get_cache(self):
        if self._cache is None:
            self._cache = self._load_cache_from_file()
        return self._cache

    def _update_cache(self, cache):
        if not os.path.exists(self._dir):
            os.makedirs(self._dir)
        with open(os.path.join(self._dir, self._file), 'w') as outfile:
            json.dump(cache, outfile)

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

    def get_activity(self, id):
        return next((a for a in self.get_activities() if a['id'] == id), None)

    def clear(self):
        cache_file = os.path.join(self._dir, self._file)
        if os.path.exists(cache_file):
            os.remove(cache_file)
        self._cache = {}


def get_cache():
    return JsonCache(config.get_strava_cli_dir(), 'activities.json')
