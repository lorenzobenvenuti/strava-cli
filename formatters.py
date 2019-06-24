import json


class Formatter(object):

    def format(self, activity):
        raise NotImplementedError()


class QuietFormatter(Formatter):

    def format(self, activity):
        return activity['id']


class DefaultFormatter(Formatter):

    def format(self, activity):
        return u"{id}\t{type}\t{start_date_local}\t{name}\t{moving_time}\t{distance}\t{total_elevation_gain}"\
                .format(**activity)


class JsonFormatter(Formatter):

    def __init__(self, quiet):
        self._quiet = quiet

    def format(self, activity):
        if self._quiet:
            keys = ('id',)
        else:
            keys = ('id', 'type', 'start_date_local', 'name',
                    'moving_time', 'distance', 'total_elevation_gain')
        return json.dumps({k: activity[k] for k in keys})


def get_formatter(quiet, json_output):
    if json_output:
        return JsonFormatter(quiet)
    if quiet:
        return QuietFormatter()
    return DefaultFormatter()
