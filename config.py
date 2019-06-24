import os
import os.path


def get_strava_cli_dir():
    return os.path.join(os.path.expanduser('~'), ".strava-cli")


def get_or_create_strava_cli_dir():
    dir = get_strava_cli_dir()
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir


def get_log_file():
    return os.path.join(get_or_create_strava_cli_dir(), 'strava-cli.log')
