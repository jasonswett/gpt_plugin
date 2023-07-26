import os

class Editor:
    def __init__(self, nvim, directory):
        self.nvim = nvim
        self.directory = directory

    def current_filename(self):
        return os.path.relpath(self.nvim.current.buffer.name, self.directory)

    def insert_code_block(self, filename, code_block):
        if code_block:
            if not self.is_buffer_with_filename_open(filename) and not self.is_current_buffer_empty():
                self.nvim.command('tabnew')

            self.nvim.current.buffer[:] = code_block.split('\n')
            path = os.path.join(self.directory, filename)
            self.save_file(path)
        else:
            self.nvim.current.buffer[:] = ["No code found in response"]

    def is_buffer_with_filename_open(self, filename):
        all_open_buffers = self.nvim.buffers
        return any([buffer.name.endswith(filename) for buffer in all_open_buffers])

    def is_current_buffer_empty(self):
        current_buffer_name = self.nvim.eval('bufname("%")')
        return current_buffer_name == ""

    def save_file(self, filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        self.nvim.command(f'w! {filename}')
