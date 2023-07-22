import re

class OpenAIAPIResponseContent:
    def __init__(self, body):
        self.body = body

    def code_block(self):
        filename_content = self.body.split('\n', 1)

        if len(filename_content) < 2:
            return None

        code_content = filename_content[1].strip()

        # Remove code fences
        code_content = re.sub(r'```.*$', '', code_content, flags=re.MULTILINE)  # remove the opening code fence
        code_content = code_content.rstrip("`")  # remove the closing code fence
        return code_content.strip()  # return the content part after stripping the leading and trailing whitespaces
