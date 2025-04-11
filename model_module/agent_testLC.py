from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from langchain.schema.output_parser import StrOutputParser
from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from ArkModel import ArkModelLink
import yaml
# loads configuration for model
with open("../config_module/config.yaml", 'r') as file:
    configuration = yaml.safe_load(file)

model_url = configuration["model_url"]


chat_model = ArkModelLink()


def multiply_tool(expression: str) -> str:
    """Multiplies two numbers given in the format 'a*b'."""
    try:
        num1, num2 = map(int, expression.split('*'))
        return str(num1 * num2)
    except Exception:
        return "Invalid input. Please use the format 'number*number'."

def subtract_tool(expression: str) -> str:
    """Multiplies two numbers given in the format 'a*b'."""
    try:
        num1, num2 = map(int, expression.split('*'))
        return str(num1 * num2)
    except Exception:
        return "Invalid input. Please use the format 'number*number'."



# Bind the tools to the model
chat_model = chat_model.bind_tools(tools=[multiply_tool, subtract_tool])


chat_model = chat_model.bind_tools(tools=chat_model.kwargs['tools']+["another_tool"])

#note: need to c
print(chat_model)
exit()

prompt_template = ChatPromptTemplate.from_messages(

    [
        ("system", "you are a helpful AI assitant who gives funny answers to questions"),
        ("human", "{prompt}"), 
    ]
)
chain =  prompt_template | chat_model | StrOutputParser()
result = chain.invoke({"prompt": "Who is Trump"})
print("******* \n\n ****** \n\n")
print(result)
