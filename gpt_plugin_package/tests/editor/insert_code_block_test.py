import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import os
import pytest
from pynvim import attach
from gpt_plugin_package.editor import Editor

@pytest.fixture(scope="function")
def nvim():
    nvim = attach('child', argv=["/usr/bin/env", "nvim", "-u", "NONE", "-N", "--embed", "--headless"])
    yield nvim  # pass control to the test function
    # Cleanup code to close all buffers
    for buffer in nvim.buffers:
        nvim.command(f'bd! {buffer.number}')  # bd! is a command to delete a buffer

def test_insert_code_block(nvim):
    directory = '.'
    editor = Editor(nvim, directory)
    file_path = os.path.join(directory, "test_code.rb")
    code_block = "def hello():\n    print('Hello, world!')"

    editor.insert_code_block("test_code.rb", code_block)

    with open(file_path, 'r') as f:
        # Expect an extra newline character at the end of the file
        assert f.read() == code_block + '\n'

    nvim.command(f"edit {file_path}")
    assert editor.current_filename() == "test_code.rb"

    # If the file needs to be removed after the test
    os.remove(file_path)
