from os import environ

key_separator = "____"
redis_wildcard_sym = "*"


def key(*args, **kwargs):
    """
    The convention is to have the venue name as the first argument.
    key("agora", 'daily') -> "agora____daily"
    make a redis composite key
    :param args - order matters, the parameters to use for the composite key
    :return: the string to be used as a key on the redis server
    """
    assert not kwargs, "Passing **kwargs is not supported. Ordering matters here, so only *args supported"
    assert len(list(args)), "Didn't specify any arguments to form a composite key."
    return key_separator.join(list(args))


def split_key(key):
    """
    "agora_____daily" -> ['agora', 'daily']
    """
    return key.split(key_separator)


def get_venue_from_key(key):
    return split_key(key)[0]


def get_non_venue_part_of_key(key):
    """
    "agora____daily___something____else" -> '____daily___something____else'
    :param key: composite key (as returned by key())
    :return:
    """
    return key_separator.join(split_key(key)[1:])


def venue_wildcard_key(venue):
    """
    When using the redis.keys command, use this function to get a wildcard key str which will match all keys
    of :venue. (assuming that the key was generate with calling key(venue, ...) - i.e. the name of the venue was first
    argument)
    :param venue:
    :return: e.g. "agora____*"
    """
    return key(venue, redis_wildcard_sym)


def configure_redis_for_testing():
    # use a different namespace when testing

    redis_db_key = 'REDIS_DB'
    redis_db_for_testing_key = 'REDIS_DB_FOR_TESTING'
    assert redis_db_key in environ, "%s env var is not set!" % redis_db_key
    assert redis_db_for_testing_key in environ, "%s env var is not set!" % redis_db_for_testing_key

    db_for_testing = int(environ[redis_db_for_testing_key])

    if int(environ[redis_db_key]) != db_for_testing:
        print("Going to use redis db #%i during testing" % db_for_testing)
    environ[redis_db_key] = str(db_for_testing)
