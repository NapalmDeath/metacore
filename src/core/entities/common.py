from __future__ import annotations
from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Any, TYPE_CHECKING

from bson import ObjectId
from pymongo.collection import Collection

if TYPE_CHECKING:
    from core.metagraph import Metagraph, MetagraphPersist


class MetagraphEntityType(Enum):
    VERTEX = 'vertex'
    EDGE = 'edge'


class EdgeType(Enum):
    INNER = 'inner'
    OUTER = 'outer'


class MetagraphEntity:
    temp_id: ObjectId
    entity_type: MetagraphEntityType
    name: str

    @property
    def id(self) -> ObjectId:
        return self.temp_id

    _metagraph: Metagraph

    def __init__(self, name: str = '') -> None:
        self.temp_id = ObjectId()
        self.name = name

    def delete(self):
        pass


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

    def delete_from(self, collection: Collection):
        return collection.delete_one({
            "_id": self._id
        })

    @staticmethod
    def delete_many_from(collection: Collection, *ids: ObjectId):
        return collection.delete_one({
            "_id": {"$in": ids}
        })


class PersistableMGEntity(MetagraphEntity, Persistable, metaclass=ABCMeta):
    mg: MetagraphPersist = None

    def set_mg(self, mg: MetagraphPersist):
        self.mg = mg
        return self

    @property
    def id(self) -> ObjectId:
        return self._id or self.temp_id

    @staticmethod
    @abstractmethod
    def load(json: Any, mg: Metagraph):
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
