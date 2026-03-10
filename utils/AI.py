import ollama
import random

class AI:
    def __init__(self, db, config):
        self.db = db
        self.config = config
        self.model_name = "qwen3.5:0.8b"

        self.history: dict[int, list] = {}

    def ask(self, question):
        response = ollama.chat(self.model_name, 
            messages=[
                {'role': 'user', 'content': str(question)},
            ]
        )
        print(response)
        return response['message']['content']
    
    # Input list of messages, output response in the style of those messages. This is for replicating speech patterns of users.
    def reply_with_replicated_speech(self, prompt, messages):
        # random 1000 messages
        messages = random.sample(messages, min(1000, len(messages)))

        system_instruction1 = {
            "role": "system", 
            "content": f"You must reply to this user with the style of the following messages. In your reply, replicate the speech patterns, tone, and vocabulary of these messages:\n\n{messages}"
        }

        system_instruction2 = {
            "role": "system", 
            "content": f"Replies should be no more than 1 paragraph with no formatting. Just a solid block of text. Do not say 'As an AI language model' or anything like that. Just reply in the style of the above messages."
        }

        response = ollama.chat(self.model_name, 
            messages=[
                system_instruction1,
                system_instruction2,
                {'role': 'user', 'content': str(prompt)},
            ]
        )
        return response['message']['content']
    
    # Normal chatgpt-like conversation with history. This is for having ongoing conversations with users where the bot remembers what was said before.
    def ask_with_history(self, user_id, question):
        self.history.get(user_id, []).append({'role': 'user', 'content': str(question)})
        
        response = ollama.chat(
            model=self.model_name, 
            messages=self.history.get(user_id, [])
        )
        
        answer = response['message']['content']
        
        self.history.get(user_id, []).append({'role': 'assistant', 'content': answer})
        
        return answer