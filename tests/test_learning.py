from __future__ import absolute_import
from thesis_common.learning_pipeline import VenueMeasurementDetached, Label, LearningMode
from thesis_common import CustomJsonEncoder, deserialize_obj_hook
from thesis_common import VenueInformation
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
        json_str = json.dumps([obj], cls=CustomJsonEncoder)

        deserialized = json.loads(json_str, object_hook=deserialize_obj_hook)[0]
        self.assertEqual(num_people, deserialized.number_of_people)
        self.assertEqual(now, deserialized.timestamp_local)
        self.assertEqual(venue_name, deserialized.venue_name)
        self.assertEqual(capacity, deserialized.venue_capacity)


class TestEnums(TestCase):
    def test_serialize(self):
        label_dikt = {}
        for lbl in Label:
            label_dikt[str(lbl)] = lbl
        mode_dikt = {}
        for mode in LearningMode:
            mode_dikt[str(mode)] = mode

        dikt = {
            "labels": label_dikt,
            "modes": mode_dikt
        }
        json_str = json.dumps(dikt, cls=CustomJsonEncoder)
        dikt_deserialized = json.loads(json_str, object_hook=deserialize_obj_hook)
        for lbl in Label:
            self.assertIn(str(lbl), dikt_deserialized['labels'])
            self.assertEqual(lbl, dikt_deserialized['labels'][str(lbl)])
        for mode in LearningMode:
            self.assertIn(str(mode), dikt_deserialized['modes'])
            self.assertEqual(mode, dikt_deserialized['modes'][str(mode)])


class TestPublicDataTypes(TestCase):
    def test_venue_information(self):
        now = dt.now()
        venue_info = VenueInformation(newest_measurement_dt_local=now, newest_measurement_dt_utc=now,
                                      oldest_measurement_dt_local=now, oldest_measurement_dt_utc=now,
                                      number_of_entries=1, venue_capacity=200)
        json_str = json.dumps(venue_info, cls=CustomJsonEncoder)
        deser = json.loads(json_str, object_hook=deserialize_obj_hook)

        self.assertEqual(deser.newest_measurement_dt_local, now)
