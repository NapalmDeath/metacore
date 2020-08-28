from typing import List

from bson import ObjectId

from core.common import Serializable, MetagraphEntity, Attributes


class Metavertex(Serializable):
    entity_type = MetagraphEntity.VERTEX

    name: str
    inner_edges: List["Metaedge"] = []
    outer_edges: List["Metaedge"] = []
    children: List["Metavertex"] = []

    def __init__(self, name: str, _id: ObjectId = None) -> None:
        self.name = name
        self._id = _id

    def add_child(self, child: "Metavertex"):
        self.children.append(child)

    def add_edge(self, edge: "Metaedge"):
        if self == edge.source:
            self.outer_edges.append(edge)
        if self == edge.dest:
            self.inner_edges.append(edge)

    def serialize(self):
        return {
            "name": self.name,
            "children": list(map(lambda c: c.id, self.children))
        }


class Metaedge(Serializable):
    entity_type = MetagraphEntity.EDGE

    name: str
    attrs: Attributes
    source: Metavertex
    dest: Metavertex

    def __init__(self, name: str, source: Metavertex, dest: Metavertex, **attrs):
        super().__init__()

        self.name = name
        self.source = source
        self.dest = dest
        self.attrs = Attributes(**attrs)

        self.source.add_edge(self)
        self.dest.add_edge(self)

    def __getattr__(self, item):
        if not self.attrs:
            raise AttributeError

        return self.attrs[item]

    def serialize(self) -> dict:
        return {
            "name": self.name,
            **self.attrs.serialize()
        }
