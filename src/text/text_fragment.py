from typing import List, cast

from bson import ObjectId
from spacy.lang.en import English

from core.agents.agent import BaseMetaAgent
from core.entities.common import Attributes
from core.entities.vertex import BaseMetavertex, Metavertex
from core.metagraph import MetagraphPersist
from text.utils import TextLevel, get_next_level, MVAttr

nlp = English()
nlp.add_pipe(nlp.create_pipe('sentencizer'))


def segment(text: str, level: TextLevel):
    if level == TextLevel.paragraph:
        doc = nlp(text)
        sentences = [sent.string.strip() for sent in doc.sents]
        return sentences

    if level == TextLevel.sentence:
        doc = nlp(text)
        return [token.text for token in doc]


def is_leaf(v: Metavertex):
    return v.attrs.get(MVAttr.level, None) == TextLevel.word


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

            if not v.attrs.get(MVAttr.processed):
                return False

            return True

        self.to_process = list(filter(
            check_vertex,
            self.mg.vertices.values()
        ))

        return len(self.to_process) > 0

    def _run_vertex(self, v: BaseMetavertex):
        text, level = v.attrs.get(MVAttr.processed, v.attrs.get(MVAttr.text)), v.attrs.get(MVAttr.level)
        fragments = segment(text, level)

        next_level = get_next_level(level)

        for i, fragment in enumerate(fragments):
            mv = Metavertex(name="{}.{}.{}".format(v.name, next_level, i),
                            attrs=Attributes(
                                **{MVAttr.text: fragment, MVAttr.level: next_level, MVAttr.token_index: i}))
            v.add_child(mv)
            self.mg.register(mv)

    def run(self) -> None:
        for v in self.to_process:
            self._run_vertex(v)
            self.processed.append(v.id)
        self.to_process = []

    def __str__(self) -> str:
        return 'TextFragmentationAgent'
