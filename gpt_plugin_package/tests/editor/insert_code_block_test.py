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
        self.code_block = "print('hi')"

    def teardown_method(self):
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

    def test_current_buffer_is_empty(self, nvim):
        editor = Editor(nvim, self.directory)
        editor.insert_code_block(self.file_name, self.code_block)
        nvim.command(f"edit {self.file_path}")
        assert editor.current_filename() == self.file_name

    def test_current_buffer_is_not_empty_expected_contents(self, nvim):
        editor = Editor(nvim, self.directory)
        nvim.current.buffer[:] = ["initial content"]
        editor.insert_code_block(self.file_name, self.code_block)
        nvim.command(f"tabnext | edit {self.file_path}")
        assert editor.current_filename() == self.file_name
        assert "\n".join(nvim.current.buffer[:]) == self.code_block

    def test_current_buffer_is_not_empty_original_content_undisturbed(self, nvim):
        editor = Editor(nvim, self.directory)
        jason_file_name = "jason.rb"
        jason_content = "i am jason"
        nvim.current.buffer[:] = [jason_content]
        nvim.command(f'w {jason_file_name}')
        editor.insert_code_block(self.file_name, self.code_block)
        nvim.command(f'buffer {jason_file_name}')
        assert "\n".join(nvim.current.buffer[:]) == jason_content
        os.remove(os.path.join(self.directory, jason_file_name))
