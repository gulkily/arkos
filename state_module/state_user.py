from model_module.ArkModelNew import ArkModelLink, UserMessage, AIMessage, SystemMessage
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class StateUser(State):
    
    def __init__(self):
        self.transition: Dict[str, str] = metadata.get("transitions", {})

        self.is_terminal = False


    def check_transition_ready(self, context):
        return True

    

    def run(self, context):

        user_input = input("You: ")
        if user_input.strip().lower() == "exit":
            print("safe_shutdown sequence initialized")
            self.is_terminal = False
            return 
        
        else:
            return UserMessage(content=user_input)
