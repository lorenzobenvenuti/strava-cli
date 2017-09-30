import os.path
import json


class JsonStore(object):

    def __init__(self, directory, file_name):
        self._dir = directory
        self._file = file_name
        self._store = None

    def _store_file(self):
        return os.path.join(self._dir, self._file)

    def is_initialized(self):
        if not os.path.exists(self._dir):
            return False
        if not os.path.exists(self._store_file()):
            return False
        return True

    def _load_store_from_file(self):
        if not self.is_initialized():
            return {}
        with open(self._store_file()) as json_data:
            return json.load(json_data)

    def _get_store(self):
        if self._store is None:
            self._store = self._load_store_from_file()
        return self._store

    def get(self, key):
        return self._get_store().get(key, None)

    def set(self, key, value):
        data = self._get_store()
        data[key] = value
        if not os.path.exists(self._dir):
            os.makedirs(self._dir)
        with open(os.path.join(self._dir, self._file), 'w') as outfile:
            json.dump(data, outfile)

    def clear(self):
        store_file = os.path.join(self._dir, self._file)
        if os.path.exists(store_file):
            os.remove(store_file)
        self._store = {}
