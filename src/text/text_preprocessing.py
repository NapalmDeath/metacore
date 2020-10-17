import re
import string
from typing import List

from bson import ObjectId
from nltk import word_tokenize
from nltk.corpus import stopwords

from core.agents.agent import BaseMetaAgent
from core.entities.vertex import BaseMetavertex, Metavertex
from core.metagraph import MetagraphPersist
from text.utils import TextLevel

stop_words = set(stopwords.words('english'))


def preprocess(text: str, level: TextLevel):
    result = text

    if level == TextLevel.sentence:
        result = result.lower()
        result = re.sub(r'\d +', '', result)
        result.strip()
        result = result.translate(str.maketrans('', '', string.punctuation))
        tokens = word_tokenize(result)
        result = ' '.join([i for i in tokens if not i in stop_words])

    return result


class TextPreprocessingAgent(BaseMetaAgent):
    processed: List[ObjectId]
    to_process: List[Metavertex]
    mg: MetagraphPersist

    def __init__(self, mg: MetagraphPersist) -> None:
        super().__init__(mg)
        self.processed = []
        self.to_process = []

    def check_condition(self) -> bool:
        self.to_process = list(filter(
            lambda v: v.attrs.level == TextLevel.sentence and v.id not in self.processed,
            self.mg.vertices.values()
        ))

        return len(self.to_process) > 0

    def _run_vertex(self, v: BaseMetavertex) -> None:
        text, level = v.attrs.text, v.attrs.level
        processed = preprocess(text, level)
        v.attrs.processed = processed

    def run(self) -> None:
        for v in self.to_process:
            self._run_vertex(v)
            self.processed.append(v.id)
        self.to_process = []

    def __str__(self) -> str:
        return 'TextPreprocessingAgent'
