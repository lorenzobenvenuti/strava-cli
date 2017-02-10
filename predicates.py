import time
import datetime


class Predicate(object):

    def matches(self, value):
        raise NotImplementedError


class DatePredicate(Predicate):

    def __init__(self, date):
        self._date = date

    def _parse_date(self, value):
        return datetime.datetime.strptime(
            value['start_date_local'], '%Y-%m-%dT%H:%M:%SZ')


class AfterPredicate(DatePredicate):

    def matches(self, value):
        return self._parse_date(value) > self._date


class BeforePredicate(DatePredicate):

    def matches(self, value):
        return self._parse_date(value) < self._date


class BoolPredicate(Predicate):

    def __init__(self, name, value):
        self._name = name
        self._value = value

    def matches(self, value):
        return value[self._name] == self._value


class AndPredicate(Predicate):

    def __init__(self, predicates):
        self._predicates = predicates

    def matches(self, value):
        for predicate in self._predicates:
            if not predicate.matches(value):
                return False
        return True


def parse_date(date_str):
    if len(date_str) == 4:
        date_str += "0101"
    elif len(date_str) == 6:
        date_str += "01"
    return datetime.datetime.strptime(date_str, "%Y%m%d")


def get_bool(bool_str):
    if bool_str.lower() in ('true', '1'):
        return True
    if bool_str.lower() in ('false', '0'):
        return False
    raise ValueError("Invalid boolean value {}".format(bool_str))


def get_predicate(name, value):
    if name == "before":
        return BeforePredicate(parse_date(value))
    if name == "after":
        return AfterPredicate(parse_date(value))
    if name == "trainer":
        return BoolPredicate('trainer', get_bool(value))
    if name == "private":
        return BoolPredicate('private', get_bool(value))
    # TODO: descrizione? Titolo?
    raise ValueError("Invalid type {}".format(name))


def get_predicate_from_filters(items):
    predicates = []
    for item in items:
        try:
            key, value = item.split("=", 1)
            predicates.append(get_predicate(key, value))
        except ValueError:
            raise ValueError("Invalid value {}".format(item))
    return AndPredicate(predicates)
