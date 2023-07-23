import os
import pynvim
from gpt_plugin_package.openai_api_request import OpenAIAPIRequest
from gpt_plugin_package.openai_api_response import OpenAIAPIResponse

LOG_FILENAME = '/Users/jasonswett/Documents/code/gpt_plugin/log/gpt_plugin.log'

@pynvim.plugin
class GptPlugin(object):
    def __init__(self, nvim):
        self.nvim = nvim
        self.directory = None
        self.tmux_pane = None

    @pynvim.command('Gpt', nargs='*', range='')
    def gpt_command(self, args, range):
        if self.directory is None:
            self.directory = self.prompt_directory()

        if self.tmux_pane is None:
            self.tmux_pane = self.prompt_tmux_pane()

        self.nvim.command('echo "Waiting for OpenAI API response..."')

        request = OpenAIAPIRequest(args)
        response = self.openai_api_response(request)
        self.write_to_log(str(response.body))
        code_block = response.code_block()
        filename = os.path.join(self.directory, response.filename())

        if code_block:
            self.insert_content_into_buffer(filename, code_block.split('\n'))
            self.save_file(filename)
            self.run_test_in_tmux(filename)
        else:
            self.nvim.current.buffer[:] = ["No code found in response"]

    def insert_content_into_buffer(self, filename, content):
        self.nvim.command(f'silent! bwipeout! {filename}')
        self.nvim.command('enew')
        self.nvim.current.buffer[:] = content

    def save_file(self, filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        self.nvim.command(f'w! {filename}')

    def openai_api_response(self, request):
        response = request.send()
        return OpenAIAPIResponse(response)

    def prompt_directory(self):
        return self.nvim.eval('input("Project root directory: ")')

    def prompt_tmux_pane(self):
        return self.nvim.eval('input("tmux pane ID: ")')

    def run_test_in_tmux(self, filename):
        self.nvim.command(f'!tmux send-keys -t {self.tmux_pane} "rspec {filename}" Enter')

    def write_to_log(self, message):
        with open(LOG_FILENAME, 'a') as f:
            f.write(f"{message}\n")
