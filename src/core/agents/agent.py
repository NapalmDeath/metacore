from core.metagraph import Metagraph


class BaseMetaAgent:
    mg: Metagraph

    def __init__(self, mg: Metagraph) -> None:
        super().__init__()
        self.mg = mg

    def check_condition(self) -> bool:
        return False

    def run(self) -> None:
        pass
