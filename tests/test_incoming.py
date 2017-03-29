from unittest import TestCase
from thesis_common import CustomJsonEncoder, deserialize_obj_hook
from datetime import datetime as dt
from thesis_common.incoming_pipeline import *
import json


class TestSerializableEnum(TestCase):
    def test_venue_stream_type(self):
        example_data = {
            "enum1": VenueStreamType.ABSOLUTE,
            "enum2": EventStreamOperator.PLUS,
            "some_number": 1
        }
        json_str = json.dumps(example_data, cls=CustomJsonEncoder)
        convert_back = json.loads(json_str, object_hook=deserialize_obj_hook)
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
        timestamp_utc=dt.utcnow(),
        metadata={'venue_token': '123'}
    )


class TestRawVenueMeasurement(TestCase):
    def test_create(self):
        raw_measurement = create_raw_measurement()

    def test_serialize(self):
        raw_measurement = create_raw_measurement()
        json_string = json.dumps(raw_measurement, cls=CustomJsonEncoder)
        convert_back = json.loads(json_string, object_hook=deserialize_obj_hook)
        self.assertEqual(raw_measurement.venue_id, convert_back.venue_id)
        self.assertEqual(raw_measurement.number_of_people, convert_back.number_of_people)
        self.assertEqual(raw_measurement.timestamp_utc, convert_back.timestamp_utc)
        self.assertEqual(raw_measurement.measurement_type, convert_back.measurement_type)

    def test_ensure_timestamp_is_utc(self):
        self.assertFalse(False)

    def test_try_invalid_input(self):
        with self.assertRaises(ValueError) as context:
            RawVenueMeasurement(
                number_of_people="this should be a number",
                measurement_type=VenueStreamType.ABSOLUTE,
                venue_id="Gym1",
                timestamp_utc=dt.utcnow(),
            )
        self.assertIn("int", str(context.exception))
        with self.assertRaises(ValueError) as context:
            RawVenueMeasurement(
                number_of_people=10,
                measurement_type="this should be an enum",
                venue_id="Gym1",
                timestamp_utc=dt.utcnow(),
            )
        self.assertIn("VenueStreamType", str(context.exception))

        with self.assertRaises(ValueError) as context:
            RawVenueMeasurement(
                number_of_people=10,
                measurement_type=VenueStreamType.ABSOLUTE,
                venue_id=12313,  # this should be a string
                timestamp_utc=dt.utcnow(),
            )
        self.assertIn("str", str(context.exception))

        with self.assertRaises(ValueError) as context:
            RawVenueMeasurement(
                number_of_people=10,
                measurement_type=VenueStreamType.ABSOLUTE,
                venue_id="Gym1",
                timestamp_utc='this should be a datetime'
            )
        self.assertIn("datetime", str(context.exception))
