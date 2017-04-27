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

    @property
    def label(self):
        return self.number_of_people

    @property
    def datetime(self):
        return self.timestamp_local


def venue_measurements_from_csv(abs_filepath, venue_capacity=500):
    """
    Given a csv file with `datetime,venue_name,amount` headers,
    return a list of VenueMeasurementDetached objects for each line of the file.

    :param abs_filepath: path to a csv file
    :param venue_capacity: int
    :return: list of VenueMeasurementDetached objects
    """
    from dateutil.parser import parse
    import csv
    with open(abs_filepath, 'r') as f:
        reader = csv.reader(f)
        headers = next(reader)
        assert 'datetime' in headers and 'amount' in headers and 'venue_name' in headers

        # sf = ground_data(file_abs_path=abs_filepath)
        result = []
        for row in reader:
            dt = parse(row[0])
            venue_name = row[1]
            amount = int(row[2])
            vm = VenueMeasurementDetached(venue_name=venue_name,
                                          number_of_people=amount,
                                          venue_capacity=venue_capacity,
                                          timestamp_local=dt)
            assert hasattr(vm, 'datetime')
            assert hasattr(vm, 'label')
            yield vm


make_class_serializable(VenueMeasurementDetached)
