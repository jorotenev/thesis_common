# https://pypi.python.org/pypi/redis
# i've misspelled enqueue probably million times in this file.
from redis import StrictRedis as RedisConnection
from os import getenv
from .utils import get_non_venue_part_of_key, key


class RedisAdapter(object):
    def __init__(self,
                 host=None,
                 db=None,
                 port=None,
                 decode_responses=True):
        host = host or getenv("REDIS_HOST")
        db = db or int(getenv("REDIS_DB"))
        port = port or int(getenv("REDIS_PORT", 6379))

        self.r = RedisConnection(host=host,
                                 db=db,
                                 port=port,
                                 decode_responses=decode_responses)

        self.non_blocking_dequeue = lambda redis: redis.rpop
        self.blocking_dequeue = lambda redis: redis.brpop
        self.enqueue = lambda redis: redis.lpush

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


