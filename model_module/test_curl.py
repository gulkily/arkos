import requests
import json

url = "http://localhost:8080/v1/chat/completions"
headers = {
    "Content-Type": "application/json"
}
payload = {
    "model": "tgi",
    "messages": [
        {
            "role": "user",
            "content": "What is the weather like in New York?"
        }
    ],
    "tools": [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "The temperature unit to use. Infer this from the users location."
                        }
                    },
                    "required": ["location", "format"]
                }
            }
        }
    ],
    "tool_choice": "get_current_weather"
}

response = requests.post(url, headers=headers, json=payload)
print(response.status_code)
print(json.dumps(response.json(), indent=2))

