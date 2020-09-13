from typing import Dict

from bson import ObjectId
from pymongo import MongoClient
from pymongo.collection import Collection

from core.common import MetagraphEntityType, MetagraphEntity, PersistableMGEntity
from core.entities import Metavertex, Metaedge


class Metagraph:
    vertices: Dict[ObjectId, Metavertex] = {}
    edges: Dict[ObjectId, Metaedge] = {}

    def save_entities(self, *entities: MetagraphEntity):
        for e in entities:
            self.save_entity(e)

    def __get_collection(self, entity_type: MetagraphEntityType) -> Dict:
        return self.vertices if entity_type == MetagraphEntityType.VERTEX else self.edges

    def save_entity(self, entity: MetagraphEntity):
        collection = self.__get_collection(entity.entity_type)
        collection[entity.id] = entity


class MetagraphPersist(Metagraph):
    db: MongoClient
    vertices_collection: Collection
    edges_collection: Collection

    def __init__(self, db: MongoClient):
        self.db = db
        self.vertices_collection = db.vertices
        self.edges_collection = db.edges

    def save_entities(self, *entities: PersistableMGEntity):
        for e in entities:
            self.save_entity(e)

    def __get_collection(self, entity_type: MetagraphEntityType) -> Collection:
        return self.vertices_collection if entity_type == MetagraphEntityType.VERTEX else self.edges_collection

    def save_entity(self, entity: PersistableMGEntity):
        super(MetagraphPersist, self).save_entity(entity)

        collection = self.__get_collection(entity.entity_type)
        entity.save(collection)

    def load_all(self):
        v = self.vertices_collection.find()
        print(v)