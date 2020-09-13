from __future__ import annotations
from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Any, TYPE_CHECKING

from bson import ObjectId
from pymongo.collection import Collection

if TYPE_CHECKING:
    from core.metagraph import Metagraph


class MetagraphEntityType(Enum):
    VERTEX = 'vertex'
    EDGE = 'edge'


class EdgeType(Enum):
    INNER = 'inner'
    OUTER = 'outer'


class MetagraphEntity:
    _temp_id: ObjectId
    entity_type: MetagraphEntityType
    name: str

    _metagraph: Metagraph

    @property
    def id(self) -> ObjectId or None:
        return self._temp_id

    def __init__(self) -> None:
        self._temp_id = ObjectId()


class Serializable(metaclass=ABCMeta):
    @abstractmethod
    def serialize(self) -> dict:
        pass


class Persistable(Serializable, metaclass=ABCMeta):
    _id: ObjectId or None = None

    @property
    def created(self) -> bool:
        return self._id is not None

    def set_id(self, _id: ObjectId):
        self._id = _id

    def save(self, collection: Collection):
        if not self.created:
            result = collection.insert_one(self.serialize())
            self.set_id(result.inserted_id)
            return result
        else:
            return collection.update_one({
                "_id": self._id
            }, {
                "$set": self.serialize()
            })


class PersistableMGEntity(MetagraphEntity, Persistable, metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def load(json: Any):
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
