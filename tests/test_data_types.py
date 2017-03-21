import json
import unittest
from unittest import TestCase
from venue_common import *
from datetime import datetime as dt


class TestSerializableEnum(TestCase):
    def test_venue_stream_type(self):
        example_data = {
            "enum1": VenueStreamType.ABSOLUTE,
            "enum2": EventStreamOperator.PLUS,
            "some_number": 1
        }
        json_str = json.dumps(example_data, cls=CustomJsonEncoder)
        convert_back = json.loads(json_str, object_hook=as_enum)
        self.assertIn("enum1", convert_back)
        self.assertIn("enum2", convert_back)
        self.assertIn("some_number", convert_back)
        self.assertEqual(VenueStreamType.ABSOLUTE, convert_back['enum1'])
        self.assertEqual(EventStreamOperator.PLUS, convert_back['enum2'])


def create_raw_measurement():
    return RawVenueMeasurement(
        number_of_people=10,
        measurement_type=VenueStreamType.ABSOLUTE,
        venue_id="Gym1",
        timestamp_utc=dt.utcnow()
    )


class TestRawVenueMeasurement(TestCase):
    def test_create(self):
        raw_measurement = create_raw_measurement()

    def test_serialize(self):
        raw_measurement = create_raw_measurement()
        json_string = json.dumps(raw_measurement, cls=CustomJsonEncoder)
        convert_back = json.loads(json_string, object_hook=as_enum)
        self.assertEqual(raw_measurement.venue_id, convert_back.venue_id)
        self.assertEqual(raw_measurement.number_of_people, convert_back.number_of_people)
        self.assertEqual(raw_measurement.timestamp_utc, convert_back.timestamp_utc)
        self.assertEqual(raw_measurement.measurement_type, convert_back.measurement_type)

    def test_ensure_timestamp_is_utc(self):
        self.assertFalse(False)
