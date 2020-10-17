from __future__ import annotations
from typing import List, TYPE_CHECKING, TypedDict, cast

from bson import ObjectId

from core.entities.common import MetagraphEntityType, MetagraphEntity, PersistableMGEntity, Attributes

if TYPE_CHECKING:
    from core.metagraph import MetagraphPersist
    from core.entities.edge import BaseMetaedge


class BaseMetavertex(MetagraphEntity):
    entity_type = MetagraphEntityType.VERTEX
    inner_edges: List[BaseMetaedge]
    outer_edges: List[BaseMetaedge]
    children: List[BaseMetavertex]
    parents: List[BaseMetavertex]
    attrs: Attributes

    def __init__(self, name: str, attrs: Attributes = Attributes()) -> None:
        super().__init__(name)

        self.children = []
        self.inner_edges = []
        self.outer_edges = []
        self.parents = []
        self.attrs = attrs

    @property
    def has_dependencies(self):
        return len(self.inner_edges) > 0 or \
               len(self.outer_edges) > 0 or \
               len(self.children) > 0 or \
               len(self.parents) > 0

    @property
    def is_root(self):
        return len(self.parents) == 0

    @property
    def is_leaf(self):
        return len(self.children) == 0

    def add_child(self, child: BaseMetavertex):
        child.add_parent(self)

        self.children.append(child)

    def add_parent(self, parent: BaseMetavertex):
        if parent not in self.parents:
            self.parents.append(parent)

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

    def find_children(self, filters={}):
        filtered_children = []

        this_children = list(filter(lambda x: x.attrs.filter(filters), self.children))
        filtered_children.extend(this_children)

        for v in this_children:
            filtered_children.extend(v.find_children(filters))

        return filtered_children

    def find_parents(self, filters={}):
        filtered_parents = []

        this_parents = list(filter(lambda x: x.attrs.filter(filters), self.parents))
        filtered_parents.extend(this_parents)

        for v in this_parents:
            filtered_parents.extend(v.find_parents(filters))

        return list(set(filtered_parents))


class MetavertexType(TypedDict):
    _id: ObjectId
    name: str
    children: List[ObjectId]
    parents: List[ObjectId]
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

    def add_parent(self, parent: BaseMetavertex):
        self.set_dirty(True)
        super().add_parent(parent)

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
            "parents": list(map(lambda p: p.id, self.parents)),
            "attrs": self.attrs.serialize()
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
            if self.parents:
                for parent in self.parents:
                    cast(Metavertex, parent).save()

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
    def deserialize(json: MetavertexType, mg) -> Metavertex:
        mv = Metavertex(name=json["name"])
        mv.set_id(json["_id"])

        for child_id in json["children"]:
            child = mg.vertices[child_id]
            mv.add_child(child)

        mv.set_dirty(False)

        return mv

    # Загрузка по цепочке из базы только нужных элементов
    @staticmethod
    def load(mg: MetagraphPersist, _id: ObjectId) -> Metavertex:
        from core.entities.edge import Metaedge

        if mg.vertices.get(_id, None):
            return cast(Metavertex, mg.vertices[_id])

        vertex_data: MetavertexType = mg.vertices_collection.find_one({
            "_id": _id
        })

        if vertex_data['children']:
            for child_id in vertex_data['children']:
                if not mg.vertices.get(child_id, None):
                    child = Metavertex.load(mg, child_id)
                    mg.vertices[child.id] = child

        mv = Metavertex.deserialize(vertex_data, mg)
        mg.vertices[mv.id] = mv

        if vertex_data['parents']:
            for parent_id in vertex_data['parents']:
                if not mg.vertices.get(parent_id, None):
                    parent = Metavertex.load(mg, parent_id)
                    mg.vertices[parent.id] = parent

        for edge_id in vertex_data['outer_edges']:
            Metaedge.load(mg, edge_id)
        for edge_id in vertex_data['inner_edges']:
            Metaedge.load(mg, edge_id)

        return mv
