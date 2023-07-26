import os

class Editor:
    def __init__(self, nvim, directory):
        self.nvim = nvim
        self.directory = directory

    def current_filename(self):
        return os.path.relpath(self.nvim.current.buffer.name, self.directory)
