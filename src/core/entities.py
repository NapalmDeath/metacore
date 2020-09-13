from typing import List
from core.common import PersistableMGEntity, MetagraphEntity, MetagraphEntityType, Attributes


class BaseMetavertex(MetagraphEntity):
    entity_type = MetagraphEntityType.VERTEX
    inner_edges: List["BaseMetaedge"] = []
    outer_edges: List["BaseMetaedge"] = []
    children: List["BaseMetavertex"] = []

    def __init__(self, name: str) -> None:
        super().__init__()

        self.name = name

    def add_child(self, child: "BaseMetavertex"):
        self.children.append(child)

    def add_edge(self, edge: "BaseMetaedge"):
        if self == edge.source:
            self.outer_edges.append(edge)
        if self == edge.dest:
            self.inner_edges.append(edge)


class Metavertex(BaseMetavertex, PersistableMGEntity):
    def serialize(self):
        return {
            "name": self.name,
            "children": list(map(lambda c: c.id, self.children))
        }


class BaseMetaedge(MetagraphEntity):
    entity_type = MetagraphEntityType.EDGE

    attrs: Attributes
    source: BaseMetavertex
    dest: BaseMetavertex

    # Вершина, хранящая данные
    inner_metavertex: "MetaedgeMetavertex"

    def __init__(self, name: str, source: BaseMetavertex, dest: BaseMetavertex, **attrs):
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


class MetaedgeMetavertex(Metavertex):
    parent_edge: "Metaedge"

    def serialize(self):
        base_data = super().serialize()

        return {
            **base_data,
            "parent_edge": self.parent_edge.id
        }


class Metaedge(BaseMetaedge, PersistableMGEntity):
    def serialize(self) -> dict:
        return {
            "name": self.name,
            **self.attrs.serialize()
        }