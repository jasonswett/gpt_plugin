import os
import openai

SYSTEM_CONTENT = """
You are connected to a Vim plugin that helps me write code.
Your response should contain the filename, the test command to be used, and the file content.
The response should contain NOTHING else. No explanation. No preamble.

Good example:
my_spec.rb
rspec my_spec.rb
```ruby
RSpec.describe "stuff" do
end

Good example:
spec/calculator_spec.rb
rspec spec/calculator_spec.rb
```ruby
RSpec.describe Calculator do
end

Bad example:
my_spec.rb
The test command is: "rspec my_spec.rb"
```ruby
RSpec.describe "stuff" do
end
"""

OPENAI_MODEL="gpt-3.5-turbo"

class OpenAIAPIRequest:
    def __init__(self, user_content):
        self.user_content = user_content

    def send(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')

        return openai.ChatCompletion.create(
          model=OPENAI_MODEL,
          messages=self.messages()
        )

    def messages(self):
        return [
                {"role": "system", "content": SYSTEM_CONTENT.strip()},
                {"role": "user", "content": self.user_content}
            ]
