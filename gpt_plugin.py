import os
import openai
import pynvim
import re

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

@pynvim.plugin
class GptPlugin(object):
    def __init__(self, nvim):
        self.nvim = nvim
        self.tmux_pane = None

    @pynvim.command('Gpt', nargs='*', range='')
    def gpt_command(self, args, range):
        if self.tmux_pane is None:
            self.tmux_pane = self.prompt_tmux_pane()

        self.nvim.command('echo "Waiting for OpenAI API response..."')

        response = self.openai_api_response(args)
        self.write_to_file(str(response))
        code_block = self.code_block(response)

        if code_block:
            self.nvim.current.buffer[:] = code_block.split('\n')
            self.nvim.command('w my_spec.rb')
            self.run_test_in_tmux()
        else:
            self.nvim.current.buffer[:] = ["No code found in response"]

    def openai_api_response(self, args):
        openai.api_key = os.getenv('OPENAI_API_KEY')

        response = openai.ChatCompletion.create(
          model=OPENAI_MODEL,
          messages=[
                {"role": "system", "content": SYSTEM_CONTENT.strip()},
                {"role": "user", "content": ' '.join(args)}
            ]
        )
        return response

    def code_block(self, response):
        content = response['choices'][0]['message']['content']
        filename_content = content.split('\n', 1)

        if len(filename_content) < 2:
            return None

        code_content = filename_content[1].strip()

        # Remove code fences
        code_content = re.sub(r'```.*$', '', code_content, flags=re.MULTILINE)  # remove the opening code fence
        code_content = code_content.rstrip("`")  # remove the closing code fence
        return code_content.strip()  # return the content part after stripping the leading and trailing whitespaces

    def prompt_tmux_pane(self):
        return self.nvim.eval('input("Please enter tmux pane ID or name: ")')

    def run_test_in_tmux(self):
        filename = "my_spec.rb"
        self.nvim.command(f'!tmux send-keys -t {self.tmux_pane} "rspec {filename}" Enter')

    def write_to_file(self, message):
        with open('/Users/jasonswett/Documents/code/gpt_plugin/log/gpt_plugin.log', 'a') as f:
            f.write(f"{message}\n")
