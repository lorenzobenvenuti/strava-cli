#!/usr/bin/env python

import argparse
from repository import CachedRepository, ApiRepository

def list_activities(args):
    repository = CachedRepository(ApiRepository(args.token))
    for activity in repository.get_activities():
        print u"{id}; {name}; {name}; {trainer}; {distance}; {gear_id}".format(**activity)

def update_activities(args):
    print "UPDATE"
    print args

def list_bikes(args):
    repository = CachedRepository(ApiRepository(args.token))
    for bike in repository.get_bikes():
        print '{id:<20} {name:<20}'.format(**bike)

def clear_cache(args):
    print "CLEAR_CACHE"
    print args

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Strava CLI interface')
    parser.add_argument('--token', '-t', required=True, help='Strava API access token')
    subparsers = parser.add_subparsers()

    parser_list = subparsers.add_parser('activities', help='List activities according to specified filters')
    parser_list.add_argument('--filter', '-f', action='append', help='Adds a filter to the query')
    parser_list.add_argument('--quiet', '-q', action='store_true', help='Prints only activity identifiers')
    #parser_list.add_argument('--cache', '-c', action='store_true', help='Stores items in cache') ## ???
    parser_list.set_defaults(func=list_activities)

    parser_update = subparsers.add_parser('update', help='Update an activity')
    parser_update.add_argument('--set', '-s', action='append', required=True, help='Sets a property')
    parser_update.add_argument('activity-id', nargs='+', help='Sets a property')
    parser_update.set_defaults(func=update_activities)

    parser_bikes = subparsers.add_parser('bikes', help='Retrieve bikes')
    parser_bikes.set_defaults(func=list_bikes)

    parser_clear_cache = subparsers.add_parser('clear-cache', help='Clear the cache')
    parser_clear_cache.set_defaults(func=clear_cache)

    args = parser.parse_args()
    args.func(args)
