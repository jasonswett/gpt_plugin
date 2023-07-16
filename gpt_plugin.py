import os
import openai
import pynvim
import re

@pynvim.plugin
class GptPlugin(object):
    def __init__(self, nvim):
        self.nvim = nvim

    @pynvim.command('Gpt', nargs='*', range='')
    def gpt_command(self, args, range):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        prompt = ' '.join(args)

        system_content = """
        You are connected to a Vim plugin that helps me write code.
        Your response should contain exactly ONE code block which I can copy and paste.
        """

        response = openai.ChatCompletion.create(
          model="gpt-3.5-turbo",
          messages=[
                {"role": "system", "content": system_content.strip()},
                {"role": "user", "content": prompt}
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
