from typing import List
import spacy

from bson import ObjectId

from core.agents.agent import BaseMetaAgent
from core.entities import Metavertex
from core.entities.common import Attributes
from core.entities.vertex import BaseMetavertex
from core.metagraph import MetagraphPersist
from text.utils import TextLevel, MVAttr, TextMVType

nlp = spacy.load("en_core_web_sm")


def fetch_morphology(sentence):
    doc = nlp(sentence)
    return doc


class TextMorphologyAgent(BaseMetaAgent):
    processed: List[ObjectId]
    to_process: List[Metavertex]
    mg: MetagraphPersist

    def __init__(self, mg: MetagraphPersist) -> None:
        super().__init__(mg)
        self.processed = []
        self.to_process = []

    def check_condition(self) -> bool:
        self.to_process = list(filter(
            lambda v: v.attrs.get(MVAttr.level) == TextLevel.sentence and
                      v.id not in self.processed and
                      v.attrs.get(MVAttr.processed) and
                      all(
                          all((not child.attrs.get(MVAttr.mv_type) for child in token.children)) for token in
                          v.children
                      ),
            self.mg.vertices.values()
        ))

        return len(self.to_process) > 0

    def _run_vertex(self, v: BaseMetavertex) -> None:
        preprocessed_sentence = v.attrs.get(MVAttr.processed)
        morph = fetch_morphology(preprocessed_sentence)
        for token in morph:
            word_vertex = next(filter(lambda x: x.attrs.text == token.text, v.children), None)

            if word_vertex:
                morph_mv = Metavertex(name='{}.morph'.format(word_vertex.name),
                                      attrs=Attributes(
                                          **{MVAttr.mv_type: TextMVType.morph, MVAttr.text: token.text,
                                             MVAttr.lemma: token.lemma_,
                                             MVAttr.pos: token.pos_}))
                word_vertex.add_child(morph_mv)
                self.mg.register(morph_mv)

    def run(self) -> None:
        for v in self.to_process:
            self._run_vertex(v)
            self.processed.append(v.id)
        self.to_process = []

    def __str__(self) -> str:
        return 'MorphAgent'
