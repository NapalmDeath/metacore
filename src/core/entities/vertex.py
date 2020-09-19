from __future__ import annotations
from typing import List, Any, TYPE_CHECKING, TypedDict

from bson import ObjectId

from core.entities.common import MetagraphEntityType, MetagraphEntity, PersistableMGEntity

if TYPE_CHECKING:
    from core.entities.edge import BaseMetaedge


class BaseMetavertex(MetagraphEntity):
    entity_type = MetagraphEntityType.VERTEX
    inner_edges: List[BaseMetaedge]
    outer_edges: List[BaseMetaedge]
    children: List[BaseMetavertex]
    parent: BaseMetavertex or None

    def __init__(self, name: str) -> None:
        super().__init__(name)

        self.children = []
        self.inner_edges = []
        self.outer_edges = []
        self.parent = None

    def add_child(self, child: BaseMetavertex):
        child.parent = self
        self.children.append(child)

    def add_edge(self, edge: BaseMetaedge):
        if self == edge.source:
            self.outer_edges.append(edge)
        if self == edge.dest:
            self.inner_edges.append(edge)

    def drop_edge(self, edge: BaseMetaedge):
        self.inner_edges = list(filter(lambda e: e.id != edge.id, self.inner_edges))
        self.outer_edges = list(filter(lambda e: e.id != edge.id, self.outer_edges))

    def delete(self):
        for edge in self.inner_edges:
            edge.delete()
        for edge in self.outer_edges:
            edge.delete()


class MetavertexType(TypedDict):
    _id: ObjectId
    name: str
    children: List[ObjectId]
    inner_edges: List[ObjectId]
    outer_edges: List[ObjectId]


class Metavertex(BaseMetavertex, PersistableMGEntity):
    def delete(self):
        edges_to_delete = [*self.inner_edges, *self.outer_edges]

        for edge in edges_to_delete:
            edge.delete()

        if self.mg:
            self.delete_many_from(self.mg.edges_collection, *map(lambda e: e.id, edges_to_delete))
            self.delete_from(self.mg.vertices_collection)

    def serialize(self):
        return {
            "name": self.name,
            "inner_edges": list(map(lambda e: e.id, self.inner_edges)),
            "outer_edges": list(map(lambda e: e.id, self.outer_edges)),
            "children": list(map(lambda c: c.id, self.children)),
            "parent": self.parent.id if self.parent else None
        }

    @staticmethod
    def load(json: MetavertexType, mg) -> Metavertex:
        mv = Metavertex(name=json["name"])
        mv.set_id(json["_id"])

        for child_id in json["children"]:
            child = mg.vertices[child_id]
            mv.add_child(child)
            child.parent = mv

        return mv
