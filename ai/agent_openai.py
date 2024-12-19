"""
openai api interface
"""
from agent_base import AIBase
from openai import OpenAI
import re
import os

class OpenAIAgent(AIBase):
    def __init__(self, angle):
        super().__init__(angle)
        self._api_key = None
        self._client = None
        self._context = []

    # Initialize API connection
    _api_key = os.getenv("OPENAI_API_KEY")
    if not _api_key:
        raise ValueError("API key not found. Make sure OPENAI_API_KEY is set as an environment variable.")
    def connect_agent(self):
        self._client = OpenAI(api_key=self._api_key)

    def initialize_agent(self):
        try:
            # Initialize the ai and update context history
            print("Initializing communication with OpenAI...")
            user_message = {
                    "role": "user",
                    "content": self.initial_prompt,
                }
            self._context.append(user_message)
            chat_completion = self._client.chat.completions.create(
                messages=self._context, model="gpt-4o",)
            
            # Udpate ai state and context history
            resp = chat_completion.choices[0].message.content
            print("OpenAI response:")
            print(resp)
            self.comprehension = resp.lower()
            ai_resp = {
                    "role": "assistant",
                    "content": resp,

            }
            self._context.append(ai_resp)
        except Exception as e:
            print(f"Failed to communicate with OpenAI: {e}")

    def update_angle(self):
        try:
            # Request ai to update the target angle and update context history
            print("Sending updated proximity to OpenAI...")
            user_message = {
                    "role": "user",
                    "content": str(self.distance),
                }
            self._context.append(user_message)
            chat_completion = self._client.chat.completions.create(
                messages=self._context, model="gpt-4o",)

            # Udpate ai state and context history
            self.query_state = True
            resp = chat_completion.choices[0].message.content
            print("OpenAI response:")
            print(resp)
            ai_resp = {
                    "role": "assistant",
                    "content": resp,
            }
            self._context.append(ai_resp)

            # Parse out angle
            if re.search(r'\bfinished\b', resp.lower()):
                self.complete_state = True
                match = re.search(r'\bfinished\b.*?(-?\d+\.?\d*)', resp.lower())
                if match:
                    extracted_value = float(match.group(1))
                    self.angle = float(extracted_value)
            else:
                self.angle = float(resp)
            
            print("\n")
            
        except Exception as e:
            print(f"Failed to get proper response from OpenAI: {e}")

    def get_agent_logic(self):
        try:
            # Interrogate ai agent for logic and update context history
            print("Querying OpenAI logic...")
            user_message = {
                    "role": "user",
                    "content": "In 200 words or less, tell me your logic used to achieve the stated goal",
                }
            self._context.append(user_message)
            chat_completion = self._client.chat.completions.create(
                messages=self._context, model="gpt-4o",)
            
            # Udpate ai state and context history
            resp = chat_completion.choices[0].message.content
            print("OpenAI response:")
            print(resp)
            ai_resp = {
                    "role": "assistant",
                    "content": resp,
            }
            self._context.append(ai_resp)
        except Exception as e:
            print(f"Failed to communicate with OpenAI: {e}")