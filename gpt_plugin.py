import os
import subprocess
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
        self.write_to_log(str(request.messages()))

        response = OpenAIAPIResponse(request.send())
        self.write_to_log(str(response.body))

        self.insert_code_block(response.filename(), response.code_block())

    @pynvim.command('GptSendTestResult', nargs='*', range='')
    def gpt_send_test_result(self, args, range):
        filename = self.nvim.current.buffer.name
        buffer_content = "\n".join(self.nvim.current.buffer[:])
        tmux_capture_command = f'tmux capture-pane -t {self.tmux_pane} -p'
        failure_message = subprocess.check_output(tmux_capture_command, shell=True, text=True)

        message = f"""This is my test:
{filename}
{buffer_content}

Here is the failure message:
{failure_message}

Write me the code that will make this failure message go away."""

        request = OpenAIAPIRequest(message)
        self.write_to_log(str(request.messages()))

        response = OpenAIAPIResponse(request.send())
        self.write_to_log(str(response.body))

    def insert_code_block(self, filename, code_block):
        if code_block:
            path = os.path.join(self.directory, filename)
            self.insert_content_into_buffer(path, code_block.split('\n'))
            self.save_file(path)
            self.run_test_in_tmux(path)
        else:
            self.nvim.current.buffer[:] = ["No code found in response"]

    def insert_content_into_buffer(self, filename, content):
        self.nvim.command(f'silent! bwipeout! {filename}')
        self.nvim.command('enew')
        self.nvim.current.buffer[:] = content

    def save_file(self, filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        self.nvim.command(f'w! {filename}')

    def prompt_directory(self):
        return self.nvim.eval('input("Project root directory: ")')

    def prompt_tmux_pane(self):
        return self.nvim.eval('input("tmux pane ID: ")')

    def run_test_in_tmux(self, filename):
        self.nvim.command(f'!tmux send-keys -t {self.tmux_pane} "rspec {filename}" Enter')

    def write_to_log(self, message):
        with open(LOG_FILENAME, 'a') as f:
            f.write(f"{message}\n")
