import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from gpt_plugin import GptPlugin

def test_code_block_with_code_block():
    plugin = GptPlugin(None)

    content = """
    Here is some code:
    ```python
    def test():
    assert True
    ```
    """

    response = {
        'choices': [
            {
                'message': {
                    'content': content
                }
            }
        ]
    }

    code = plugin.code_block(response)
    assert code == "def test():\n    assert True"

def test_code_block_without_code_block():
    plugin = GptPlugin(None)

    response = {
        'choices': [
            {
                'message': {
                    'content': "There is no code block present"
                }
            }
        ]
    }

    code = plugin.code_block(response)
    assert code is None
