import config
import os.path
import os


class TokenProvider(object):

    def get_token(self):
        raise NotImplementedError


class TokenProviderChain(TokenProvider):

    def __init__(self, providers):
        self._providers = providers

    def get_token(self):
        for provider in self._providers:
            token = provider.get_token()
            if token is not None:
                return token
        return None


class HomeTokenProvider(TokenProvider):

    def __init__(self, dir, filename):
        self._filename = os.path.join(dir, filename)

    def get_token(self):
        if os.path.exists(self._filename):
            with open(self._filename, 'r') as token_file:
                return token_file.read()
        return None


class EnvTokenProvider(TokenProvider):

    def get_token(self):
        return os.environ.get("STRAVA_TOKEN", None)


class TokenStore(object):

    def store_token(self, token):
        raise NotImplementedError


class HomeTokenStore(TokenStore):

    def __init__(self, dir, filename):
        self._dir = dir
        self._filename = os.path.join(dir, filename)

    def store_token(self, token):
        if not os.path.exists(self._dir):
            os.makedirs(self._dir)
        with open(os.path.join(self._filename), 'w') as outfile:
            outfile.write(token)


def get_token_provider(args):
    return TokenProviderChain((
        HomeTokenProvider(config.get_strava_cli_dir(), 'token'),
        EnvTokenProvider()
    ))


def get_token_store(args):
    return HomeTokenStore(config.get_strava_cli_dir(), 'token')
