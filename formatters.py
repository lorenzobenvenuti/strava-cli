class Formatter(object):

    def format(self, activity):
        raise NotImplementedError()


class QuietFormatter(Formatter):

    def format(self, activity):
        return activity['id']


class DefaultFormatter(Formatter):

    def format(self, activity):
        return u"{id}\t{name}\t{distance}".format(**activity)


def get_formatter(quiet):
    if quiet:
        return QuietFormatter()
    return DefaultFormatter()
