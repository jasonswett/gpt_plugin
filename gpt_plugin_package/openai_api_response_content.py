import re

class OpenAIAPIResponseContent:
    def __init__(self, body):
        self.body = body

    def filename(self):
        filename_content = self.body.split('\n', 2)
        if len(filename_content) < 2:
            return None
        filename_line = filename_content[0].strip()
        return filename_line.replace('filename: ', '')

    def code_block(self):
        lines = self.body.split('\n')
        return '\n'.join(lines[2:-1])
