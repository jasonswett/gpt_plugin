import os

class Editor:
    def __init__(self, nvim, directory):
        self.nvim = nvim
        self.directory = directory

    def current_filename(self):
        return os.path.relpath(self.nvim.current.buffer.name, self.directory)

    def insert_code_block(self, filename, code_block):
        if not code_block:
            self.nvim.current.buffer[:] = ["No code found in response"]
            return

        if self.is_buffer_with_filename_open(filename):
            self.nvim.command(f'buffer {filename}')
        else:
            if not self.is_current_buffer_empty():
                self.nvim.command('tabnew')

        self.nvim.current.buffer[:] = code_block.split('\n')
        path = os.path.join(self.directory, filename)
        self.save_file(path)

    def is_buffer_with_filename_open(self, filename):
        all_open_buffers = self.nvim.buffers
        return any([buffer.name.endswith(filename) for buffer in all_open_buffers])

    def is_current_buffer_empty(self):
        current_buffer_name = self.nvim.eval('bufname("%")')
        return current_buffer_name == ""

    def save_file(self, filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        self.nvim.command(f'w! {filename}')

    def all_file_contents(self):
        all_file_contents = []

        for buffer in self.nvim.buffers:
            if buffer.name:  # Check if the buffer is associated with a file
                relative_path = os.path.relpath(buffer.name, self.directory)
                file_content = "\n".join(buffer[:])
                all_file_contents.append("{}{}".format(relative_path, file_content))

        return "\n".join(all_file_contents)

    def current_buffer_content(self):
        return "\n".join(self.nvim.current.buffer[:])
