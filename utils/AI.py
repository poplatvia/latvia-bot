import re
from groq import Groq

class AI:
    def __init__(self, db, config):
        self.db = db
        self.config = config
        self.model_name = "llama-3.3-70b-versatile"
        
        keys = []
        with open("keys.txt", 'r') as f:
            for line in f:
                key = line.strip()
                if key:
                    keys.append(key)

        self.client = Groq(api_key=keys[0])  # Use the first key for now

        self.is_generating = False
        self.history: dict[int, list] = {}

    def ask(self, question):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{'role': 'user', 'content': str(question)}]
        )
        return response.choices[0].message.content

    def reply_with_replicated_speech(self, prompt, messages):
        if self.is_generating:
            return "Please wait a moment."

        self.is_generating = True
        
        try:
            system_instruction = (
                f"You must reply to the user using the exact style of the following messages. "
                f"Replicate the speech patterns, tone, vocabulary, and quirkiness of these examples:\n\n{messages}\n\n"
                f"RULES: 1 paragraph max. No formatting. No 'As an AI'. Just the response. SPEAK ONLY IN ENGLISH NO MATTER WHAT. If the question is not clear, ask for clarification instead of making assumptions."
            )

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": str(prompt)},
                ],
                temperature=0.6, # Slightly higher temperature helps with mimicry
            )
            return response.choices[0].message.content
        finally:
            # reset the generation flag even if it errors out
            self.is_generating = False

    def ask_with_history(self, user_id, question):
        if user_id not in self.history:
            self.history[user_id] = []

        self.history[user_id].append({'role': 'user', 'content': str(question)})
        
        if len(self.history[user_id]) > 10:
            self.history[user_id] = self.history[user_id][-10:]

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=self.history[user_id]
        )
        
        answer = response.choices[0].message.content
        
        self.history[user_id].append({'role': 'assistant', 'content': answer})
        
        return answer