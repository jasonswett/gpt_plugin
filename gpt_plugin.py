import os
import subprocess
import pynvim
from gpt_plugin_package.openai_api_request import OpenAIAPIRequest
from gpt_plugin_package.openai_api_response import OpenAIAPIResponse
from gpt_plugin_package.test_failure_request_message import TestFailureRequestMessage

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
        failure_message = self.tmux_pane_content()

        test_failure_request_message = TestFailureRequestMessage(
            self.current_filename(),
            self.current_buffer_content(),
            failure_message
        )

        request = self.request(str(test_failure_request_message))
        response = self.response(request)
        self.insert_code_block(response.filename(), response.code_block())
        self.run_test_in_tmux(response.test_command())

    def insert_code_block(self, filename, code_block):
        if code_block:
            if not self.is_buffer_with_filename_open(filename) and not self.is_current_buffer_empty():
                self.nvim.command('tabnew')

            self.nvim.current.buffer[:] = code_block.split('\n')
            path = os.path.join(self.directory, filename)
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

    def current_filename(self):
        return self.nvim.current.buffer.name

    def current_buffer_content(self):
        return "\n".join(self.nvim.current.buffer[:])

    def tmux_pane_content(self):
        command = f'tmux capture-pane -t {self.tmux_pane} -p'
        return subprocess.check_output(command, shell=True, text=True)

    def is_current_buffer_empty(self):
        current_buffer_name = self.nvim.eval('bufname("%")')
        return current_buffer_name == ""

    def is_buffer_with_filename_open(self, filename):
        all_open_buffers = self.nvim.buffers
        return any([buffer.name.endswith(filename) for buffer in all_open_buffers])
