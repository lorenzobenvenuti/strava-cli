#!/usr/bin/env python

import argparse
import repository
import predicates
import formatters
import cache


def list_activities(args):
    r = repository.get_repository(args.token)
    p = predicates.get_predicate_from_filters(args.filter)
    f = formatters.get_formatter(args.quiet)
    for activity in r.get_activities():
        if p.matches(activity):
            print f.format(activity)


def get_update_data(args):
    data = {}
    for value in args.set:
        tokens = value.split('=')
        if len(tokens) != 2:
            raise ValueError("Invalid argument {}".format(value))
        data[tokens[0]] = tokens[1]
    return data


def update_activities(args):
    r = repository.get_repository(args.token)
    data = get_update_data(args)
    for id in args.id:
        r.update_activity(int(id), data)


def activities_details(args):
    raise NotImplementedError


def list_bikes(args):
    r = repository.get_repository(args.token)
    for bike in r.get_bikes():
        print '{id:<20} {name:<20}'.format(**bike)


def clear_cache(args):
    cache.get_cache().clear()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Strava Command Line Interface')
    parser.add_argument('--token', '-t',
                        required=True, help='Strava API access token')
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

    args = parser.parse_args()
    args.func(args)
