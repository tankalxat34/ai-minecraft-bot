"""
OpenAI functionality to play in Minecraft
"""

import os
from openai import OpenAI

from helper import loadDotEnv
loadDotEnv()


client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)


class Session:
    def __init__(self, model: str = "gpt-3.5-turbo", systemPrompt: str = "You are expert and you are inside the minecraft game"):
        self.messages = [
            # {"role": "system", "content": "You are expert and you are inside the minecraft game. You can interact with the world of minecraft through the Python language using the `mineflayer` library as well as the 'mineflayer-pathfinder` plugin.  When you receive a task to perform an action in a chat, you must issue Python code using this library that performs the specified action."},
            {"role": "system", "content": systemPrompt},
        ]
        
        self.completion = None
    
    def _createMessage(self, text: str, role: str = "user") -> dict:
        return {
            "role": role,
            "text": text
        }
    
    def ask(self, messageText: str, typeUser: str = "user"):
        """
        Use `$.choices[0].message`
        """
        self.messages.append(self._createMessage(messageText, typeUser))
        
        self.completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.messages
        )
        
        # completion.choices[0].message
        return self.completion

