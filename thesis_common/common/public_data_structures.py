from . import make_class_serializable


class VenueInformation(object):
    """
    Brief information about the data the Historical API has about a venue
    """

    def __init__(self, oldest_measurement_dt_utc, newest_measurement_dt_utc, number_of_entries):
        self.oldest_measurement_dt_utc = oldest_measurement_dt_utc
        self.newest_measurement_dt_utc = newest_measurement_dt_utc
        self.number_of_entries = number_of_entries


make_class_serializable(VenueInformation)
