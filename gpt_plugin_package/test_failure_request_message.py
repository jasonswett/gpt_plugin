class TestFailureRequestMessage:
    __test__ = False

    def __init__(self, filename, buffer_content, failure_message):
        self.filename = filename
        self.buffer_content = buffer_content
        self.failure_message = failure_message

    def __str__(self):
        return f"""
This is my test:
{self.filename}
{self.buffer_content}

Here is the failure message:
{self.failure_message}

Write me the code that will make this failure message go away."""
