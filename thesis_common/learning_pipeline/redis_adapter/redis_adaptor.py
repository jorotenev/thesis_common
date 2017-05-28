# https://pypi.python.org/pypi/redis
# i've misspelled enqueue probably million times in this file.
from redis import StrictRedis as RedisConnection
from os import getenv
from .utils import get_non_venue_part_of_key, key, venue_wildcard_key
from thesis_common.common import thesis_logger


def stringify_int(v):
    try:
        return str(int(v))
    except Exception as ex:
        return None


class RedisAdapter(object):
    def __init__(self,
                 host=None,
                 db=None,
                 port=None,
                 decode_responses=True):
        host = host or getenv("REDIS_HOST")
        db = stringify_int(db) or int(getenv("REDIS_DB"))  # "0" is a truthy value
        port = stringify_int(port) or int(getenv("REDIS_PORT", 6379))

        self.r = RedisConnection(host=host,
                                 db=db,
                                 port=port,
                                 decode_responses=decode_responses)
        
        # fail fast if we can't connect
        self.r.ping()

        self.non_blocking_dequeue = lambda redis: redis.rpop
        self.blocking_dequeue = lambda redis: redis.brpop
        self.enqueue = lambda redis: redis.lpush
        thesis_logger.debug("{name} started. db:#{db} host:{host} port:{port}".format(
            name=self.__class__.__name__,
            host=host,
            db=db,
            port=port,
        ))

    def redis_is_up(self, ):
        try:
            return self.r.ping()
        except:
            return False

    def drop_db(self):
        """
        Deletes ALL keys of the current database
        :return:
        """
        keys = self.r.keys("*")
        if keys:
            self.r.delete(*keys)
