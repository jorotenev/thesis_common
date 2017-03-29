# start import ensures that the enum is in the namespace so that getattr() works
import json
from datetime import datetime
import dateutil.parser
from .enums import _enum_classes

_registered_serializable_classes = []


def make_class_serializable(cls):
    """
    Call this method to make a class json-serializable.
    :param cls:
    :return:
    """
    global _registered_serializable_classes
    _registered_serializable_classes.append(cls)


class CustomJsonEncoder(json.JSONEncoder):
    """
    Custom class used together with json.dumps()
    http://stackoverflow.com/questions/24481852/serialising-an-enum-member-to-json
    http://stackoverflow.com/questions/3768895/how-to-make-a-class-json-serializable
    """

    def default(self, obj):
        # global _registered_serializable_classes
        if type(obj) in _enum_classes().values():
            return {"__enum__": str(obj)}
        if type(obj) in _registered_serializable_classes:
            return {_serialazable_cls_name(type(obj)): obj.__dict__}
        if type(obj) is datetime:
            return {"__datetime__": obj.isoformat()}
        return json.JSONEncoder.default(self, obj)


def deserialize_obj_hook(d):
    global _registered_serializable_classes
    # see if the d has a serialized class that we manage (list could be empty!)
    managed_classes_in_dikt = [cls for cls in _registered_serializable_classes if _serialazable_cls_name(cls) in d]

    if "__enum__" in d:
        name, member = d["__enum__"].split(".")
        return getattr(_enum_classes()[name], member)
    elif managed_classes_in_dikt:
        assert len(managed_classes_in_dikt) is 1
        managed_serializeable_klass = managed_classes_in_dikt[0]  # there should be only one class, so take it

        dikt = d[_serialazable_cls_name(managed_serializeable_klass)]
        # initialise an instance of the class and return it
        return managed_serializeable_klass(**dikt)
    elif "__datetime__" in d:
        return dateutil.parser.parse(d['__datetime__'])
    else:
        return d


def _serialazable_cls_name(cls):
    return "__%s__" % cls.__name__
