import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from .openai_api_response_content import OpenAIAPIResponseContent

def test_code_block_with_code_block():
    body = "test_spec.rb\n\n```ruby\nRSpec.describe \"stuff\" do\nend\n```"

    content = OpenAIAPIResponseContent(body)
    code = content.code_block()
    assert code == "RSpec.describe \"stuff\" do\nend"
