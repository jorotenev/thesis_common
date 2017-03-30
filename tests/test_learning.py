from thesis_common.learning_pipeline import VenueMeasurementDetached
from thesis_common import CustomJsonEncoder, deserialize_obj_hook

from unittest import TestCase
from datetime import datetime as dt
import json


class TestVenueMeasurementDetached(TestCase):
    def test_obj_serialize(self):
        num_people = 10
        capacity = 100
        venue_name = "Gym1"
        now = dt.now()
        obj = VenueMeasurementDetached(number_of_people=num_people,
                                       timestamp_local=now,
                                       venue_name=venue_name,
                                       venue_capacity=capacity)
        json_str = json.dumps(obj, cls=CustomJsonEncoder)

        deserialized = json.loads(json_str, object_hook=deserialize_obj_hook)
        self.assertEqual(num_people, deserialized.number_of_people)
        self.assertEqual(now, deserialized.timestamp_local)
        self.assertEqual(venue_name, deserialized.venue_name)
        self.assertEqual(capacity, deserialized.venue_capacity)
