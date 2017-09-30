import os.path
import json
import util
from flask import Flask, redirect, request
import requests


class AbstractAuth(object):

    def get_token(self):
        raise NotImplementedError

    def set_token(self, value):
        raise NotImplementedError


class StoreAuth(AbstractAuth):

    def __init__(self, store):
        self._store = store
        self._data = None

    def get_token(self):
        return self._store.get('token')

    def set_token(self, token):
        self._store.set('token', token)


class Authorizer(object):

    AUTH_URL_TEMPLATE = 'https://www.strava.com/oauth/authorize?client_id={}'\
        '&response_type=code&redirect_uri=http://localhost:{}/token'\
        '&scope=view_private,write'

    TOKEN_URL = 'https://www.strava.com/oauth/token'

    def __init__(self, port):
        self._port = port

    def index(self):
        return redirect(Authorizer.AUTH_URL_TEMPLATE.format(
                            self._client_id, self._port), 302)

    def get_token(self):
        if 'error' in request.args:
            return "Access denied"
        if 'code' in request.args:
            response = requests.post(Authorizer.TOKEN_URL, data={
                'client_id': self._client_id,
                'client_secret': self._client_secret,
                'code': request.args['code']})
            d = response.json()
            if 'access_token' in d:
                return "Access token: {}".format(d['access_token'])
            return "An error occurred retrieving access token; "\
                "please check your client id and client secret"
        return "?"

    def authorize(self, client_id, client_secret):
        self._client_id = client_id
        self._client_secret = client_secret
        app = Flask(__name__)
        app.add_url_rule('/', 'index', self.index)
        app.add_url_rule('/token', 'get_token', self.get_token)
        app.run(port=self._port)

if __name__ == '__main__':
    import sys
    a = Authorizer(8080)
    a.authorize(sys.argv[1], sys.argv[2])
