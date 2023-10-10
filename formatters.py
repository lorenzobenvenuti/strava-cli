import json
import gpxpy
import datetime
import xml.etree.ElementTree as ElementTree


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

    def format(self, activity, stream_types, gps):
        gpx = gpxpy.gpx.GPX()
        
        self.setup_extensions(gpx, stream_types)

        gpx_track = gpxpy.gpx.GPXTrack(
            name=activity.get('name'))
        gpx_track.type = activity.get('type')
        gpx_track.comment = str(activity.get('id')) #extensions are better for this, but gpxpy doesn't support extensions
        gpx.tracks.append(gpx_track)

        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)


        for entry in gps:
            time = datetime.datetime.fromtimestamp(entry['time']).astimezone(datetime.timezone.utc) if 'time' in entry else None
            point = entry['latlng'] if 'latlng' in entry else [None, None]
            altitude = entry['altitude'] if 'altitude' in entry else None
            
            point = gpxpy.gpx.GPXTrackPoint(latitude=point[0], longitude=point[1], elevation=altitude, time=time)
            gpx_segment.points.append(point)
            
            main_extension = ElementTree.Element('gpxtpx:TrackPointExtension')
            
            if 'gpxtpx' in gpx.nsmap:
                if 'temp' in entry:
                    temperature = ElementTree.SubElement(main_extension, 'gpxtpx:atemp')
                    temperature.text = str(entry['temp'])
                
                if 'heartrate' in entry:
                    heart_rate = ElementTree.SubElement(main_extension, 'gpxtpx:hr')
                    heart_rate.text = str(entry['heartrate'])
                
                if 'cadence' in entry:
                    cadence = ElementTree.SubElement(main_extension, 'gpxtpx:cad')
                    cadence.text = str(entry['cadence'])
                
                if 'velocity_smooth' in entry:
                    speed = ElementTree.SubElement(main_extension, 'gpxtpx:speed')
                    speed.text = str(entry['velocity_smooth'])
                
                if len(main_extension) > 0:
                    point.extensions.append(main_extension)
            
            if 'gpxpx' in gpx.nsmap and 'watts' in entry:
                power = ElementTree.Element('gpxpx:PowerInWatts')
                power.text = str(round(entry['watts']))
                point.extensions.append(power)
        
        return gpx.to_xml(prettyprint=True)

    def setup_extensions(self, gpx, stream_types):
        if 'heartrate' in stream_types or 'cadence' in stream_types or 'temp' in stream_types or 'velocity_smooth' in stream_types:
            # https://www8.garmin.com/xmlschemas/TrackPointExtensionv2.xsd
            gpx.nsmap['gpxtpx'] = 'http://www.garmin.com/xmlschemas/TrackPointExtension/v2'
            ElementTree.register_namespace('gpxtpx', 'http://www.garmin.com/xmlschemas/TrackPointExtension/v2')
        
        if 'watts' in stream_types:
            # https://www8.garmin.com/xmlschemas/PowerExtensionv1.xsd
            gpx.nsmap['gpxpx'] = 'http://www.garmin.com/xmlschemas/PowerExtension/v1'
            ElementTree.register_namespace('gpxpx', 'http://www.garmin.com/xmlschemas/PowerExtension/v1')


class JsonGpsFormatter(Formatter):

    def format(self, activity, stream_types, gps):
        return json.dumps({'activity':activity, 'data':list(gps)})


def get_formatter(json_output = False, quiet = False, verbose = False, utc = False):
    return JsonFormatter(quiet, verbose, utc) if json_output else DefaultFormatter(quiet, verbose, utc)

def get_formatter_details(json_output = False, quiet = False, verbose = False, utc = False):
    return JsonFormatter(quiet, verbose, utc) if json_output else DetailFormatter(quiet, verbose, utc)

def get_formatter_gps(json_output = False):
    return JsonGpsFormatter() if json_output else GpxFormatter()

