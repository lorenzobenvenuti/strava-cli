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
            refresher = TokenRefresher(self._client_id, self._client_secret)
            auth = refresher.refresh(code=request.args['code'])
            if auth:
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


class TokenRefresher:

    TOKEN_URL = 'https://www.strava.com/oauth/token'
    REFRESH_TOKEN = 'refresh_token'
    ACCESS_TOKEN = 'access_token'
    EXPIRES_AT = 'expires_at'
    CLIENT_ID = 'client_id'
    CLIENT_SECRET = 'client_secret'
    GRANT_TYPE = 'grant_type'
    CODE = 'code'
    AUTHORIZATION_CODE = 'authorization_code'
    KEYS = (EXPIRES_AT, REFRESH_TOKEN, ACCESS_TOKEN)

    def __init__(self, client_id, client_secret):
        self._client_id = client_id
        self._client_secret = client_secret

    def refresh(self, code=None, refresh_token=None):
        if code and refresh_token:
            raise ValueError("Choose one between code and refresh_token")
        data = {}
        data[TokenRefresher.CLIENT_ID] = self._client_id
        data[TokenRefresher.CLIENT_SECRET] = self._client_secret
        data[TokenRefresher.GRANT_TYPE] = TokenRefresher.AUTHORIZATION_CODE
        if refresh_token:
            data[TokenRefresher.REFRESH_TOKEN] = refresh_token
        if code:
            data[TokenRefresher.CODE] = code
        response = requests.post(TokenRefresher.TOKEN_URL, data=data)
        d = response.json()
        if TokenRefresher.ACCESS_TOKEN in d:
            auth = {k: d[k] for k in TokenRefresher.KEYS}
            auth[TokenRefresher.CLIENT_ID] = self._client_id
            auth[TokenRefresher.CLIENT_SECRET] = self._client_secret
            return auth
        return None


class AccessTokenProvider:

    def __init__(self, store):
        self._store = store

    def get_access_token(self):
        auth = self._store.load_auth()
        if time.time() < auth[TokenRefresher.EXPIRES_AT]:
            return auth[TokenRefresher.ACCESS_TOKEN]
        refresher = TokenRefresher(self._client_id, self._client_secret)
        auth = refresher.refresh(
                            refresh_token=auth[TokenRefresher.REFRESH_TOKEN])
        if not auth:
            return None
        self._store.save_auth(auth)
        return auth[TokenRefresher.ACCESS_TOKEN]


def auth_store():
    return HomeAuthStore(config.get_strava_cli_dir(), "auth.json")


def authorizer(port):
    return Authorizer(port, auth_store())


def access_token_provider():
    return AccessTokenProvider(auth_store())
