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

def test_current_filename(nvim):
    directory = '.'
    editor = Editor(nvim, directory)
    file_path = os.path.join(directory, "test_file.rb")
    with open(file_path, "w") as f:
        f.write("print('Hello, World!')")
    nvim.command(f"edit {file_path}")
    assert editor.current_filename() == "test_file.rb"
    os.remove(file_path)

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

def test_all_file_contents_with_single_file(nvim):
    directory = '.'
    editor = Editor(nvim, directory)
    file_path = os.path.join(directory, "test_file_1.rb")
    with open(file_path, "w") as f:
        f.write("print('Hello, World!')")
    nvim.command(f"edit {file_path}")

    assert editor.all_file_contents() == f"test_file_1.rbprint('Hello, World!')"
    os.remove(file_path)

def test_all_file_contents_with_multiple_files(nvim):
    directory = '.'
    editor = Editor(nvim, directory)
    file_path_1 = os.path.join(directory, "test_file_1.rb")
    file_path_2 = os.path.join(directory, "test_file_2.rb")
    with open(file_path_1, "w") as f:
        f.write("print('Hello, World!')")
    nvim.command(f"edit {file_path_1}")
    with open(file_path_2, "w") as f:
        f.write("print('Goodbye, World!')")
    nvim.command(f"tabnew {file_path_2}")

    assert editor.all_file_contents() == f"test_file_1.rbprint('Hello, World!')\ntest_file_2.rbprint('Goodbye, World!')"
    os.remove(file_path_1)
    os.remove(file_path_2)
