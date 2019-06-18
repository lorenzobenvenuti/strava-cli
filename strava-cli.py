#!/usr/bin/env python3

import auth
import argparse
import config
import repository
import predicates
import formatters
import cache
import authtoken
import logging


logging.basicConfig(
    filename=config.get_log_file(),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)


def print_utf8(value):
    print(value)


def authenticate(args):
    a = auth.Authorizer(args.port)
    a.authorize(args.client_id, args.client_secret)


def get_token(args):
    tkn = authtoken.get_token_provider(args).get_token()
    if tkn is None:
        logging.getLogger('get_token').error("No token specified - aborting")
        import sys
        print_utf8("No token specified - please"
                   "store a token using the store-token command or "
                   "set the STRAVA_TOKEN environment variable")
        sys.exit(1)
    return tkn


def list_activities(args):
    r = repository.get_repository(get_token(args))
    p = predicates.get_predicate_from_filters(args.filter)
    f = formatters.get_formatter(args.quiet)
    for activity in r.get_activities():
        if p.matches(activity):
            print_utf8(f.format(activity))


def get_update_data(args):
    data = {}
    for value in args.set:
        tokens = value.split('=')
        if len(tokens) != 2:
            raise ValueError("Invalid argument {}".format(value))
        data[tokens[0]] = tokens[1]
    return data


def update_activities(args):
    r = repository.get_repository(get_token(args))
    data = get_update_data(args)
    for id in args.id:
        r.update_activity(int(id), data)


def activities_details(args):
    raise NotImplementedError


def list_bikes(args):
    r = repository.get_repository(get_token(args))
    for bike in r.get_bikes():
        print_utf8('{id:<20} {name:<20}'.format(**bike))


def clear_cache(args):
    logging.getLogger('clear_cache').info("Clearing cache")
    cache.get_cache().clear()


def store_token(args):
    authtoken.get_token_store(args).store_token(args.token)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Strava Command Line Interface')
    subparsers = parser.add_subparsers()

    parser_list = subparsers.add_parser('activities', help='List activities '
                                        'according to specified filters')
    parser_list.add_argument('--filter', '-f', action='append',
                             help='Adds a filter to the query')
    parser_list.add_argument('--quiet', '-q', action='store_true',
                             help='Prints only activity identifiers')
    parser_list.set_defaults(func=list_activities)

    parser_details = subparsers.add_parser('details', help='Retrieves the '
                                           'details of one or more activities')
    parser_details.add_argument('id',
                                nargs='+', help='Activity id(s)')
    parser_details.set_defaults(func=activities_details)

    parser_update = subparsers.add_parser('update',
                                          help='Update one or more activities')
    parser_update.add_argument('--set', '-s', action='append',
                               required=True, help='Sets a property')
    parser_update.add_argument('id', nargs='+', help='Activity id(s)')
    parser_update.set_defaults(func=update_activities)

    parser_bikes = subparsers.add_parser('bikes', help='Retrieve bikes')
    parser_bikes.set_defaults(func=list_bikes)

    parser_clear_cache = subparsers.add_parser('clear-cache',
                                               help='Clear the cache')
    parser_clear_cache.set_defaults(func=clear_cache)

    parser_auth = subparsers.add_parser('authenticate', help='Authenticate '
                                        'using a client secret and client id')
    parser_auth.add_argument('--port', '-p', type=int,
                             default=8080, help='Port')
    parser_auth.add_argument('--client-id', '-i',
                             type=int, required=True, help='Strava Client Id')
    parser_auth.add_argument('--client-secret', '-s',
                             required=True, help='Strava Client Secret')
    parser_auth.set_defaults(func=authenticate)

    parser_store_token = subparsers.add_parser(
                          'store-token', help='Store authentication token')
    parser_store_token.set_defaults(func=store_token)
    parser_store_token.add_argument('token', help='Authentication token')

    args = parser.parse_args()

    args.func(args)
