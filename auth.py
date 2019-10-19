import os.path
import config
import json
import util
from flask import Flask, redirect, request, abort
import requests
import logging
import time


class HomeAuthStore:

    def __init__(self, dir, filename):
        self._dir = dir
        self._filename = os.path.join(dir, filename)

    @property
    def _full_path(self):
        return os.path.join(self._filename)

    def load_auth(self):
        if not os.path.exists(self._full_path):
            return None
        with open(self._full_path, 'r') as infile:
            return json.load(infile)

    def save_auth(self, auth):
        if not os.path.exists(self._dir):
            os.makedirs(self._dir)
        with open(self._full_path, 'w') as outfile:
            json.dump(auth, outfile)


class Authorizer:

    AUTH_URL_TEMPLATE = 'https://www.strava.com/oauth/authorize?client_id={}'\
        '&response_type=code&redirect_uri=http://localhost:{}/token'\
        '&scope=activity:read_all,activity:write'

    TOKEN_URL = 'https://www.strava.com/oauth/token'

    KEYS = ('expires_at', 'refresh_token', 'access_token')

    def __init__(self, port, store=HomeAuthStore(
                                config.get_strava_cli_dir(), "auth.json")):
        self._port = port
        self._store = store

    def index(self):
        return redirect(Authorizer.AUTH_URL_TEMPLATE.format(
                            self._client_id, self._port), 302)

    def get_token(self):
        if 'error' in request.args:
            return abort(401)
        if 'code' in request.args:
            response = requests.post(Authorizer.TOKEN_URL, data={
                'client_id': self._client_id,
                'client_secret': self._client_secret,
                'code': request.args['code'],
                'grant_type': 'authorization_code'
            })
            d = response.json()
            if 'access_token' in d:
                auth = {k: d[k] for k in Authorizer.KEYS}
                auth['client_id'] = self._client_id
                auth['client_secret'] = self._client_secret
                self._store.save_auth(auth)
                return "Token successfully stored"
            return "An error occurred retrieving access token; "\
                "please check your client id and client secret."
        abort(404)

    def authorize(self, client_id, client_secret):
        self._client_id = client_id
        self._client_secret = client_secret
        app = Flask(__name__)
        app.add_url_rule('/', 'index', self.index)
        app.add_url_rule('/token', 'get_token', self.get_token)
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        print("Navigate to http://localhost:{} using your web browser and "
              "perform the authorization flow.\n"
              "Press CTRL-C to abort".format(self._port))
        app.run(port=self._port)


class AccessTokenProvider:

    def __init__(self, store):
        self._store = store

    def get_access_token(self):
        auth = self._store.load_auth()
        if time.time() < auth['expires_at']:
            return auth['access_token']
        response = requests.post(Authorizer.TOKEN_URL, data={
            'client_id': auth['client_id'],
            'client_secret': auth['client_secret'],
            'refresh_token': auth['refresh_token'],
            'grant_type': 'authorization_code'
        })
        d = response.json()
        auth['refresh_token'] = d['refresh_token']
        auth['access_token'] = d['access_token']
        auth['expires_at'] = d['expires_at']
        self._store.save_auth(auth)
        return auth['access_token']


def auth_store():
    return HomeAuthStore(config.get_strava_cli_dir(), "auth.json")


def authorizer(port):
    return Authorizer(port, auth_store())


def access_token_provider():
    return AccessTokenProvider(auth_store())
