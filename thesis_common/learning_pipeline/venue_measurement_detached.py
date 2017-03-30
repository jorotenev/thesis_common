from thesis_common.common import make_class_serializable


class VenueMeasurementDetached(object):
    def __init__(self, number_of_people, timestamp_local, venue_capacity, venue_name):
        """

        :param number_of_people:
        :type int
        :param timestamp_local: localized datetime (i.e. not UTC)
        :type datetime.datetime
        :param venue_name: the name of the venue (can be used to uniquely identify a venue in the Historical DB.
        :type str
        :param venue_capacity - how many people the venue can fit
        :type int
        """
        self.number_of_people = number_of_people
        self.timestamp_local = timestamp_local
        self.venue_capacity = venue_capacity
        self.venue_name = venue_name


make_class_serializable(VenueMeasurementDetached)
