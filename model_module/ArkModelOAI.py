from typing import Any, Dict, List, Optional, Union, AsyncIterator

from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_function
from huggingface_hub import InferenceClient
from openai import OpenAI
import pprint 
pp = pprint.PrettyPrinter()




class ArkModelLink(BaseChatModel, BaseModel):
    """A custom chat model which interfaces with Hugging Face TGI and supports tool calling."""

    model_name: str = Field(default="tgi")
    base_url: str = Field(default="http://localhost:8080/v1")
    max_tokens: int = Field(default=1024)
    temperature: float = Field(default=0.7)
    tools: Optional[List[BaseTool]] = Field(default_factory=list)


    def _convert_tools(self) -> Optional[List[Dict[str, Any]]]:
        if not self.tools:
            return None

        def convert_tool(tool: BaseTool) -> Dict[str, Any]:
            tool_as_dict = convert_to_openai_function(tool)
            return {
                "type": "function",
                "function": tool_as_dict
            }
            
        converted = [convert_tool(tool) for tool in self.tools]
        return converted
    def _get_tool_by_name(self, name: str) -> Optional[BaseTool]:
        return next((tool for tool in self.tools if tool.name == name), None)

    def make_llm_call(self, messages: List[BaseMessage], tools: Optional[List[Dict[str, Any]]] = None) -> Union[str, Dict[str, Any]]:
        client = OpenAI(
            base_url="http://localhost:8080/v1",
            api_key="_",
        )
        
        chat_completion = client.chat.completions.create(
            model="tgi",
            messages=[
                {
                    "role": "system",
                    "content": messages[0].content,
                },
                {
                    "role": "user",
                    "content": messages[-1].content,
                },
            ],
            tools=tools,
            tool_choice="auto",  # tool selected by model
            max_tokens=self.max_tokens,
        )
        message = chat_completion.choices[0].message
        if hasattr(message, "tool_calls") and message.tool_calls:
            # Return full message object if there are tool calls
            return {"tool_calls": message.tool_calls}
        else:
            return {"tool_calls": None, "message": message.content}
        
    
    def _generate(
    self,
    messages: List[BaseMessage],
    stop: Optional[List[str]] = None,
    run_manager: Optional[CallbackManagerForLLMRun] = None,
    **kwargs: Any
) -> ChatResult:
        tool_schemas = self._convert_tools()

        # Step 1: Make initial LLM call
        response = self.make_llm_call(messages, tools=tool_schemas)
        if response["tool_calls"]: 

            print("***** IM USING TOOLS ******")
            tool_messages = [] 
            
            for tool_call in response["tool_calls"]:
                tool_name = tool_call.function.name
                arguments = tool_call.function.arguments

                tool = self._get_tool_by_name(tool_name)
                if not tool:
                    raise ValueError(f"Tool '{tool_name}' was requested but not found")

                tool_args = arguments

                

                tool_output = tool.invoke(tool_args)
                tool_message = {
                    "type" : "message",
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(tool_output),
                }
                tool_messages.append(tool_message)

                # Step 2: Make SECOND LLM call, feeding back tool results

                hinter = "the answer to the tool you called is: "
                second_response = self.make_llm_call(
                    messages + [BaseMessage(type="unknown", content=hinter + tool_messages[0]['content'])],  # feed back the tool result
                    tools=tool_schemas,
                )

                
                content = str(second_response)

        else:
            print("*****NO TOOL CALL USED****")
            # No tool used, just regular model output
            content = str(response)

        message = AIMessage(
            content=content,
            usage_metadata={
                "input_tokens": 123,
                "output_tokens": 456,
                "total_tokens": 579
            }
        )


        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation], llm_output=None)

    def bind_tools(self, tools: List[BaseTool]) -> "ArkModelLink":

        
        return self.copy(update={"tools": self.tools + tools})

    @property
    def _llm_type(self) -> str:
        return "hugging-face-tgi-server"

    async def _astream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any
    ) -> AsyncIterator[ChatGenerationChunk]:
        from sseclient import SSEClient
        import json

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": messages[0].content},
                {"role": "user", "content": messages[-1].content},
            ],
            "stream": True,
            "max_tokens": self.max_tokens,
        }

        tool_schemas = self._convert_tools()
        if tool_schemas:
            payload["tools"] = tool_schemas

        import requests
        headers = {"Accept": "text/event-stream", "Content-Type": "application/json"}
        response = requests.post(
            url=self.base_url + "chat/completions",
            headers=headers,
            json=payload,
            stream=True,
        )

        client = SSEClient(response)
        for event in client.events():
            if event.data.strip() == "[DONE]":
                break
            try:
                chunk_data = json.loads(event.data)
                delta = chunk_data["choices"][0].get("delta", {})
                if delta.get("content"):
                    yield ChatGenerationChunk(
                        message=AIMessage(content=delta["content"])
                    )
            except Exception:
                continue

if __name__ == "__main__":
    chat_model = ArkModelLink()




