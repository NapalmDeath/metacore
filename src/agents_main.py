from core.agents.agent_runner import AgentRunner
from text.morph_agent import TextMorphologyAgent
from text.syntax_agent import TextSyntaxAgent
from text.text_fragment import TextFragmentationAgent
from core.entities.common import Attributes
from core.metacore import Metacore, MetacoreConfig
from core.entities import Metavertex
from text.text_preprocessing import TextPreprocessingAgent
from text.utils import TextLevel

if __name__ == '__main__':
    metacore = Metacore(MetacoreConfig(
        db_connect_url='mongodb://localhost:27017/',
        db_name="metacore"
    ))

    mg = metacore.initialize()

    metacore.drop()

    root_text = Metavertex(name="root",
                           attrs=Attributes(text='Autonomous cars shift insurance liability toward manufacturers.',
                                            level=TextLevel.paragraph))

    mg.register(root_text)

    agent_runner = AgentRunner(mg)
    agent_runner.add_agent(TextFragmentationAgent)
    agent_runner.add_agent(TextPreprocessingAgent)
    agent_runner.add_agent(TextMorphologyAgent)
    agent_runner.add_agent(TextSyntaxAgent)
    agent_runner.run_all()

    mg.save_all()
