import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from gpt_plugin import GptPlugin

def test_code_block_with_code_block():
    plugin = GptPlugin(None)

    response = {
      "id": "chatcmpl-7esy9Xuc3Fjuakwa8wp1BCpya5rkE",
      "object": "chat.completion",
      "created": 1689978777,
      "model": "gpt-3.5-turbo-0613",
      "choices": [
        {
          "index": 0,
          "message": {
            "role": "assistant",
            "content": "test_spec.rb\n\n```ruby\nRSpec.describe \"stuff\" do\nend\n```"
          },
          "finish_reason": "stop"
        }
      ],
      "usage": {
        "prompt_tokens": 72,
        "completion_tokens": 51,
        "total_tokens": 123
      }
    }

    code = plugin.code_block(response)
    assert code == "RSpec.describe \"stuff\" do\nend"
