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
        matches = re.findall(r'```(\w+)(.*)```', self.body, re.DOTALL)
        return matches[0][1].strip() if matches else None
