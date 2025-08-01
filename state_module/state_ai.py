from model_module.ArkModelNew import ArkModelLink, UserMessage, AIMessage, SystemMessage
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))





class StateUser(State):
    
    def __init__(self):
        self.transition: Dict[str, str] = metadata.get("transitions", {})

        self.is_terminal = False


    def check_transition_ready(self, context):
        return True


    def run(self,agent, context):
        agent_response = agent.call_llm(context=context)

        return AIMessage(content=agent_response)

