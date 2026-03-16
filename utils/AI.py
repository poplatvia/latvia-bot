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

    # limit max_len messages
    def insert_message(self, user_id, content, max_len=10):
        if user_id not in self.history:
            self.history[user_id] = []
        
        self.history[user_id].append({'role': 'user', 'content': str(content)})
        
        if len(self.history[user_id]) > max_len:
            self.history[user_id] = self.history[user_id][-max_len:]

    def ask(self, question):
        response = self.__get_client().chat.completions.create(
            model=self.model_name,
            messages=[{'role': 'user', 'content': str(question)}]
        )
        return response.choices[0].message.content

    def reply_with_replicated_speech(self, prompt, messages, extra_instructions=""):
        if self.is_generating:
            return "Please wait a moment."

        self.is_generating = True
        

        system_instruction = (
            f"You must reply to the user using the exact style of the following messages. "
            f"Replicate the speech patterns, tone, vocabulary, and quirks of these examples:\n\n{messages}\n\n"
            f"RULES: 2 SENTENCES MAX. No formatting. No 'As an AI'. You aren't 'trained'. "
            f"Just the response. SPEAK ONLY IN ENGLISH NO MATTER WHAT. If the question is not clear, ask for clarification instead of making assumptions. "
            f" YOU ARE THE PERSON IN THE EXAMPLES, NOT AN AI. YOU HAVE THE SAME KNOWLEDGE AS THE EXAMPLES, NOTHING MORE. YOU MUST CREATE SOMETHING NEW. A NEW THOUGHT. DO NOT REPEAT ANYTHING EXACTLY. DO NOT PARAPHRASE, CREATE NEW SENTENCES THAT CONVEY THE SAME MEANING. "
        )

        while True:
            client = self.__get_client()

            try:
                response = client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "system", "content": extra_instructions},
                        {"role": "user", "content": str(prompt)},
                    ],
                    temperature=0.9, # Slightly higher temperature helps with mimicry
                )
                self.is_generating = False
                return response.choices[0].message.content
            
            except GroqError as e:
                self.dead_keys.append(client.api_key)
                self.keys.remove(client.api_key)

                if not self.keys:
                    self.keys = self.dead_keys
                    break

        self.is_generating = False
        return "Your question is stupid and as a consequence I refuse to answer it."

    def ask_with_history(self, user_id, question, context: list[str]):

        if self.is_generating:
            return "Please wait a moment."

        self.is_generating = True
        

        system_instruction = (
            f"You must reply to the user factually extrapolating from statements made by the server owner. "
            f"The messages by the server owner are the following:\n\n{context}\n\n"
            f"RULES: 2 SENTENCES MAX. No formatting. No 'As an AI'. You aren't 'trained'. "
            f"Do not mention 'AI' or 'as an AI' in your response. Just the response. If the question is not clear, ask for clarification instead of making assumptions."
            f" Speak only English and be very stern and factual."
        )

        if user_id not in self.history:
            self.history[user_id] = []

        self.history[user_id].append({'role': 'user', 'content': str(question)})

        while True:
            client = self.__get_client()

            try:
                response = client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_instruction},
                        *self.history[user_id],
                        {"role": "user", "content": str(question)},
                    ],
                    temperature=0.6, # Slightly lower temperature for factuality
                )
                self.is_generating = False
                answer = response.choices[0].message.content
                self.history[user_id].append({'role': 'assistant', 'content': answer})
                return answer
            
            except GroqError as e:
                self.dead_keys.append(client.api_key)
                self.keys.remove(client.api_key)

                if not self.keys:
                    self.keys = self.dead_keys
                    break

        self.is_generating = False
        return "Your question is stupid and as a consequence I refuse to answer it."