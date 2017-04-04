from os import environ


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
