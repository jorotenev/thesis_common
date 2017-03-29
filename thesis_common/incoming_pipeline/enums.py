from thesis_common import SerializableEnum, make_enum_serialazable


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


make_enum_serialazable(__name__)
