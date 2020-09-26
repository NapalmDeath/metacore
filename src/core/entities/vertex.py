from __future__ import annotations
from typing import List, TYPE_CHECKING, TypedDict, cast

from bson import ObjectId

from core.entities.common import MetagraphEntityType, MetagraphEntity, PersistableMGEntity

if TYPE_CHECKING:
    from core.metagraph import MetagraphPersist
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

    @property
    def has_dependencies(self):
        return len(self.inner_edges) > 0 or \
               len(self.outer_edges) > 0 or \
               len(self.children) > 0 or\
               self.parent

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
    def set_mg(self, mg: MetagraphPersist):
        super().set_mg(mg)
        self.collection = self.mg.vertices_collection

    def add_child(self, child: BaseMetavertex):
        self.set_dirty(True)
        cast(Metavertex, child).set_dirty(True)

        super().add_child(child)

    def add_edge(self, edge: BaseMetaedge):
        self.set_dirty(True)
        super().add_edge(edge)

    def drop_edge(self, edge: BaseMetaedge):
        self.set_dirty(True)
        super().drop_edge(edge)

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

    def save(self):
        if not self.dirty:
            return

        is_first_save = not self.created

        super().save()
        self.set_dirty(False)

        # В случае, если меняем двойную связь (туда-обратно), например, родительская и дочерняя вершина
        # После сохранения дочерней, сохраняем родительскую и пересохраняем дочернюю
        was_changed_dependency = is_first_save and self.has_dependencies

        if is_first_save:
            if self.parent:
                self.parent.save()

            if self.children:
                for child in self.children:
                    cast(Metavertex, child).save()

            if self.inner_edges:
                for e in self.inner_edges:
                    cast("Metaedge", e).save()

            if self.outer_edges:
                for e in self.outer_edges:
                    cast("Metaedge", e).save()

        if was_changed_dependency:
            super().save()

    @staticmethod
    def load(json: MetavertexType, mg) -> Metavertex:
        mv = Metavertex(name=json["name"])
        mv.set_id(json["_id"])

        for child_id in json["children"]:
            child = mg.vertices[child_id]
            mv.add_child(child)
            child.parent = mv

        mv.set_dirty(False)

        return mv
