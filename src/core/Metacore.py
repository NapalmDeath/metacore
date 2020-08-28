from typing import TypedDict
from pymongo import MongoClient

from core.Metagraph import Metagraph


class MetacoreConfig(TypedDict):
    db_connect_url: str
    db_name: str


class Metacore:
    db: MongoClient = None
    config: MetacoreConfig
    metagraph: Metagraph

    def __init__(self, config: MetacoreConfig):
        self.config = config
        pass

    def initialize(self) -> Metagraph:
        client = MongoClient(self.config["db_connect_url"])
        self.db = client[self.config["db_name"]]
        self.metagraph = Metagraph(self.db)

        return self.metagraph
