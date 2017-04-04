# https://pypi.python.org/pypi/redis
# i've misspelled enqueue probably million times in this file.
from redis import StrictRedis as RedisConnection
from warnings import warn
from os import getenv


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

    def atomic_cylinders_enqueue(self, venue, cylinders_dikt):
        """
        For the venue, atomically enqueue to the queues of all cylinders.

        We go the extra mile with the pipeline, because we want to ensure that
        when we enqueue data for a venue, the queues have the same len before and after the transaction.
        Transaction ensures that if we enqueue on 4 queues, and we are halfway-through,
        if another client tries to dequeue/check the len of a queue, he will first have to wait for the transaction
        to finish.

        There's NO rollback supported, BUT the pipeline is executed as one
        command (thus no other clients can enqueue/dequeue at the same time)
        :param venue:
        :param cylinders_dikt: keys: cylinder label, values: cylinder data
        :return: none
        :raises RuntimeError, if the length of the queues is different after the atomic enqueuing operation
        """
        pipe = self.r.pipeline(transaction=True)
        for cyl_label, cyl_data in cylinders_dikt.items():
            self.enqueue(pipe)(key(venue, cyl_label), cyl_data)

        # commit the pipeline
        pipe.execute()
        cyl_labels = cylinders_dikt.keys()
        cylinder_lengths = [self.get_size_of_cylinder_queue(venue=venue, cylinder=cyl_label) for cyl_label in
                            cyl_labels]
        # if len(set(cylinder_lengths)) != 1:
        #     raise RuntimeError(
        #         "The length of the queues for [{venue}] differ. queue lenghts:[{lenghts}]. keys:[{keys}]".format(
        #             lenghts=cylinder_lengths,
        #             venue=venue,
        #             keys=cyl_labels
        #         ))

    def multiple_cylinders_dequeue(self, venue, cylinder_labels):
        """
        Dequeue from multiple cylinders, and return a combined result.
        # https://redis.io/commands/blpop#codeblpopcode-inside-a-codemulticode--codeexeccode-transaction
        # ^ we can't do an "atomic"/transaction when we do a "blocking" pop,
        thus the data for a cylinder can be None (if the queue of the cylinder was empty)
        We raise a RuntimeError if some queues returned a result, and some a None, because all queues should
        have the same number of elements at all times.
        :param venue:
        :param cylinder_labels: strings
        :return:  dict with keys the cylinder_labels, and values the dequequed elemnt for this cylinder label
        :raises RuntimeError - if some queues returned a result and some didn't.
        """

        pipe = self.r.pipeline(transaction=True)
        dequeue = self.non_blocking_dequeue(pipe)

        result = {}
        for cyl_label in cylinder_labels:
            dequeue(key(venue=venue, cylinder=cyl_label))

        # ensure that either **all** queues returned an element OR **all** queues returned None
        response = pipe.execute()
        if len(response) is not len(cylinder_labels):
            raise RuntimeError(
                "The response should return some data (possibly None) for all queues")

        for cyl_label, cyl_data in zip(cylinder_labels, response):
            result[cyl_label] = cyl_data
        return result

    def dequeue_from_cylinder_queue_of_venue(self, venue, cylinder_label, blocking=False):
        """
        Same as enqueue_to_cylinder_queue_of_venue, but to dequeue from the queue.
        :param blocking - should the request block if there's no data in the queue.
        if False, and no data in the queue, return None.
        If True, and no data in the queue, block until data appears
        :returns the oldest entry in the queue, or None if queue empty and blocking=False
        """
        cyl_key = key(venue, cylinder_label)
        if blocking:
            # brpop returns a  (key, data) tuple. We are interested only in the data
            response = self.blocking_dequeue(self.r)(cyl_key)
            assert response, "Response from **blocking** dequeue None"
            response = response[1]
        else:
            response = self.non_blocking_dequeue(self.r)(cyl_key)
        return response

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

    def get_size_of_cylinder_queue(self, venue, cylinder):
        return self.r.llen(key(venue=venue, cylinder=cylinder))

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
