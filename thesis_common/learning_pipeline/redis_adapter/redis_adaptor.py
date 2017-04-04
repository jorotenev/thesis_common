# https://pypi.python.org/pypi/redis
from redis import StrictRedis as RedisConnection
from warnings import warn
from os import getenv


class RedisAdapter(object):
    def __init__(self):
        # import here so that other script had the chance to adjust some of the config

        self.r = RedisConnection(host=getenv('REDIS_HOST'),
                                 db=int(getenv("REDIS_DB")),
                                 port=int(getenv("REDIS_PORT", 6379)),
                                 decode_responses=True)

    def atomic_cylinders_enqueue(self, venue, cylinders_dikt):
        """
        For the venue, atomically enqueue to the queues of all cylinders.
        If enqueue for one cylinder-queue fails, all are aborted.

        We go the extra mile with the pipeline, because we want to ensure that
        when we enqueue data for a venue, the queues always have the same len
        :param venue:
        :param cylinders_dikt: keys: cylinder label, values: cylinder data
        :return: none
        """
        pipe = self.r.pipeline(transaction=True)
        for cyl_label, cyl_data in cylinders_dikt.items():
            pipe.lpush(key(venue, cyl_label), cyl_data)

        # commit the transaction
        pipe.execute()
        cyl_labels = cylinders_dikt.keys()
        cylinder_lengths = [self.r.llen(key(venue, cyl_label) for cyl_label in cyl_labels)]
        if len(set(cylinder_lengths)) != len(cylinder_lengths):
            warn("The length of the queues for [{venue}] differ. queue lenghts:[{lenghts}]. keys:[{keys}]".format(
                lenghts=cylinder_lengths,
                venue=venue,
                keys=cyl_labels
            ))

    def dequeue_from_cylinder_queue_of_venue(self, venue, cylinder_label, blocking=False):
        """
        Same as enqueue_to_cylinder_queue_of_venue, but to dequeue from the queue.
        :param blocking - should the request block if there's no data in the queue.
        if False, and no data in the queue, return None.
        If True, and no data in the queue, block until data appears
        :returns a string with the oldest entry in the queue, or None if queue empty and blocking=False
        """

        pop = self.r.brpop if blocking else self.r.rpop
        return pop(key(venue, cylinder_label))

    def get_queues_for_venue(self, venue):
        """
        Given a venue, return the queues of the cylinders of this venue.
        The return value is a dikt, with keys the internal, redis, name of the queue + the data of the queue

        :param venue:
        :return:  dikt with keys the internal name of a cylinder queue and value the queue of this cylinder
        """
        keys = self.r.keys("%s*" % key(venue, ''))
        result = {}
        for k in keys:
            queue_len = self.r.llen(k)
            queue = self.r.lrange(k, 0, queue_len)
            result[k] = queue

        return result

    def get_cylinder_queue_of_venue(self, venue, cylinder):
        """
        Get the contents of a queue. The first element is the most recently enqueued
        :param venue: str
        :param cylinder: str
        :return: list
        """
        queue_name = key(venue, cylinder)
        queue_len = self.r.llen(queue_name)
        queue_data = self.r.lrange(queue_name, 0, queue_len)
        return queue_data

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

    def get_venue_labels(self, venue):
        """
        Return the names of all Labels used as keys for this venue
        :param venue: venue name
        :return: array of strings of the names of labels
        """
        venue_keys = self.r.keys(
            key(venue, '') + "*")  ## gets all keys that have in the beginning the name of the venue
        return [get_label_from_key(k) for k in venue_keys]  # return only the label


key_separator = "____"


def key(venue, cylinder):
    """
    make a redis composite key
    :param args - order matters, the parameters to use for the composite key
    :return: the string to be used as a key on the redis server
    """
    return key_separator.join([venue, cylinder])


def split_key(key):
    """
    "agora_____daily" -> ['agora', 'daily']
    """
    return key.split(key_separator)


def get_venue_from_key(key):
    return split_key(key)[0]


def get_label_from_key(key):
    return split_key(key)[1]
