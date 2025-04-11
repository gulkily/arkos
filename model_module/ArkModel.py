from typing import Any, Dict, Iterator, List, Optional

from langchain_core.callbacks import (

    CallbackManagerForLLMRun,
)
from langchain_core.language_models import BaseChatModel

from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
)
from langchain_core.messages.ai import UsageMetadata
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from pydantic import Field

from huggingface_hub import InferenceClient


class ArkModelLink(BaseChatModel):
    """A custom chat model which interfaces with Hugginface TGI"""


    # model_name: str = Field(alias='model')
    
    def _generate(

        self, 
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None, 
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any
    ) -> ChatResult: 

        """
        Override _generate method to implement custom chat_model logic
        """ 

        last_message = messages
        response = self.make_llm_call(messages)

        message = AIMessage(
    content= f'{response}',  # Ensure this is a valid string
    content_list=["some string", {"key": "value"}],  # Ensure this is a valid list of strings or dicts
    usage_metadata={
        "input_tokens": 123,  # Example value
        "output_tokens": 456,  # Example value
        "total_tokens": 579  # Example value
    }
)
        
        generation = ChatGeneration(message=message)
        ans = ChatResult(generations=[generation], llm_output = None)
        return ans
    
    def make_llm_call(self, messages): 

        sys_msg = messages[0].content
        user_msg = messages[-1].content
        
        client = InferenceClient(
            base_url="http://localhost:8080/v1/",
        )

        output = client.chat.completions.create(
            model="tgi",
            messages=[
                {"role": "system", "content": f'{sys_msg}'},

                {"role": "user", "content": f'{user_msg}'},
            ],
            stream=False,
            max_tokens=1024,
        )


        response = output.choices[0].message.content
        return response
    
    def bind_tools(self,tools):
        '''

        input: tools [array of tools]

        '''
        if not self.kwargs: 
            self.bind_tools(tools=tools)
        else:
            self.bind_tools(tools=chat_model.kwargs['tools']+tools)


        

    @property
    def _llm_type(self) -> str:
        """Get the type of language model used by this chat model."""
        return "hugging-face-tgi-server"
        
