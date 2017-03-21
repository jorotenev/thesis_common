# start import ensures that the enum is in the namespace so that getattr() works
import dateutil.parser

from .enums import *
from .raw_venue_measurement import RawVenueMeasurement
import json
from datetime import datetime


# Custom encoder and decoder

class CustomJsonEncoder(json.JSONEncoder):
    """
    Custom class used together with json.dumps()
    http://stackoverflow.com/questions/24481852/serialising-an-enum-member-to-json
    http://stackoverflow.com/questions/3768895/how-to-make-a-class-json-serializable
    """

    def default(self, obj):
        if type(obj) in enum_classes().values():
            return {"__enum__": str(obj)}
        if type(obj) is RawVenueMeasurement:
            return {"__" + str(RawVenueMeasurement.__name__) + "__": obj.__dict__}
        if type(obj) is datetime:
            return {"__datetime__": obj.isoformat()}
        return json.JSONEncoder.default(self, obj)


def as_enum(d):
    if "__enum__" in d:
        name, member = d["__enum__"].split(".")
        return getattr(enum_classes()[name], member)
    elif "__" + str(RawVenueMeasurement.__name__) + "__" in d:
        dikt = d["__" + str(RawVenueMeasurement.__name__) + "__"]
        return RawVenueMeasurement(**dikt)
    elif "__datetime__" in d:
        return dateutil.parser.parse(d['__datetime__'])
    else:
        return d
