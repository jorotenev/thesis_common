import enum

from thesis_common import SerializableEnum, make_enum_serialazable


class Label(SerializableEnum):
    """
    E.g. label daily on a cylinder means that this cylinder operates on data with scope day
    E.g. label daily on a kNN model means that the model is trained with data from a cylinder with a matching label
    """
    daily = 'daily_label'
    weekly = "weekly_label"


class LearningMode(SerializableEnum):
    """
    We either run an experiment (e.g. to measure the performance of our learning pipeline
    or we run in a "live" mode - e.g. when we run in production
    """
    live = 'live_learning_mode'
    simulation = 'simulaiton_learning_mode'


make_enum_serialazable(__name__)
