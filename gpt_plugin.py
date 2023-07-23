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

        request = self.request(' '.join(args))
        response = self.response(request)
        self.insert_code_block(response.filename(), response.code_block())
        self.run_test_in_tmux(response.test_command())

    @pynvim.command('GptSendTestResult', nargs='*', range='')
    def gpt_send_test_result(self, args, range):
        filename = self.nvim.current.buffer.name
        buffer_content = "\n".join(self.nvim.current.buffer[:])
        tmux_capture_command = f'tmux capture-pane -t {self.tmux_pane} -p'
        failure_message = subprocess.check_output(tmux_capture_command, shell=True, text=True)

        message = f"""
This is my test:
{filename}
{buffer_content}

Here is the failure message:
{failure_message}

Write me the code that will make this failure message go away."""

        request = self.request(message)
        response = self.response(request)
        self.insert_code_block(response.filename(), response.code_block())
        self.run_test_in_tmux(response.test_command())

    def insert_code_block(self, filename, code_block):
        if code_block:
            path = os.path.join(self.directory, filename)

            # Check if current buffer is truly empty using Vimscript function bufname('%')
            current_buffer_name = self.nvim.eval('bufname("%")')
            is_current_buffer_empty = (current_buffer_name == "")

            # Get all open buffers
            buffers = self.nvim.buffers

            # Check if buffer with filename already exists
            is_buffer_open = any([buf.name.endswith(filename) for buf in buffers])

            if not is_buffer_open and not is_current_buffer_empty:
                # Create a new tab if the current buffer is not empty
                self.nvim.command('tabnew')

            # Insert the code block
            self.nvim.current.buffer[:] = code_block.split('\n')
            self.save_file(path)
        else:
            self.nvim.current.buffer[:] = ["No code found in response"]

    def save_file(self, filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        self.nvim.command(f'w! {filename}')

    def prompt_directory(self):
        return self.nvim.eval('input("Project root directory: ")')

    def prompt_tmux_pane(self):
        return self.nvim.eval('input("tmux pane ID: ")')

    def run_test_in_tmux(self, test_command):
        self.nvim.command(f'!tmux send-keys -t {self.tmux_pane} "{test_command}" Enter')

    def write_to_log(self, message):
        with open(LOG_FILENAME, 'a') as f:
            f.write(f"{message}\n")

    def request(self, user_content):
        request = OpenAIAPIRequest(user_content)
        self.write_to_log(str(request.messages()))
        return request

    def response(self, request):
        self.nvim.command('echo "Waiting for OpenAI API response..."')
        response = OpenAIAPIResponse(request.send())
        self.write_to_log(str(response.body))
        return response
