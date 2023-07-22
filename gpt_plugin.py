import pynvim
from gpt_plugin_package.openai_api_request import OpenAIAPIRequest
from gpt_plugin_package.openai_api_response import OpenAIAPIResponse

@pynvim.plugin
class GptPlugin(object):
    def __init__(self, nvim):
        self.nvim = nvim
        self.tmux_pane = None

    @pynvim.command('Gpt', nargs='*', range='')
    def gpt_command(self, args, range):
        if self.tmux_pane is None:
            self.tmux_pane = self.prompt_tmux_pane()

        self.nvim.command('echo "Waiting for OpenAI API response..."')

        openai_api_response = self.openai_api_response(args)
        self.write_to_file(str(openai_api_response.body))
        code_block = openai_api_response.code_block()

        if code_block:
            self.nvim.current.buffer[:] = code_block.split('\n')
            self.nvim.command('w my_spec.rb')
            self.run_test_in_tmux()
        else:
            self.nvim.current.buffer[:] = ["No code found in response"]

    def openai_api_response(self, args):
        response = OpenAIAPIRequest(args).send()
        return OpenAIAPIResponse(response)

    def prompt_tmux_pane(self):
        return self.nvim.eval('input("Please enter tmux pane ID or name: ")')

    def run_test_in_tmux(self):
        filename = "my_spec.rb"
        self.nvim.command(f'!tmux send-keys -t {self.tmux_pane} "rspec {filename}" Enter')

    def write_to_file(self, message):
        with open('/Users/jasonswett/Documents/code/gpt_plugin/log/gpt_plugin.log', 'a') as f:
            f.write(f"{message}\n")
