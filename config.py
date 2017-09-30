import os.path


def get_strava_cli_dir():
    return os.path.join(os.path.expanduser('~'), ".strava-cli")
