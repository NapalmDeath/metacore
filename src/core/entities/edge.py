from __future__ import annotations
from typing import TYPE_CHECKING, TypedDict, Dict, cast

from bson import ObjectId

from core.entities.common import MetagraphEntity, MetagraphEntityType, Attributes, PersistableMGEntity

if TYPE_CHECKING:
    from core.metagraph import Metagraph, MetagraphPersist
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

    def delete(self):
        self.source.drop_edge(self)
        self.dest.drop_edge(self)


class MetaedgeType(TypedDict):
    _id: ObjectId
    name: str
    source: ObjectId
    dest: ObjectId
    attrs: Dict


class Metaedge(BaseMetaedge, PersistableMGEntity):
    def set_mg(self, mg: MetagraphPersist):
        super().set_mg(mg)
        self.collection = self.mg.edges_collection

    def delete(self):
        super(Metaedge, self).delete()

        if self.mg:
            self.mg.save_entities(cast('Metavertex', self.source), cast('Metavertex', self.dest))
            self.delete_from(self.mg.edges_collection)

    def save(self):
        if not self.dirty:
            return

        is_first_save = not self.created

        super().save()
        self.set_dirty(False)

        if is_first_save:
            source = cast("Metavertex", self.source)
            dest = cast("Metavertex", self.dest)

            was_changed_dependencies = not source.created or not dest.created

            source.save()
            dest.save()

            if was_changed_dependencies:
                super().save()

    def serialize(self) -> dict:
        return {
            "name": self.name,
            "source": self.source.id,
            "dest": self.dest.id,
            "attrs": self.attrs.serialize()
        }

    @staticmethod
    def deserialize(json: MetaedgeType, mg: Metagraph) -> Metaedge:
        source = mg.vertices[json["source"]]
        dest = mg.vertices[json["dest"]]

        me = Metaedge(name=json["name"], source=source, dest=dest, **json["attrs"])
        me.set_id(json["_id"])

        me.set_dirty(False)

        return me

    @staticmethod
    def load(mg: MetagraphPersist, _id: ObjectId) -> Metaedge:
        from core.entities.vertex import Metavertex

        if mg.edges.get(_id, None):
            return cast(Metaedge, mg.edges[_id])

        edge_data: MetaedgeType = mg.edges_collection.find_one({
            "_id": _id
        })

        Metavertex.load(mg, edge_data['source'])
        Metavertex.load(mg, edge_data['dest'])

        me = Metaedge.deserialize(edge_data, mg)
        mg.edges[_id] = me

        return me
