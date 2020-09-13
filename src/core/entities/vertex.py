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

    def __init__(self, name: str) -> None:
        super().__init__(name)

        self.children = []
        self.inner_edges = []
        self.outer_edges = []

    def add_child(self, child: BaseMetavertex):
        self.children.append(child)

    def add_edge(self, edge: BaseMetaedge):
        if self == edge.source:
            self.outer_edges.append(edge)
        if self == edge.dest:
            self.inner_edges.append(edge)


class MetavertexType(TypedDict):
    _id: ObjectId
    name: str
    children: List[ObjectId]
    inner_edges: List[ObjectId]
    outer_edges: List[ObjectId]


class Metavertex(BaseMetavertex, PersistableMGEntity):
    def serialize(self):
        return {
            "name": self.name,
            "inner_edges": list(map(lambda e: e.id, self.inner_edges)),
            "outer_edges": list(map(lambda e: e.id, self.outer_edges)),
            "children": list(map(lambda c: c.id, self.children))
        }

    @staticmethod
    def load(json: MetavertexType, mg) -> Metavertex:
        mv = Metavertex(name=json["name"])
        mv.set_id(json["_id"])

        for child_id in json["children"]:
            child = mg.vertices[child_id]
            mv.add_child(child)

        return mv
