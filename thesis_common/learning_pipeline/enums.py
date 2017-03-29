import enum
from thesis_common import make_enum_serialazable


class Label(enum.Enum):
    """
    E.g. label daily on a cylinder means that this cylinder operates on data with scope day
    E.g. label daily on a kNN model means that the model is trained with data from a cylinder with a matching label
    """
    daily = 'daily_label'
    weekly = "weekly_label"


make_enum_serialazable(__name__)
