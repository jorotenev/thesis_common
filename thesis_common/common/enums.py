from enum import Enum
import inspect
import sys

"""
All enum classes used in this lib should be defined in this file, so that the `enum_classes()` can find them

"""
# We allow all submodules to register their enums here
# This is needed because the json deserializer needs to have access to all
# enums when deserializing
_registered_enums = []


def make_enum_serialazable(module_name):
    """
    Call this function within a file which has defined Enums.
    This will enable the Enums to be serialized and deserializaed
    :param module_name: just pass __name__
    :return:
    """
    global _registered_enums
    for enumName, enumCls in inspect.getmembers(sys.modules[module_name], inspect.isclass):
        if issubclass(enumCls, SerializableEnum):
            _registered_enums.append(enumCls)


class SerializableEnum(Enum):
    """
    Abstract class for Enums to use. An enum extending this class is able to be serialized to json
    by the encoder/decoder in the json_serialize.p.
    See `export_enum_classes()`.
    """


def _enum_classes():
    """
    :return: returns all subclasses of SerializableEnum (including SerializableEnum)
    """

    result = {}
    for enumCls in _registered_enums:
        if issubclass(enumCls, SerializableEnum):
            result[enumCls.__name__] = enumCls
    return result
