import random
from groq import Groq, GroqError

class AI:
    def __init__(self, db, config):
        self.db = db
        self.config = config
        self.model_name = "llama-3.3-70b-versatile"
        
        self.dead_keys = []
        self.keys = []
        with open("keys.txt", 'r') as f:
            for line in f:
                key = line.strip()
                if key:
                    self.keys.append(key)

        self.is_generating = False
        self.history: dict[int, list] = {}

    def __get_client(self):
        if not self.keys:
            raise Exception("No API keys available")
        key = random.choice(self.keys)
        client = Groq(api_key=key)
        return client

    def ask(self, question):
        response = self.__get_client().chat.completions.create(
            model=self.model_name,
            messages=[{'role': 'user', 'content': str(question)}]
        )
        return response.choices[0].message.content

    def reply_with_replicated_speech(self, prompt, messages):
        if self.is_generating:
            return "Please wait a moment."

        self.is_generating = True
        

        system_instruction = (
            f"You must reply to the user using the exact style of the following messages. "
            f"Replicate the speech patterns, tone, vocabulary, and quirkiness of these examples:\n\n{messages}\n\n"
            f"RULES: 1 paragraph max. No formatting. No 'As an AI'. Just the response. SPEAK ONLY IN ENGLISH NO MATTER WHAT. If the question is not clear, ask for clarification instead of making assumptions."
        )

        while True:
            client = self.__get_client()
            try:
                response = client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": str(prompt)},
                    ],
                    temperature=0.75, # Slightly higher temperature helps with mimicry
                )
                return response.choices[0].message.content
            
            except GroqError as e:
                print(self.keys)
                self.dead_keys.append(client.api_key)
                self.keys.remove(client.api_key)

                if not self.keys:
                    self.keys = self.dead_keys
                    break

        self.is_generating = False
        return "I literally CANNOT think right now ughhh"

    def ask_with_history(self, user_id, question):
        if user_id not in self.history:
            self.history[user_id] = []

        self.history[user_id].append({'role': 'user', 'content': str(question)})
        
        if len(self.history[user_id]) > 10:
            self.history[user_id] = self.history[user_id][-10:]

        response = self.__get_client().chat.completions.create(
            model=self.model_name,
            messages=self.history[user_id]
        )
        
        answer = response.choices[0].message.content
        
        self.history[user_id].append({'role': 'assistant', 'content': answer})
        
        return answer