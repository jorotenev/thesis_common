from enum import Enum
import inspect
import sys

"""
All enum classes used in this lib should be defined in this file, so that the `enum_classes()` can find them

"""


class SerializableEnum(Enum):
    """
    Abstract class for Enums to use. An enum extending this class is able to be serialized to json
    by the encoder/decoder in the json_serialize.py
    """


class VenueStreamType(SerializableEnum):
    """
    Describe the type of a venue in terms of the format of data we receive from the venue.
    If we receive te current number of people, then the ABSOLUTE stream type is appropriate.
    If we receive events (e..g 2 people left the venue), then the EVENT type is appropriate.
    absolute (123 people in the venue) or event (1 person entered)
    """

    ABSOLUTE = 'absolute'
    EVENT = 'event'


class EventStreamOperator(SerializableEnum):
    """
    When the data is of type VenueStreamType.EVENT, the event could be of two types - either 
    people walked into(PLUS) or walked out of the venue(MINUS).
    """
    PLUS = "plus"
    MINUS = "minus"


def enum_classes():
    """
    :return: returns all subclasses of SerializableEnum in this file (including SerializableEnum)
    """

    result = {}
    for enumName, enumCls in inspect.getmembers(sys.modules[__name__], inspect.isclass):
        if issubclass(enumCls, SerializableEnum):
            result[enumName] = enumCls
    return result
