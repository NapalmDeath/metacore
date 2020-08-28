from pymongo import MongoClient
from pymongo.collection import Collection

from core.common import Serializable, MetagraphEntity


class Metagraph:
    db: MongoClient
    vertices: Collection
    edges: Collection

    def __init__(self, db: MongoClient):
        self.db = db
        self.vertices = db.vertices
        self.edges = db.edges

    def save_entities(self, *entities: Serializable):
        for e in entities:
            self.save_entity(e)

    def save_entity(self, entity: Serializable):
        collection = self.vertices if entity.entity_type == MetagraphEntity.VERTEX else self.edges

        if not entity.created:
            result = collection.insert_one(entity.serialize())
            entity.set_id(result.inserted_id)
            return result
        else:
            return collection.update_one({
                "_id": entity.id
            }, {
                "$set": entity.serialize()
            })
