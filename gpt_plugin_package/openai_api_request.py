import os
import openai

SYSTEM_CONTENT = """
You are connected to a Vim plugin that helps me write code.
Your response should be formatted as follows.
There should be NOTHING in your response except the filename and file content.

Example:
my_spec.rb
```ruby
RSpec.describe "stuff" do
end
"""

OPENAI_MODEL="gpt-3.5-turbo"

class OpenAIAPIRequest:
    def __init__(self, args):
        self.args = args

    def send(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')

        return openai.ChatCompletion.create(
          model=OPENAI_MODEL,
          messages=[
                {"role": "system", "content": SYSTEM_CONTENT.strip()},
                {"role": "user", "content": ' '.join(self.args)}
            ]
        )