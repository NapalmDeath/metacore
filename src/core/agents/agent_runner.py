from typing import List, Type

from core.agents.agent import BaseMetaAgent
from core.metagraph import MetagraphPersist
from text.utils import debug


class AgentRunner:
    mg: MetagraphPersist
    agents_to_run: List[BaseMetaAgent]
    agents: List[BaseMetaAgent]

    def __init__(self, mg: MetagraphPersist) -> None:
        super().__init__()
        self.mg = mg
        self.agents_to_run = []
        self.agents = []

    def add_agent(self, cls: Type[BaseMetaAgent]):
        agent = cls(self.mg)
        self.agents.append(agent)

    def check(self) -> bool:
        self.agents_to_run = []

        for agent in self.agents:
            if agent.check_condition():
                debug('agent', agent, 'passed condition')
                self.agents_to_run.append(agent)

        return len(self.agents_to_run) > 0

    def run(self):
        debug('running', self.agents_to_run)
        for agent in self.agents_to_run:
            agent.run()

    def run_single(self):
        self.check()
        self.run()

    def run_all(self):
        while self.check():
            self.run()
