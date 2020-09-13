from __future__ import annotations
from typing import List, Any, TYPE_CHECKING

from core.entities.common import MetagraphEntityType, MetagraphEntity, PersistableMGEntity

if TYPE_CHECKING:
    from core.entities.edge import BaseMetaedge


class BaseMetavertex(MetagraphEntity):
    entity_type = MetagraphEntityType.VERTEX
    inner_edges: List[BaseMetaedge] = []
    outer_edges: List[BaseMetaedge] = []
    children: List[BaseMetavertex] = []

    def __init__(self, name: str) -> None:
        super().__init__()

        self.name = name

    def add_child(self, child: BaseMetavertex):
        self.children.append(child)

    def add_edge(self, edge: BaseMetaedge):
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

    @staticmethod
    def load(json: Any) -> Metavertex:
        pass