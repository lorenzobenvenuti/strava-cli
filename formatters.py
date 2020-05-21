import json
import gpxpy
import datetime


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
            output += '{}\t'.format(activity.get(key, ''))
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


class GpxFormatter(Formatter):

    def format(self, activity, gps):
        gpx = gpxpy.gpx.GPX()

        gpx_track = gpxpy.gpx.GPXTrack(
            name=activity.get('name'))
        gpx_track.type = activity.get('type')
        gpx_track.comment = str(activity.get('id')) #extensions are better for this, but gpxpy doesn't support extensions
        gpx.tracks.append(gpx_track)

        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)


        for time, point, altitude in gps:
            time = datetime.datetime.fromtimestamp(time)
            gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(latitude=point[0], longitude=point[1], elevation=altitude, time=time))
            
        return gpx.to_xml(prettyprint=True)


class JsonGpsFormatter(Formatter):

    def format(self, activity, gps):
        return json.dumps({'activity':activity, 'data':list(gps)})


def get_formatter(json_output = False, quiet = False, verbose = False):
    return JsonFormatter(quiet, verbose) if json_output else DefaultFormatter(quiet, verbose)

def get_formatter_details(json_output = False, quiet = False, verbose = False):
    return JsonFormatter(quiet, verbose) if json_output else DetailFormatter(quiet, verbose)

def get_formatter_gps(json_output = False, quiet = False, verbose = False):
    return JsonGpsFormatter(quiet, verbose) if json_output else GpxFormatter(quiet, verbose)

