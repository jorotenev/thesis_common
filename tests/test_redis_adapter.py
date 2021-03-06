from __future__ import absolute_import
import json
from time import sleep
from multiprocessing import Process
from datetime import datetime as dt, timedelta as td
from thesis_common.learning_pipeline.redis_adapter import StoredPredictionsAdapter, TrainingDataRedisAdapter, key, \
    venue_wildcard_key
from thesis_common.learning_pipeline.redis_adapter import configure_redis_for_testing
from thesis_common.learning_pipeline import Label
from unittest import TestCase


class TestTrainingDataRedisAdapter(TestCase):
    @classmethod
    def setUpClass(cls):

        configure_redis_for_testing()
        cls.adapter = TrainingDataRedisAdapter()
        cls.adapter.drop_db()

    def setUp(self):
        # the underlying redis connection (python.redis)
        self.raw_redis_client = self.adapter.r

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
        self.assertTrue(self.raw_redis_client.ping())

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
        self.assertEqual(set([self.key_cylinder_1, self.key_cylinder_2]), set(self.raw_redis_client.keys("*")))

        # let's assert the len of both queues is correct
        self.assertEqual(len(self.cyl_1_input_list), self.raw_redis_client.llen(self.key_cylinder_1))
        self.assertEqual(len(self.cyl_2_input_list), self.raw_redis_client.llen(self.key_cylinder_2))

        assert len(self.cyl_1_input_list) == len(self.cyl_2_input_list)

        # now let's verify the contents of each of the cylinders on redis.
        # it's a queue, thus if we start dequeuing, we should first see the [0] element of cyl_[1|2]_queue
        for snapshot_cyl_1, snapshot_cyl_2 in zip(self.cyl_1_input_list,
                                                  self.cyl_2_input_list):
            dequeued_cyl_1_snapshot = json.loads(self.raw_redis_client.rpop(self.key_cylinder_1))
            dequeued_cyl_2_snapshot = json.loads(self.raw_redis_client.rpop(self.key_cylinder_2))

            self.assertEqual(snapshot_cyl_1, dequeued_cyl_1_snapshot)
            self.assertEqual(snapshot_cyl_2, dequeued_cyl_2_snapshot)

        # we dequeued everything so the queue should be empty
        self.assertEqual(0, self.raw_redis_client.llen(self.key_cylinder_1))
        self.assertEqual(0, self.raw_redis_client.llen(self.key_cylinder_2))

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

    def test_dequeue_from_cylinder_queue_of_venue_non_blocking(self):
        for label, input_list in zip(self.labels, self.input_lists):
            for i, el in enumerate(input_list):
                dequeued = self.adapter.dequeue_from_cylinder_queue_of_venue(venue=self.venue, cylinder_label=label)
                dequeued = json.loads(dequeued)
                # if we deque from a queue, we get the oldest entry in the queue,
                # which is the i element of the list
                self.assertEqual(input_list[i], dequeued)

        # all queues should be empty
        # and non-blocking dequeue should return None
        for label, input_list in zip(self.labels, self.input_lists):
            size = self.adapter.get_size_of_cylinder_queue(venue=self.venue, cylinder=label)
            self.assertEqual(0, size)
            self.assertIsNone(self.adapter.dequeue_from_cylinder_queue_of_venue(venue=self.venue, cylinder_label=label))

    def test_get_venue_labels(self):

        # note that the labels are represented by their string representations,
        # and not the Enum.
        # During normal usage, the response from the adapter should be deserialized via:
        # json.loads(response, object_hook=thesis_common.deserialize_obj_hook)

        # verify that the returned names of Label enums belong of an actual instance of the Label enum
        possible_label_enum_names = [enum.name for enum in Label]
        labels = self.adapter.get_venue_labels(venue=self.venue)
        for returned_label in labels:
            self.assertIn(returned_label, possible_label_enum_names)

        # verifty that we receive back all the labels that we initially stored
        expected_labels = self.labels
        self.assertEqual(set(expected_labels), set(labels))

    def test_get_size_of_cylinder_queue(self):
        for label, queue in zip(self.labels, self.input_lists):
            self.assertEqual(len(queue), self.adapter.get_size_of_cylinder_queue(self.venue, label))
            self.adapter.dequeue_from_cylinder_queue_of_venue(venue=self.venue, cylinder_label=label)
            self.assertEqual(len(queue) - 1, self.adapter.get_size_of_cylinder_queue(self.venue, label))

    def test_dequeue_from_cylinder_queue_of_venue_blocking(self):
        """
        We want to ensure that the dequeueuing blocks
        We put it in a Process to and check that the process is "blocked" (dequeue doesn't return immediately when queue is empty
        """

        self.deplete_all_queues(
            depleter=lambda lbl: self.adapter.dequeue_from_cylinder_queue_of_venue(venue=self.venue,
                                                                                   cylinder_label=lbl,
                                                                                   blocking=True))
        for label in self.labels:
            p = Process(target=self.adapter.dequeue_from_cylinder_queue_of_venue,
                        name="dequeue_process",
                        kwargs={"venue": self.venue,
                                "cylinder_label": label,
                                "blocking": True})
            self.ensure_blocking_dequeue_blocks(label=label, process=p)

    def test_atomic_cylinders_dequeue(self):
        for l1, l2 in zip(self.cyl_1_input_list, self.cyl_2_input_list):
            result_dict = self.adapter.multiple_cylinders_dequeue(venue=self.venue,
                                                                  cylinder_labels=[self.cyl_1_label, self.cyl_2_label])
            self.assertEqual(l1, json.loads(result_dict[self.cyl_1_label]))
            self.assertEqual(l2, json.loads(result_dict[self.cyl_2_label]))

        self.ensure_all_queues_empty()
        for l1, l2 in zip(self.cyl_1_input_list, self.cyl_2_input_list):
            result_dict = self.adapter.multiple_cylinders_dequeue(venue=self.venue,
                                                                  cylinder_labels=[self.cyl_1_label, self.cyl_2_label])
            self.assertIsNone(result_dict[self.cyl_1_label])
            self.assertIsNone(result_dict[self.cyl_2_label])

    def ensure_blocking_dequeue_blocks(self, label, process):
        """
        For an **empty** queue of a cylinder with label `label`, ensure that a blocking dequeue() really blocks
        and that enqueuing to the queue, will unblock the dequeue()
        :param label: the label of cylinder
        process: multiprocessing.Process - initialised process with the dequeue operation as target= and the necessary
        args/kwargs of the target function.
        :return: None
        """
        assert 0 == self.adapter.get_size_of_cylinder_queue(venue=self.venue,
                                                            cylinder=label), "queue should be empty, for this test to make sense"

        process.start()
        sleep(.5)

        self.assertTrue(process.is_alive(),
                        "Process should still be alive, because the dequeue() is blocking and there's no data ")
        # now let's add something to the queue and see if the process finishes
        self.adapter.atomic_cylinders_enqueue(venue=self.venue, cylinders_dikt={label: "random data"})
        process.join(timeout=.2)  # wait for the process 0.2 seconds to finish
        self.assertFalse(process.is_alive(), "The dequeue() should have returned")
        self.assertEqual(0, process.exitcode, "Process should exit with zero code to indicate it was successful")

    def deplete_all_queues(self, depleter):
        """
        lambda, which takes just a label, and will dequeue from the queue with this label
        :param depleter:
        :return:
        """
        for label, input_list in zip(self.labels, self.input_lists):
            for el in input_list:
                dequeued = depleter(label)
                self.assertEqual(el, json.loads(dequeued))

        self.ensure_all_queues_empty()

    def ensure_all_queues_empty(self):
        for label in self.labels:
            q_size = self.adapter.get_size_of_cylinder_queue(venue=self.venue, cylinder=label)
            assert q_size == 0, "failed to deplete queue [%s]" % key(self.venue, label)


