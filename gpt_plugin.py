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

    @pynvim.command('Gpt', nargs='*', range='')
    def gpt_command(self, args, range):
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
        else:
            self.nvim.current.buffer[:] = ["No code found in response"]

    def code_block(self, response):
        content = response['choices'][0]['message']['content']
        code = re.findall(r'```(?:\w+\n)?(.*?)```', content, re.DOTALL)
        return code[0].strip() if code else None
