import os
import openai

OPENAI_MODEL="gpt-3.5-turbo-16k"

class OpenAIAPIRequest:
    def __init__(self, system_content, user_content):
        self.system_content = system_content
        self.user_content = user_content

    def send(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')

        return openai.ChatCompletion.create(
          model=OPENAI_MODEL,
          messages=self.messages()
        )

    def messages(self):
        return [
                {"role": "system", "content": self.system_content.strip()},
                {"role": "user", "content": self.user_content}
            ]
