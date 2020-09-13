from __future__ import annotations
from typing import Any, TYPE_CHECKING, TypedDict, Dict

from bson import ObjectId

from core.entities.common import MetagraphEntity, MetagraphEntityType, Attributes, PersistableMGEntity

if TYPE_CHECKING:
    from core.metagraph import Metagraph
    from core.entities.vertex import BaseMetavertex


class BaseMetaedge(MetagraphEntity):
    entity_type = MetagraphEntityType.EDGE

    attrs: Attributes
    source: BaseMetavertex
    dest: BaseMetavertex

    def __init__(self, name: str, source: BaseMetavertex, dest: BaseMetavertex, **attrs):
        super().__init__(name)

        self.source = source
        self.dest = dest
        self.attrs = Attributes(**attrs)

        self.source.add_edge(self)
        self.dest.add_edge(self)

    def __getattr__(self, item):
        if not self.attrs:
            raise AttributeError

        return self.attrs[item]


class MetaedgeType(TypedDict):
    _id: ObjectId
    name: str
    source: ObjectId
    dest: ObjectId
    attrs: Dict


class Metaedge(BaseMetaedge, PersistableMGEntity):
    def serialize(self) -> dict:
        return {
            "name": self.name,
            "source": self.source.id,
            "dest": self.dest.id,
            "attrs": self.attrs.serialize()
        }

    @staticmethod
    def load(json: MetaedgeType, mg: Metagraph) -> Metaedge:
        source = mg.vertices[json["source"]]
        dest = mg.vertices[json["dest"]]

        me = Metaedge(name=json["name"], source=source, dest=dest, **json["attrs"])
        me.set_id(json["_id"])

        return me
