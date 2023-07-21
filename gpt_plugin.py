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

        code = self.parse_response(response['choices'][0]['message']['content'])
        if code:
            self.nvim.current.buffer[:] = code.strip().split('\n')
        else:
            self.nvim.current.buffer[:] = ["No code found in response"]

    def parse_response(self, response):
        code = re.findall(r'```(?:\w+\n)?(.*?)```', response, re.DOTALL)
        return code[0].strip() if code else None
