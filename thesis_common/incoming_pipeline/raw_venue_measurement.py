"""
In this file we provide constants, enums, and functions to operate on venue measurements.
The data used to construct the objects is the one we received from venues (i.e. "raw").
This 
"""
import datetime
from .enums import VenueStreamType, EventStreamOperator
from thesis_common import make_class_serializable


class RawVenueMeasurement(object):
    """
    Convenience data-class to hold a venue measurement.
    The purpose of this class is to encapsulate data that has just arrived at a gate,
    make it easy to searialize and deserialize the contents.
    """

    def __init__(self, venue_id, timestamp_utc, number_of_people, measurement_type, operator=None, metadata={}):
        """
        :param venue_id - the name of the venue. str.
        :param timestamp_utc - the UTC time at which the measurement was made. datetime
        :param measurement_type - the type of data - i.e. gyms send events, bibs send absolute number of people
        :type VenueStreamType
        :param number_of_people - the number of people for this measurement (for VenueStreamType.ABSOLUTE this will be
        the number of people at the venue, for EVENT the number of people for which the event occurred.)
        :type int
        :param operator - only needed if `measurement_type` is STREAM, not needed if it is ABSOLUTE.
        in the case of stream of type event, the operator says if we should add/subtract :number_of_people
        :type EventStreamOperator
        :param metadata - any additional metadata
        :type dict
        :raises ValueError - if the arguments passed are invalid
        """

        self.venue_id = venue_id
        self.timestamp_utc = timestamp_utc
        self.measurement_type = measurement_type
        self.operator = operator
        self.number_of_people = number_of_people
        self.metadata = metadata

        # raise an exception if input data is not good
        self._validate_input()

    def _validate_input(self):
        """
       Used to check if the state of the object is valid

       `measurement` can be a dict of two shapes:
       * if measurement_type is ABSOLUTE, then
       {
           NUMBER_OF_PEOPLE: <int>
       }
       * if measurement_type is EVENT, then
       {
           EVENT_OPERATOR_KEY: <EVENT_OPERATOR_PLUS | EVENT_OPERATOR_MINUS >
           NUMBER_OF_PEOPLE: int
       }
       :param raw_measurement:
       :return: nothing. will silently return if :event validates
       """

        try:
            expected_type(str, self.venue_id, "venue_id")
            expected_type(datetime.datetime, self.timestamp_utc, "timestamp_utc")

            expected_type(VenueStreamType, self.measurement_type, "measurement_type")

            expected_type(int, self.number_of_people, "number_of_people")

            if self.measurement_type is VenueStreamType.ABSOLUTE:
                if self.operator:
                    raise ValueError("The stream type for the venue doesn't allow passing an Event operator")

            elif self.measurement_type is VenueStreamType.EVENT:
                expected_type(EventStreamOperator, self.operator, "operator")
            else:
                raise ValueError("Unsupported member of the VenueStreamType enum")

            if self.metadata:
                expected_type(dict, self.metadata, "metadata")

        except Exception as ex:
            raise ValueError("Validation of input failed. Reason: %s" % str(ex))


def expected_type(expected, variable, var_name):
    """
    Verify the type of a variable
    :param expected: type
    :param variable: some variable
    :param var_name: the name of the variable, for readibility
    :return: None
    :raises TypeErorr - if type(variable) != :expected
    """
    if type(variable) is not expected:
        raise TypeError(
            "{variable_name} should be {expected_class}. Actual type: {actual_type}".format(
                variable_name=var_name,
                expected_class=str(expected.__name__),
                actual_type=type(variable).__name__))


make_class_serializable(RawVenueMeasurement)