class TestStoredPredictionsRedisAdapter(TestCase):
    def setUp(self):
        self.default_set_of_predictions = "this will normally be a json string with a map b/w datatime and an int prediction"
        self.default_venue = "agora"
        self.default_datetime_newest_training_data = dt.now().replace(microsecond=0)

        # the key for the predictions we stored
        self.key_for_oldest_predictions = self.add_set_of_predictions(offset_in_hours=0)

    @classmethod
    def setUpClass(cls):
        configure_redis_for_testing()
        cls.adapter = StoredPredictionsAdapter()
        cls.adapter.drop_db()
        cls.raw_redis_client = cls.adapter.r

    def tearDown(self):
        self.adapter.drop_db()

    def test_store_predictions(self):
        self.assertTrue(self.raw_redis_client.exists(self.key_for_oldest_predictions),
                        "The set of predictions was not added under the expected key")
        self.assertIsNotNone(self.raw_redis_client.get(self.key_for_oldest_predictions),
                             "There's not content under key: %s" % self.key_for_oldest_predictions)

    def test_add_avaialable_predictions(self):
        key_of_auxiliary_data_structure = key(self.default_venue, StoredPredictionsAdapter._predictions_stack_tag)
        self.assertEqual(1, self.raw_redis_client.llen(key_of_auxiliary_data_structure),
                         "The auxilary list for the venue, doesn't any keys of predicitons for the venue")

        self.assertEqual(self.key_for_oldest_predictions, self.raw_redis_client.lpop(key_of_auxiliary_data_structure),
                         "The auxilary list for the venue, doesn't have the correct key of the newest prediciton")

    def test_get_keys_of_available_predictions_for_venue(self):
        # add new predictions for the venue
        key_of_new_predictions = self.add_set_of_predictions(offset_in_hours=1)
        self.assertEqual(key_of_new_predictions,
                         self.adapter.get_keys_of_available_predictions_for_venue(venue=self.default_venue)[0],
                         "the data structure hasn't got the key of the newest set of predictions")

        self.assertEqual(self.key_for_oldest_predictions,
                         self.adapter.get_keys_of_available_predictions_for_venue(venue=self.default_venue)[1],
                         "the data structure hasn't got the key of the originally added set of predictions")

    def test_get_key_of_newest_predictions(self):
        key_of_new_predictions = self.add_set_of_predictions(offset_in_hours=1)
        self.assertEqual(key_of_new_predictions, self.adapter.get_key_of_newest_predictions(venue=self.default_venue),
                         "The returned key doesn't match the key of the expected newest set of prediction")

    def test_get_dt_from_key(self):
        self.assertEqual(self.default_datetime_newest_training_data,
                         self.adapter.get_datetime_part_of_key(self.key_for_oldest_predictions))

    def test_get_predictions(self):
        # we've added predictions in the construct and the key under which they are stored.

        prediction_dt, predictions = self.adapter.get_predictions(predictions_key=self.key_for_oldest_predictions)

        self.assertEqual(self.default_datetime_newest_training_data, prediction_dt,
                         "The timestamp of the newest entry used to train the predictor model doesn't match the expected one")
        self.assertEqual(predictions, self.default_set_of_predictions)

    def add_set_of_predictions(self, offset_in_hours):
        """
        Add a new prediction for the default venue.
        :param offset_in_hours: with how many hours to increase the datetime from the initially added predictions set.
        :return: the key of the newly stored set of predictions
        """
        new_dt = self.default_datetime_newest_training_data + td(hours=offset_in_hours)
        self.adapter.store_predictions(venue=self.default_venue,
                                       # well it's the same but the content doesn't really matter
                                       predictions=self.default_set_of_predictions,
                                       datetime_newest_training=new_dt)

        key_of_new_predictions = key(self.default_venue, new_dt.replace(microsecond=0).isoformat())
        return key_of_new_predictions
