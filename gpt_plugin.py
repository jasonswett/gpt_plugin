import os
import subprocess
import pynvim

from gpt_plugin_package.openai_api_request import OpenAIAPIRequest
from gpt_plugin_package.openai_api_response import OpenAIAPIResponse
from gpt_plugin_package.test_failure_request_message import TestFailureRequestMessage
from gpt_plugin_package.api_logger import APILogger
from gpt_plugin_package.editor import Editor

@pynvim.plugin
class GptPlugin(object):
    def __init__(self, nvim):
        self.nvim = nvim
        self.directory = '.'
        self.editor = Editor(nvim, self.directory)
        self.tmux_pane = None
        self.most_recent_test_command = None
        self.logger = APILogger()

    @pynvim.command('Gpt', nargs='*', range='')
    def gpt_command(self, args, range):
        request = self.code_request(' '.join(args))
        response = self.response(request)
        self.insert_code_block(response.filename(), response.code_block())

    @pynvim.command('GptRunTest', nargs='*', range='')
    def gpt_run_test_command(self, args, range):
        if self.tmux_pane is None:
            self.tmux_pane = self.prompt_tmux_pane()

        system_content = f"""
            Give me a command to run the test {self.editor.current_filename()}.
            Your response should contain absolutely nothing but the command.
            Examples:

            rspec my_spec.rb
            pytest my_test.py
        """

        request = self.request(system_content, ' '.join(args))
        response = self.response(request)
        self.run_test_in_tmux(response.content().body)

    @pynvim.command('GptSendTestResult', nargs='*', range='')
    def gpt_send_test_result(self, args, range):
        failure_message = self.tmux_pane_content()

        test_failure_request_message = TestFailureRequestMessage(
            self.editor.current_filename(),
            self.current_buffer_content(),
            failure_message
        )

        user_content = f"""
            Give me the code to make the following failure go away.
            I don't want the test to necessarily pass, I ONLY want enough code
            to make the failure message go away.
            {str(test_failure_request_message)}
        """

        request = self.code_request(user_content)
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

    def code_request(self, user_content):
        system_content = """
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
        return OpenAIAPIRequest(
            system_content,
            self.user_content_with_context(user_content),
            self.logger
        )

    def request(self, system_content, user_content):
        return OpenAIAPIRequest(
            system_content,
            self.user_content_with_context(user_content),
            self.logger
        )

    def user_content_with_context(self, user_content):
        return user_content + "\nHere is some file content that might be relevant:\n\n" + self.all_file_contents()

    def all_file_contents(self):
        all_file_contents = []

        for buffer in self.nvim.buffers:
            try:
                relative_path = os.path.relpath(buffer.name, self.directory)
                file_content = "\n".join(buffer[:])
                all_file_contents.append("{}{}".format(relative_path, file_content))
            except Exception as e:
                self.logger.write(f"Error processing buffer {buffer.name} with directory {self.directory}: {str(e)}")

        return "\n".join(all_file_contents)

    def response(self, request):
        self.nvim.command('echo "Waiting for OpenAI API response..."')
        response = OpenAIAPIResponse(request.send())
        self.logger.write(str(response.body))
        return response

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
