import os
import openai
import pynvim
import re

SYSTEM_CONTENT = """
You are connected to a Vim plugin that helps me write code.
Your response should contain exactly ONE code block which I can copy and paste.
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

        self.nvim.command('echo "Waiting for API response..."')

        response = self.openai_api_response(args)
        code_block = self.code_block(response)

        if code_block:
            self.nvim.current.buffer[:] = code_block
            self.nvim.command('w my_spec.rb')
            self.run_test_in_tmux()
        else:
            self.nvim.current.buffer[:] = ["No code found in response"]

    def openai_api_response(self, args):
        openai.api_key = os.getenv('OPENAI_API_KEY')

        return openai.ChatCompletion.create(
          model=OPENAI_MODEL,
          messages=[
                {"role": "system", "content": SYSTEM_CONTENT.strip()},
                {"role": "user", "content": ' '.join(args)}
            ]
        )

    def code_block(self, response):
        content = response['choices'][0]['message']['content']
        code = re.findall(r'```(?:\w+\n)?(.*?)```', content, re.DOTALL)
        return code[0].strip().split('\n') if code else None

    def prompt_tmux_pane(self):
        return self.nvim.eval('input("Please enter tmux pane ID or name: ")')

    def run_test_in_tmux(self):
        filename = "my_spec.rb"
        self.nvim.command(f'!tmux send-keys -t {self.tmux_pane} "rspec {filename}" Enter')
