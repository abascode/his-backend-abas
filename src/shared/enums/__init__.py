from enum import Enum


class TableOrderEnum(Enum):
    asc = "asc"
    desc = "desc"


class Database(Enum):
    VEHICLE_ALLOCATION = "vehicle_allocation"
