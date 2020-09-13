from __future__ import annotations
from typing import Any, TYPE_CHECKING

from core.entities.common import MetagraphEntity, MetagraphEntityType, Attributes, PersistableMGEntity

if TYPE_CHECKING:
    from core.entities.vertex import BaseMetavertex


class BaseMetaedge(MetagraphEntity):
    entity_type = MetagraphEntityType.EDGE

    attrs: Attributes
    source: BaseMetavertex
    dest: BaseMetavertex

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


class Metaedge(BaseMetaedge, PersistableMGEntity):
    def serialize(self) -> dict:
        return {
            "name": self.name,
            **self.attrs.serialize()
        }

    @staticmethod
    def load(json: Any):
        pass
