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

        openai.api_key = os.getenv('OPENAI_API_KEY')

        response = openai.ChatCompletion.create(
          model=OPENAI_MODEL,
          messages=[
                {"role": "system", "content": SYSTEM_CONTENT.strip()},
                {"role": "user", "content": ' '.join(args)}
            ]
        )

        code_block = self.code_block(response)
        if code_block:
            self.nvim.current.buffer[:] = code_block.strip().split('\n')
            self.nvim.command('w my_spec.rb')
            self.run_rspec_in_tmux(code_block)
        else:
            self.nvim.current.buffer[:] = ["No code found in response"]

    def code_block(self, response):
        content = response['choices'][0]['message']['content']
        code = re.findall(r'```(?:\w+\n)?(.*?)```', content, re.DOTALL)
        return code[0].strip() if code else None

    def prompt_tmux_pane(self):
        return self.nvim.eval('input("Please enter tmux pane ID or name: ")')

    def run_rspec_in_tmux(self, code_block):
        filename = "my_spec.rb"
        self.nvim.command(f'!tmux send-keys -t {self.tmux_pane} "rspec {filename}" Enter')
