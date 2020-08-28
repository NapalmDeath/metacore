from abc import ABCMeta, abstractmethod, abstractproperty
from enum import Enum
from typing import Any

from bson import ObjectId


class MetagraphEntity(Enum):
    VERTEX = 'vertex'
    EDGE = 'edge'


class EdgeType(Enum):
    INNER = 'inner'
    OUTER = 'outer'


class Serializable(metaclass=ABCMeta):
    entity_type: MetagraphEntity

    _id: ObjectId or None = None

    @property
    def id(self) -> ObjectId or None:
        return self._id

    @property
    def created(self) -> bool:
        return self._id is not None

    def set_id(self, _id: ObjectId):
        self._id = _id

    @abstractmethod
    def serialize(self) -> dict:
        pass


class Attributes(Serializable):
    values: dict = {}

    def __init__(self, **kwargs) -> None:
        super().__init__()

        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def created(self) -> bool:
        return True

    def __getattr__(self, item) -> Any:
        return self.values[item]

    def __setattr__(self, key, value):
        self.values[key] = value

    def serialize(self) -> dict:
        return self.values



