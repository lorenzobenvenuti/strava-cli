import time
import datetime
import util
import logging


class Predicate(object):

    def matches(self, value):
        raise NotImplementedError


class AlwaysTruePredicate(Predicate):

    def matches(self, value):
        return True


class DatePredicate(Predicate):

    def __init__(self, date, utc = False):
        self._date = date
        self._utc = utc

    def _parse_date(self, value):
        return util.parse_date(value['start_date' if self._utc else 'start_date_local'])


class AfterPredicate(DatePredicate):

    def matches(self, value):
        return self._parse_date(value) > self._date


class BeforePredicate(DatePredicate):

    def matches(self, value):
        return self._parse_date(value) < self._date


class EqPredicate(Predicate):

    def __init__(self, name, value):
        self._name = name
        self._value = value

    def matches(self, value):
        return value[self._name] == self._value


class RangePredicate(Predicate):

    def __init__(self, name, min_value, max_value):
        self._name = name
        self._min = min_value
        self._max = max_value

    def matches(self, value):
        num = value[self._name]
        if self._min is None:
            return num < self._max
        if self._max is None:
            return num > self._min
        return num > self._min and num < self._max


class AndPredicate(Predicate):

    def __init__(self, predicates):
        self._predicates = predicates

    def matches(self, value):
        for predicate in self._predicates:
            if not predicate.matches(value):
                return False
        return True


def parse_date(utc, date_str):
    parsed_date = datetime.datetime.strptime(date_str, "%Y%m%d")
    if utc:
        parsed_date.replace(tzinfo=datetime.timezone.utc)
    return parsed_date


def parse_bool(bool_str):
    if bool_str.lower() in ('true', '1'):
        return True
    if bool_str.lower() in ('false', '0'):
        return False
    raise ValueError("Invalid boolean value {}".format(bool_str))


def parse_range(range_str):
    tokens = range_str.split('-')
    if len(tokens) != 2 or (not tokens[0] and not tokens[1]):
        raise ValueError("Invalid range {}".format(range_str))
    if not tokens[0]:
        return (None, float(tokens[1]))
    elif not tokens[1]:
        return (float(tokens[0]), None)
    return (float(tokens[0]), float(tokens[1]))


def get_predicate(utc, name, value):
    if name == "before":
        return BeforePredicate(parse_date(utc, value), utc)
    if name == "after":
        return AfterPredicate(parse_date(utc, value), utc)
    if name == "trainer":
        return EqPredicate('trainer', parse_bool(value))
    if name == "type":
        return EqPredicate('type', value)
    if name == "private":
        return EqPredicate('private', parse_bool(value))
    if name == "distance":
        min_value, max_value = parse_range(value)
        return RangePredicate('distance', min_value, max_value)
    if name == "elevation":
        min_value, max_value = parse_range(value)
        return RangePredicate('total_elevation_gain', min_value, max_value)
    raise ValueError("Invalid type {}".format(name))


def get_predicate_from_filters(utc, items):
    predicates = []
    if items is None:
        return AlwaysTruePredicate()
    for item in items:
        try:
            key, value = item.split("=", 1)
            predicates.append(get_predicate(utc, key, value))
        except ValueError as e:
            logging.getLogger("get_predicate_from_filters").exception(e)
            raise ValueError("Invalid value {}".format(item))
    return AndPredicate(predicates)
