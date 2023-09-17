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

# Scenarios:
#
# GPT gives us a filename and some code associated with that filename
#
# The current buffer is the only buffer
#   The current buffer is empty
#   The current buffer is not empty
#
# The current buffer is not the only buffer
#   The target filename matches the current buffer
#   The target filename does not match the current buffer

def test_current_buffer_is_only_buffer_and_current_buffer_is_empty(nvim):
    directory = '.'
    editor = Editor(nvim, directory)
    file_path = os.path.join(directory, "martin.rb")
    code_block = "print('hi')"

    editor.insert_code_block("martin.rb", code_block)

    nvim.command(f"edit {file_path}")
    assert editor.current_filename() == "martin.rb"

    os.remove(file_path)

# When current buffer is the only buffer and the current buffer is not empty,
# assert that a new tab matching the filename contains the expected contents
def test_current_buffer_is_only_buffer_and_current_buffer_is_not_empty_expected_contents(nvim):
    # Setup
    directory = '.'
    editor = Editor(nvim, directory)

    # Create a non-empty buffer
    non_empty_content = "initial content"
    nvim.current.buffer[:] = [non_empty_content]

    file_name = "martin.rb"
    file_path = os.path.join(directory, file_name)
    code_block = "print('hi')"

    # Action
    editor.insert_code_block(file_name, code_block)

    # Verification
    # Ensure the tab with the specified filename has the inserted code block
    nvim.command(f"tabnext | edit {file_path}")  # Switch to the tab and open the file
    assert editor.current_filename() == file_name
    assert "\n".join(nvim.current.buffer[:]) == code_block

    # Cleanup
    os.remove(file_path)

# When current buffer is the only buffer and the current buffer is not empty,
# assert that the current buffer's contents are undisturbed
def test_current_buffer_is_only_buffer_and_current_buffer_is_not_empty_original_content_undisturbed(nvim):
    # Setup
    directory = '.'
    editor = Editor(nvim, directory)

    # Create and save a buffer with filename "jason.rb" and content "i am jason"
    jason_file_name = "jason.rb"
    jason_content = "i am jason"
    nvim.current.buffer[:] = [jason_content]
    nvim.command(f'w {jason_file_name}')

    # Action: Insert a new code block into "martin.rb"
    file_name = "martin.rb"
    code_block = "print('hi')"
    editor.insert_code_block(file_name, code_block)

    # Verification
    # Switch back to the original buffer by filename and verify its content
    nvim.command(f'buffer {jason_file_name}')
    assert "\n".join(nvim.current.buffer[:]) == jason_content

    # Cleanup: Removing the created "jason.rb" file
    os.remove(os.path.join(directory, "jason.rb"))
    os.remove(os.path.join(directory, "martin.rb"))
