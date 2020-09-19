from typing import TypedDict
from pymongo import MongoClient

from core.metagraph import MetagraphPersist


class MetacoreConfig(TypedDict):
    db_connect_url: str
    db_name: str


class Metacore:
    db: MongoClient = None
    config: MetacoreConfig
    metagraph: MetagraphPersist
    client: MongoClient

    def __init__(self, config: MetacoreConfig):
        self.config = config
        pass

    def initialize(self) -> MetagraphPersist:
        self.client = MongoClient(self.config["db_connect_url"])
        self.db = self.client[self.config["db_name"]]

        self.metagraph = MetagraphPersist(self.db)

        return self.metagraph

    def drop(self):
        self.client.drop_database(self.config["db_name"])
