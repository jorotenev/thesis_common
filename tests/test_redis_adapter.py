import json
from thesis_common.learning_pipeline.redis_adapter import RedisAdapter, key, configure_redis_for_testing
from thesis_common.learning_pipeline import Label
from unittest import TestCase


class TestRedisAdapter(TestCase):
    @classmethod
    def setUpClass(cls):
        configure_redis_for_testing()

    def setUp(self):
        self.adapter = RedisAdapter()
        # the underlying redis connection (python.redis)
        self.r = self.adapter.r

        self.cyl_1_label = Label.daily.name
        self.cyl_2_label = Label.weekly.name
        self.venue = 'agora'
        self.key_cylinder_1 = key(self.venue, self.cyl_1_label)
        self.key_cylinder_2 = key(self.venue, self.cyl_2_label)
        self.add_to_redis()

        self.labels = [self.cyl_1_label, self.cyl_2_label]
        self.input_lists = [self.cyl_1_input_list, self.cyl_2_input_list]

    def add_to_redis(self):
        """
        Add to a redis queue data for two cylinders of a venue.
        Each queue of a cylinder receives a number of snapshots of the contents of the cylinder.

        """
        self.cyl_1_input_list = []
        for i in range(10):
            # fake adding the contents of a cylinder
            self.cyl_1_input_list.append(list(range(i, i + 10)))

        self.cyl_2_input_list = []
        for i in range(10, 20):
            # fake adding the contents of a cylinder
            self.cyl_2_input_list.append(list(range(i, i + 10)))

        assert len(self.cyl_2_input_list) == len(self.cyl_1_input_list)

        for cyl_1_snapshot, cyl_2_snapshot in zip(self.cyl_1_input_list, self.cyl_2_input_list):
            # a dikt with the "current" data of both cylinders
            dikt = {
                self.cyl_1_label: json.dumps(cyl_1_snapshot),
                self.cyl_2_label: json.dumps(cyl_2_snapshot)
            }
            self.adapter.atomic_cylinders_enqueue(venue=self.venue, cylinders_dikt=dikt)

    def tearDown(self):
        self.adapter.drop_db()

    def test_smoke_test(self):
        self.assertTrue(self.r.ping())

    def test_atomic_cylinders_enqueue(self):
        """
        Test that enqueuing on the queue of cylinder of a venue works correctly

        The memory engine periodically flushes the contents of its cylinders
        to redis. here we call a snapshot the data of one such flush
        we simulate several of these flushes,
        so that we can ensure that the queue on redis works
        """

        # we added data to the redis
        # now we need to check that redis has the correct keys


        # there are entries in the redis for both cylinders
        # and they are no other keys
        self.assertEqual(set([self.key_cylinder_1, self.key_cylinder_2]), set(self.r.keys("*")))

        # let's assert the len of both queues is correct
        self.assertEqual(len(self.cyl_1_input_list), self.r.llen(self.key_cylinder_1))
        self.assertEqual(len(self.cyl_2_input_list), self.r.llen(self.key_cylinder_2))

        assert len(self.cyl_1_input_list) == len(self.cyl_2_input_list)

        # now let's verify the contents of each of the cylinders on redis.
        # it's a queue, thus if we start dequeuing, we should first see the [0] element of cyl_[1|2]_queue
        for snapshot_cyl_1, snapshot_cyl_2 in zip(self.cyl_1_input_list,
                                                  self.cyl_2_input_list):
            dequeued_cyl_1_snapshot = json.loads(self.r.rpop(self.key_cylinder_1))
            dequeued_cyl_2_snapshot = json.loads(self.r.rpop(self.key_cylinder_2))

            self.assertEqual(snapshot_cyl_1, dequeued_cyl_1_snapshot)
            self.assertEqual(snapshot_cyl_2, dequeued_cyl_2_snapshot)

        # we dequeued everything so the queue should be empty
        self.assertEqual(0, self.r.llen(self.key_cylinder_1))
        self.assertEqual(0, self.r.llen(self.key_cylinder_2))

    def test_get_cylinder_queue_of_venue(self):

        for cyl_label, cyl_queue in zip(self.labels, self.input_lists):
            redis_response = self.adapter.get_cylinder_queue_of_venue(venue=self.venue, cylinder=cyl_label)
            # we enqueue on the left and dequeue from the right of the redis data structure
            # thus we need to reverse before comparing to the queue we built here
            queue_from_redis = list(reversed([json.loads(l) for l in redis_response]))
            self.assertEqual(cyl_queue, queue_from_redis)

    def test_get_queues_for_venue(self):
        dikt_with_queues = self.adapter.get_queues_for_venue(venue=self.venue)

        redis_internal_labels = [key(self.venue, label) for label in self.labels]
        self.assertEqual(set(redis_internal_labels), set(dikt_with_queues.keys()))

        # we get the queue for this cylinder, then reverse it (to compare it with the initial list we stored)
        queue_1 = [json.loads(single_entry) for single_entry in reversed(dikt_with_queues[redis_internal_labels[0]])]
        queue_2 = [json.loads(single_entry) for single_entry in reversed(dikt_with_queues[redis_internal_labels[1]])]

        self.assertEqual(self.input_lists[0], queue_1)
        self.assertEqual(self.input_lists[1], queue_2)

    def test_dequeue_from_cylinder_queue_of_venue(self):
        for label, input_list in zip(self.labels, self.input_lists):
            dequeued = self.adapter.dequeue_from_cylinder_queue_of_venue(venue=self.venue, cylinder_label=label)
            dequeued = json.loads(dequeued)
            # if we deque from a queue, we get the oldest entry in the queue,
            # which is the first element we addedt to the queue - the first element of the list
            self.assertEqual(input_list[0], dequeued)
