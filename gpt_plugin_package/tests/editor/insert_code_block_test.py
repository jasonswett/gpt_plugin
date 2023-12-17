import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import os
import pytest
from pynvim import attach
from gpt_plugin_package.editor import Editor

@pytest.fixture(scope="function")
def nvim():
    nvim = attach('child', argv=["/usr/bin/env", "nvim", "-u", "NONE", "-N", "--embed", "--headless"])
    yield nvim
    for buffer in nvim.buffers:
        nvim.command(f'bd! {buffer.number}')

# Group 1: When the current buffer is the only buffer
class TestCurrentBufferIsOnlyBuffer:
    def setup_method(self):
        self.directory = '.'
        self.file_name = "martin.rb"
        self.file_path = os.path.join(self.directory, self.file_name)

    def teardown_method(self):
        for filename in ["martin.rb", "jason.rb", "calculator_spec.rb", "calculator.rb"]:
            file_path = os.path.join(self.directory, filename)
            if os.path.exists(file_path):
                os.remove(file_path)

    def test_1(self, nvim):
        # When the current buffer is empty
        editor = Editor(nvim, self.directory)

        # And we insert a code block for
        # a new file called martin.rb
        editor.write_code_block("martin.rb", "puts 'hello world'")

        # Then the result is that the current buffer is martin.rb
        assert editor.current_filename() == "martin.rb"

    def test_2(self, nvim):
        # When the current buffer is not empty
        editor = Editor(nvim, self.directory)
        nvim.current.buffer[:] = ["initial content"]

        # And we insert a code block for
        # a new file called martin.rb
        editor.write_code_block("martin.rb", "puts 'hello world'")

        # The content of the martin.rb buffer gets replaced
        # with the inserted code block
        nvim.command(f"edit martin.rb")
        assert "\n".join(nvim.current.buffer[:]) == "puts 'hello world'"

    def test_3(self, nvim):
        editor = Editor(nvim, self.directory)

        # When some content exists in some tab
        nvim.current.buffer[:] = ["i am jason"]
        nvim.command(f'w jason.rb')

        # And we insert a code block into a different tab
        editor.write_code_block("martin.rb", "puts 'hello world'")

        # The original tab is untouched
        nvim.command(f'buffer jason.rb')
        assert "\n".join(nvim.current.buffer[:]) == "i am jason"

        os.remove(os.path.join(self.directory, "jason.rb"))

    def test_4(self, nvim):
        editor = Editor(nvim, self.directory)

        # When some content exists in Tab A
        nvim.current.buffer[:] = ["this is some test code"]
        nvim.command(f'w calculator_spec.rb')

        # And we insert a code block into Tab B
        editor.write_code_block("calculator.rb", "puts 1 + 1 = 2")

        # And we navigate to Tab A
        nvim.command(f'buffer calculator_spec.rb')

        # And we insert another code block into Tab B
        editor.write_code_block("calculator.rb", "puts 2 + 2 = 4")

        # Tab A still contains the test code
        nvim.command('buffer calculator_spec.rb')
        assert nvim.current.buffer[:] == ["this is some test code"]

    def test_5(self, nvim):
        editor = Editor(nvim, self.directory)

        # When some content exists in Tab A
        nvim.current.buffer[:] = ["this is some test code"]
        nvim.command(f'w calculator_spec.rb')

        # And we insert a code block into Tab B
        editor.write_code_block("calculator.rb", "puts 1 + 1 = 2")

        # And we navigate to Tab A
        nvim.command(f'buffer calculator_spec.rb')

        # And we insert another code block into Tab B
        editor.write_code_block("calculator.rb", "puts 2 + 2 = 4")

        # Tab B contains the application code
        nvim.command('buffer calculator.rb')
        assert nvim.current.buffer[:] == ["puts 2 + 2 = 4"]

    def test_6(self, nvim):
        editor = Editor(nvim, self.directory)

        # When some content exists in Tab A
        nvim.current.buffer[:] = ["this is some test code"]
        nvim.command(f'w calculator_spec.rb')

        # And we insert a code block into Tab B
        editor.write_code_block("calculator.rb", "puts 1 + 1 = 2")

        # And we navigate to Tab A
        nvim.command(f'buffer calculator_spec.rb')

        # And we insert another code block into Tab B
        editor.write_code_block("calculator.rb", "puts 2 + 2 = 4")

        # Tab A does not contain the application code
        nvim.command('buffer calculator_spec.rb')
        assert nvim.current.buffer[:] != ["puts 2 + 2 = 4"]

    def test_7(self, nvim):
        editor = Editor(nvim, self.directory)

        # Given an empty code block
        empty_code_block = ""

        # When we try to insert this empty code block into a new file
        editor.write_code_block("empty_file.rb", empty_code_block)

        # Then the current buffer should contain the text "No code found in response"
        assert nvim.current.buffer[:] == ["No code found in response"], "Current buffer does not contain expected message for empty code block"
