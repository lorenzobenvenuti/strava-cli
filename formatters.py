import json
import gpxpy
import datetime


class Formatter(object):

    def __init__(self, quiet = False, verbose = False, utc = False):
        self._quiet = quiet
        self._verbose = verbose
        self._utc = utc

    def _get_keys(self, activity):
        if self._quiet:
            return ('id',)
        elif self._verbose:
            return sorted(activity.keys())
        else:
            return ('id', 'type', 'start_date' if self._utc else 'start_date_local', 'name',
                    'moving_time', 'distance', 'total_elevation_gain')
    
    def format(self, activity):
        raise NotImplementedError()


class DefaultFormatter(Formatter):

    def format(self, activity):
        output = ''
        for key in self._get_keys(activity):
            output_value = activity.get(key, '')
            if key == 'start_date_local':
                output_value = output_value.replace('Z','') #Z is incorrect here
            output += '{}\t'.format(output_value)
        return output

class DetailFormatter(Formatter):

    def format(self, activity):
        output = '{}\n'.format(activity['id'])
        for key in self._get_keys(activity):
            if key != 'id' and key in activity:
                output_value = activity[key]
                if key == 'start_date_local':
                    output_value = output_value.replace('Z','') #Z is incorrect here
                output += '{:>20}: {}'.format(key.replace('_', ' '), output_value) + '\n'
        return output

class JsonFormatter(Formatter):

    def format(self, activity):
        return json.dumps({k: activity[k] for k in self._get_keys(activity) if k in activity})


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


def get_formatter(json_output = False, quiet = False, verbose = False, utc = False):
    return JsonFormatter(quiet, verbose, utc) if json_output else DefaultFormatter(quiet, verbose, utc)

def get_formatter_details(json_output = False, quiet = False, verbose = False, utc = False):
    return JsonFormatter(quiet, verbose, utc) if json_output else DetailFormatter(quiet, verbose, utc)

def get_formatter_gps(json_output = False):
    return JsonGpsFormatter() if json_output else GpxFormatter()

