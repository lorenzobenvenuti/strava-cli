#!/usr/bin/env python3

import auth
import argparse
import config
import repository
import predicates
import formatters
import cache
import logging


logging.basicConfig(
    filename=config.get_log_file(),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)


def authenticate(args):
    a = auth.authorizer(args.port)
    a.authorize(args.client_id, args.client_secret)


def get_token(args):
    tkn = auth.access_token_provider().get_access_token()
    if tkn is None:
        logging.getLogger('get_token').error("No token specified - aborting")
        import sys
        print("Cannot find a token - please authenticate")
        sys.exit(1)
    return tkn


def list_activities(args):
    r = repository.get_repository(get_token(args), args.update_cache)
    p = predicates.get_predicate_from_filters(args.filter)
    f = formatters.get_formatter(args.json, args.quiet, args.verbose)
    for activity in r.get_activities():
        if p.matches(activity):
            print(f.format(activity))


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
        if not id.isdigit():
            print('activity {} needs to be a number'.format(id))
            continue
        r.update_activity(int(id), data)


def activities_details(args):
    r = repository.get_repository(get_token(args), args.update_cache)
    f = formatters.get_formatter_details(args.json, args.quiet, args.verbose)
    for id in args.id:
        if not id.isdigit():
            print('activity {} needs to be a number'.format(id))
            continue
        activity = r.get_activity(int(id))
        print(f.format(activity) if activity is not None else 'activity {} not found'.format(id))


def activities_gps(args):
    r = repository.get_repository(get_token(args), args.update_cache)
    f = formatters.get_formatter_gps(args.json)
    for id in args.id:
        if not id.isdigit():
            print('activity {} needs to be a number'.format(id))
            continue
        print(f.format(*r.get_gps(int(id))))


def list_bikes(args):
    r = repository.get_repository(get_token(args))
    for bike in r.get_bikes():
        print('{id:<20} {name:<20}'.format(**bike))


def list_shoes(args):
    r = repository.get_repository(get_token(args))
    for shoe in r.get_shoes():
        print('{id:<20} {name:<20}'.format(**shoe))


def clear_cache(args):
    logging.getLogger('clear_cache').info("Clearing cache")
    cache.get_cache().clear()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Strava Command Line Interface')
    parser.set_defaults(func=lambda args: parser.print_help())
    subparsers = parser.add_subparsers()

    parser_list = subparsers.add_parser('activities', help='List activities '
                                        'according to specified filters')
    parser_list.add_argument('--filter', '-f', action='append',
                             help='Adds a filter to the query')
    parser_list.add_argument('--quiet', '-q', action='store_true',
                             help='Prints only activity identifiers')
    parser_list.add_argument('--json', '-j', action='store_true',
                             help='Output in JSON format')
    parser_list.add_argument('--verbose', '-v', action='store_true',
                             help='Prints more information about the activity')
    parser_list.add_argument('--update-cache', '-c', type=lambda s: s.lower() in ['true', 'yes'], default=True,
                             help='Update the internal cache.  This is the default.')
    parser_list.set_defaults(func=list_activities)

    parser_details = subparsers.add_parser('details', help='Retrieves the '
                                           'details of one or more activities')
    parser_details.add_argument('--quiet', '-q', action='store_true',
                             help='Prints only activity identifiers')
    parser_details.add_argument('--json', '-j', action='store_true',
                             help='Output in JSON format')
    parser_details.add_argument('--verbose', '-v', action='store_true',
                             help='Prints more information about the activity')
    parser_details.add_argument('--update-cache', '-c', type=lambda s: s.lower() in ['true', 'yes'], default=True,
                             help='Update the internal cache.  This is the default.')
    parser_details.add_argument('id',
                                nargs='+', help='Activity id(s)')
    parser_details.set_defaults(func=activities_details)

    parser_gps = subparsers.add_parser('gps', help='Retrieves the '
                                           'gps file of one or more activities')
    parser_gps.add_argument('--json', '-j', action='store_true',
                             help='Output in JSON format')
    parser_gps.add_argument('id',
                                nargs='+', help='Activity id(s)')
    parser_gps.add_argument('--update-cache', '-c', type=lambda s: s.lower() in ['true', 'yes'], default=True,
                             help='Update the internal cache.  This is the default.')
    parser_gps.set_defaults(func=activities_gps)

    parser_update = subparsers.add_parser('update',
                                          help='Update one or more activities')
    parser_update.add_argument('--set', '-s', action='append',
                               required=True, help='Sets a property')
    parser_update.add_argument('id', nargs='+', help='Activity id(s)')
    parser_update.set_defaults(func=update_activities)

    parser_bikes = subparsers.add_parser('bikes', help='Retrieve bikes')
    parser_bikes.set_defaults(func=list_bikes)

    parser_shoes = subparsers.add_parser('shoes', help='Retrieve shoes')
    parser_shoes.set_defaults(func=list_shoes)

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

    args = parser.parse_args()

    args.func(args)
