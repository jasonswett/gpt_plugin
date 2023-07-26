import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import os
import pytest
from pynvim import attach
from gpt_plugin_package.editor import Editor

@pytest.fixture(scope="module")
def nvim():
    return attach('child', argv=["/usr/bin/env", "nvim", "-u", "NONE", "-N", "--embed", "--headless"])

def test_current_filename(nvim):
    directory = '.'
    editor = Editor(nvim, directory)
    file_path = os.path.join(directory, "test_file.rb")
    with open(file_path, "w") as f:
        f.write("print('Hello, World!')")
    nvim.command(f"edit {file_path}")
    assert editor.current_filename() == "test_file.rb"
    os.remove(file_path)
