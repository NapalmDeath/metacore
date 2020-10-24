from typing import List
import spacy

from bson import ObjectId

from core.agents.agent import BaseMetaAgent
from core.entities import Metavertex, Metaedge
from core.entities.common import Attributes
from core.entities.vertex import BaseMetavertex
from core.metagraph import MetagraphPersist
from text.utils import TextLevel, MVAttr, TextMVType, MEAttr, debug

nlp = spacy.load("en_core_web_sm")


def fetch_syntax(sentence):
    doc = nlp(sentence)
    return doc


class TextSyntaxAgent(BaseMetaAgent):
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
                      not v.is_leaf and
                      v.id not in self.processed,
            self.mg.vertices.values()
        ))

        return len(self.to_process) > 0

    def _run_vertex(self, v: BaseMetavertex) -> None:
        syntax = fetch_syntax(v.attrs.get(MVAttr.text))

        for i, token in enumerate(syntax):
            word_vertex = next(filter(lambda x: x.attrs.get(MVAttr.token_index) == token.i, v.children), None)
            head_vertex = next(filter(lambda x: x.attrs.get(MVAttr.token_index) == token.head.i, v.children), None)

            if not (word_vertex and head_vertex) or word_vertex == head_vertex:
                continue

            edge = Metaedge('{}.{}.{}'.format(token.dep_, token.head.text, token.text), head_vertex, word_vertex, **{
                MEAttr.oriented: True
            })

            word_vertex.attrs.set(MVAttr.syntax_parsed, True)
            head_vertex.attrs.set(MVAttr.syntax_parsed, True)

            self.mg.register(edge)

    def run(self) -> None:
        for v in self.to_process:
            self._run_vertex(v)
            self.processed.append(v.id)
        self.to_process = []

    def __str__(self) -> str:
        return 'SyntaxAgent'
