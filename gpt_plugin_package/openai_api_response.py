from .openai_api_response_content import OpenAIAPIResponseContent

class OpenAIAPIResponse:
    def __init__(self, body):
        self.body = body

    def code_block(self):
        return OpenAIAPIResponseContent(self.body['choices'][0]['message']['content']).code_block()
