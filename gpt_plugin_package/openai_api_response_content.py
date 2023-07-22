import re

class OpenAIAPIResponseContent:
    def __init__(self, body):
        self.body = body

    def filename(self):
        filename_content = self.body.split('\n', 1)
        if len(filename_content) < 1:
            return None
        return filename_content[0].strip()

    def code_block(self):
        code_content = self.body.split('\n', 1)[1]
        return re.sub(r'```.*$', '', code_content, flags=re.MULTILINE).rstrip("`").strip()
