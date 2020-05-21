import json


class Formatter(object):

    def __init__(self, quiet = False, verbose = False):
        self._quiet = quiet
        self._verbose = verbose

    def get_keys(self):
        if self._quiet:
            return ('id',)
        elif self._verbose:
            return ('id', 'external_id', 'upload_id', 'athlete', 'name',
                    'distance', 'moving_time', 'elapsed_time',
                    'total_elevation_gain', 'elev_high', 'elev_low', 'type',
                    'start_date', 'start_date_local', 'timezone', 'start_latlng',
                    'end_latlng', 'achievement_count', 'kudos_count', 'comment_count',
                    'athlete_count', 'photo_count', 'total_photo_count', 'map', 'trainer',
                    'commute', 'manual', 'private', 'flagged', 'workout_type',
                    'upload_id_str', 'average_speed', 'max_speed', 'has_kudoed',
                    'gear_id', 'kilojoules', 'average_watts', 'device_watts', 'max_watts',
                    'weighted_average_watts')
        else:
            return ('id', 'type', 'start_date_local', 'name',
                    'moving_time', 'distance', 'total_elevation_gain')
    
    def format(self, activity):
        raise NotImplementedError()


class DefaultFormatter(Formatter):

    def format(self, activity):
        output = ''
        for key in self.get_keys():
            output += '{}\t'.format(activity[key] if key in activity else '')
        return output

class DetailFormatter(Formatter):

    def format(self, activity):
        output = '{}\n'.format(activity['id'])
        for key in self.get_keys():
            if key != 'id' and key in activity:
                output += '{:>20}: {}'.format(key.replace('_', ' '), activity[key]) + '\n'
        return output

class JsonFormatter(Formatter):

    def format(self, activity):
        return json.dumps({k: activity[k] for k in self.get_keys() if k in activity})


def get_formatter(json_output = False, quiet = False, verbose = False):
    return JsonFormatter(quiet, verbose) if json_output else DefaultFormatter(quiet, verbose)

def get_formatter_details(json_output = False, quiet = False, verbose = False):
    return JsonFormatter(quiet, verbose) if json_output else DetailFormatter(quiet, verbose)

