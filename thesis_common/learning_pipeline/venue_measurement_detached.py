from thesis_common.common import make_class_serializable


class VenueMeasurementDetached(object):
    def __init__(self, number_of_people, timestamp_local):
        """

        :param number_of_people:
         :type int
        :param timestamp_local: localized datetime (i.e. not UTC)
         :type datetime.datetime
        """
        self.number_of_people = number_of_people
        self.timestamp_local = timestamp_local


make_class_serializable(VenueMeasurementDetached)
