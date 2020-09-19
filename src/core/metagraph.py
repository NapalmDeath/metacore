from __future__ import annotations
from typing import Dict, TYPE_CHECKING, cast

from bson import ObjectId
from pymongo import MongoClient
from pymongo.collection import Collection

from core.entities.common import MetagraphEntityType, MetagraphEntity, PersistableMGEntity
from core.entities.vertex import Metavertex
from core.entities.edge import Metaedge

if TYPE_CHECKING:
    from core.entities.vertex import BaseMetavertex
    from core.entities.edge import BaseMetaedge


class Metagraph:
    vertices: Dict[ObjectId, BaseMetavertex]
    edges: Dict[ObjectId, BaseMetaedge]

    def __init__(self) -> None:
        super().__init__()
        self.vertices = {}
        self.edges = {}

    def save_entities(self, *entities: MetagraphEntity):
        for e in entities:
            self.save_entity(e)

    def _get_entity_collection(self, entity_type: MetagraphEntityType) -> Dict:
        return self.vertices if entity_type == MetagraphEntityType.VERTEX else self.edges

    def save_entity(self, entity: MetagraphEntity):
        collection = self._get_entity_collection(entity.entity_type)
        collection[entity.id] = entity

    def delete_entity(self, entity: MetagraphEntity):
        collection = self._get_entity_collection(entity.entity_type)
        del collection[entity.id]

        entity.delete()


class MetagraphPersist(Metagraph):
    db: MongoClient
    vertices_collection: Collection
    edges_collection: Collection

    def __init__(self, db: MongoClient):
        super(MetagraphPersist, self).__init__()

        self.db = db
        self.vertices_collection = db.vertices
        self.edges_collection = db.edges

    def save_entities(self, *entities: PersistableMGEntity):
        for e in entities:
            self.save_entity(e)

    def _get_db_collection(self, entity_type: MetagraphEntityType) -> Collection:
        return self.vertices_collection if entity_type == MetagraphEntityType.VERTEX else self.edges_collection

    def save_entity(self, entity: PersistableMGEntity):
        collection = self._get_db_collection(entity.entity_type)
        entity.save(collection)

        collection = self._get_entity_collection(entity.entity_type)

        if entity.temp_id in collection:
            del collection[entity.temp_id]

        collection[entity.id] = entity

        entity.set_mg(self)

    def delete_entity(self, entity: PersistableMGEntity):
        super().delete_entity(entity)

    def register(self, *entities: MetagraphEntity):
        for entity in entities:
            super().save_entity(entity)

    def load_all(self):
        all_vertices = list(self.vertices_collection.find())

        leaf_vertices = list(filter(lambda x: len(x["children"]) == 0, all_vertices))
        other_vertices = list(filter(lambda x: len(x["children"]) > 0, all_vertices))

        for vertices in [leaf_vertices, other_vertices]:
            for v in vertices:
                m = Metavertex.load(v, self)
                self.vertices[m.id] = m

        edges = list(self.edges_collection.find())

        for edge in edges:
            e = Metaedge.load(edge, self)
            self.edges[e.id] = e


