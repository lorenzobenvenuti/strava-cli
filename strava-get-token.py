#!/usr/bin/env python

import argparse
from flask import Flask, redirect, request
import requests

app = Flask(__name__)
args = None

AUTH_URL_TEMPLATE = 'https://www.strava.com/oauth/authorize?client_id={}'\
    '&response_type=code&redirect_uri=http://localhost:{}/token'\
    '&scope=view_private,write'


TOKEN_URL = 'https://www.strava.com/oauth/token'


@app.route("/")
def index():
    return redirect(AUTH_URL_TEMPLATE.format(args.client_id, args.port), 302)


@app.route("/token")
def get_token():
    if 'error' in request.args:
        return "Access denied"
    if 'code' in request.args:
        response = requests.post(TOKEN_URL, data={
            'client_id': args.client_id, 'client_secret': args.client_secret,
            'code': request.args['code']})
        d = response.json()
        if 'access_token' in d:
            return "Access token: {}".format(d['access_token'])
        return "An error occurred retrieving access token; "\
            "please check your client id and client secret"
    return "?"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description='Retrieves Strava API access token')
    parser.add_argument('--port', '-p', type=int, default=8080, help='Port')
    parser.add_argument('--client-id', '-i',
                        type=int, required=True, help='Strava Client Id')
    parser.add_argument('--client-secret', '-s',
                        required=True, help='Strava Client Secret')
    args = parser.parse_args()
    app.run(port=args.port, debug=True)
