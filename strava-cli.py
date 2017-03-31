#!/usr/bin/env python

import argparse
import repository
import predicates
import formatters


def list_activities(args):
    r = repository.get_repository(args.token)
    p = predicates.get_predicate_from_filters(args.filter)
    f = formatters.get_formatter(args.quiet)
    for activity in r.get_activities():
        if p.matches(activity):
            print f.format(activity)


def update_activities(args):
    raise NotImplementedError


def activities_details(args):
    raise NotImplementedError


def list_bikes(args):
    r = repository.get_repository(args.token)
    for bike in r.get_bikes():
        print '{id:<20} {name:<20}'.format(**bike)


def clear_cache(args):
    print "CLEAR_CACHE"
    print args


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
    parser_details.add_argument('activity-id',
                                nargs='+', help='Activity id(s)')
    parser_details.set_defaults(func=activities_details)

    parser_update = subparsers.add_parser('update',
                                          help='Update one or more activities')
    parser_update.add_argument('--set', '-s', action='append',
                               required=True, help='Sets a property')
    parser_update.add_argument('activity-id', nargs='+', help='Activity id(s)')
    parser_update.set_defaults(func=update_activities)

    parser_bikes = subparsers.add_parser('bikes', help='Retrieve bikes')
    parser_bikes.set_defaults(func=list_bikes)

    parser_clear_cache = subparsers.add_parser('clear-cache',
                                               help='Clear the cache')
    parser_clear_cache.set_defaults(func=clear_cache)

    args = parser.parse_args()
    args.func(args)
