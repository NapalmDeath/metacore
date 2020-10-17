from typing import List, cast

from bson import ObjectId

from core.agents.agent import BaseMetaAgent
from core.entities.common import Attributes
from core.entities.vertex import BaseMetavertex, Metavertex
from core.metagraph import MetagraphPersist
from text.utils import TextLevel, get_next_level
from nltk.tokenize import sent_tokenize, word_tokenize


def segment(text: str, level: TextLevel):
    if level == TextLevel.paragraph:
        return sent_tokenize(text)

    if level == TextLevel.sentence:
        return word_tokenize(text)


def is_leaf(v: Metavertex):
    return v.attrs.level == TextLevel.word


class TextFragmentationAgent(BaseMetaAgent):
    processed: List[ObjectId]
    to_process: List[Metavertex]
    mg: MetagraphPersist

    def __init__(self, mg: MetagraphPersist) -> None:
        super().__init__(mg)
        self.processed = []
        self.to_process = []

    def check_condition(self) -> bool:
        def check_vertex(v: Metavertex) -> bool:
            if v.id in self.processed or is_leaf(v):
                return False

            if v.is_root:
                return True

            if not v.attrs.get('processed'):
                return False

            return True

        self.to_process = list(filter(
            check_vertex,
            self.mg.vertices.values()
        ))

        return len(self.to_process) > 0

    def _run_vertex(self, v: BaseMetavertex):
        text, level = v.attrs.get('processed', v.attrs.text), v.attrs.level
        fragments = segment(text, level)

        next_level = get_next_level(level)

        for i, fragment in enumerate(fragments):
            mv = Metavertex(name="{}.{}.{}".format(v.name, next_level, i),
                            attrs=Attributes(text=fragment, level=next_level))
            v.add_child(mv)
            self.mg.register(mv)

    def run(self) -> None:
        for v in self.to_process:
            self._run_vertex(v)
            self.processed.append(v.id)
        self.to_process = []

    def __str__(self) -> str:
        return 'TextFragmentationAgent'
