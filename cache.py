import os
import os.path
import json


class AbstractCache(object):

    def load(self):
        raise NotImplementedError

    def update(self, values):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError


class JsonCache(AbstractCache):

    def __init__(self, directory, file_name):
        self._dir = directory
        self._file = file_name

    def load(self):
        if not os.path.exists(self._dir):
            return None
        cache_file = os.path.join(self._dir, self._file)
        if not os.path.exists(cache_file):
            return None
        with open(cache_file) as json_data:
            return json.load(json_data)

    def update(self, values):
        if not os.path.exists(self._dir):
            os.makedirs(self._dir)
        with open(os.path.join(self._dir, self._file), 'w') as outfile:
            json.dump(values, outfile)

    def clear(self):
        cache_file = os.path.join(self._dir, self._file)
        if os.path.exists(cache_file):
            os.remove(cache_file)


def get_cache():
    return JsonCache(os.path.join(os.path.expanduser('~'), ".strava-cli"),
                     'activities.json')
