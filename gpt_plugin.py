import os
import subprocess
import pynvim
from gpt_plugin_package.openai_api_request import OpenAIAPIRequest
from gpt_plugin_package.openai_api_response import OpenAIAPIResponse
from gpt_plugin_package.test_failure_request_message import TestFailureRequestMessage
from gpt_plugin_package.api_logger import APILogger

CODE_REQUEST_SYSTEM_CONTENT = """
You are connected to a Vim plugin that helps me write code.
Your response should contain the filename and the file content.
The response should contain NOTHING else. No explanation. No preamble.

Good example:
my_spec.rb
```ruby
RSpec.describe "stuff" do
end

Good example:
spec/calculator_spec.rb
```ruby
RSpec.describe Calculator do
end

Bad example:
Filename: my_spec.rb
```ruby
RSpec.describe "stuff" do
end
"""

@pynvim.plugin
class GptPlugin(object):
    def __init__(self, nvim):
        self.nvim = nvim
        self.directory = '.'
        self.tmux_pane = None
        self.most_recent_test_command = None
        self.logger = APILogger()

    @pynvim.command('Gpt', nargs='*', range='')
    def gpt_command(self, args, range):

        request = self.request(CODE_REQUEST_SYSTEM_CONTENT, ' '.join(args))
        response = self.response(request)
        self.insert_code_block(response.filename(), response.code_block())

    @pynvim.command('GptRunTest', nargs='*', range='')
    def gpt_run_test_command(self, args, range):
        if self.tmux_pane is None:
            self.tmux_pane = self.prompt_tmux_pane()

        user_content = f"""
            Give me a command to run the test {self.current_filename()}.
            Your response should contain absolutely nothing but the command.
            Example:

            rspec my_spec.rb
        """

        request = self.request('', user_content)
        response = self.response(request)
        self.run_test_in_tmux(response.content().body)

    @pynvim.command('GptSendTestResult', nargs='*', range='')
    def gpt_send_test_result(self, args, range):
        failure_message = self.tmux_pane_content()

        test_failure_request_message = TestFailureRequestMessage(
            self.current_filename(),
            self.current_buffer_content(),
            failure_message
        )

        user_content = f"""
            Give me the code to make the following failure go away.
            I don't want the test to necessarily pass, I ONLY want enough code
            to make the failure message go away.
            {str(test_failure_request_message)}
        """

        request = self.request(CODE_REQUEST_SYSTEM_CONTENT, user_content)
        response = self.response(request)
        self.insert_code_block(response.filename(), response.code_block())

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

    def request(self, system_content, user_content):
        request = OpenAIAPIRequest(
            system_content,
            user_content + "\n".join(self.all_file_contents())
        )

        self.logger.write(str(request.messages()))
        return request

    def all_file_contents(self):
        all_file_contents = []

        for buffer in self.nvim.buffers:
            try:
                relative_path = os.path.relpath(buffer.name, self.directory)
                file_content = "\n".join(buffer[:])
                all_file_contents.append(
                    "Here is some file content that may be relevant:\n\n{}{}".format(
                        relative_path, file_content
                    )
                )
            except Exception as e:
                self.logger.write(f"Error processing buffer {buffer.name} with directory {self.directory}: {str(e)}")

        return all_file_contents

    def response(self, request):
        self.nvim.command('echo "Waiting for OpenAI API response..."')
        response = OpenAIAPIResponse(request.send())
        self.logger.write(str(response.body))
        return response

    def current_filename(self):
        return os.path.relpath(self.nvim.current.buffer.name, self.directory)

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
