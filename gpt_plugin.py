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

        # Extract code between ``` marks and remove potential language hint (e.g., ruby)
        code = re.findall(r'```(?:\w+\n)?(.*?)```', response.choices[0].message['content'], re.DOTALL)

        if code:
            # Clear the current buffer and replace with API response
            self.nvim.current.buffer[:] = code[0].strip().split('\n')
        else:
            self.nvim.current.buffer[:] = ["No code found in response"]
