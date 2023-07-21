from gpt_plugin import GptPlugin

def test_parse_response_with_code_block():
    plugin = GptPlugin(None)

    response = """
    Here is some code:
    ```python
    def test():
    assert True
    ```
    """

    code = plugin.parse_response(response)
    assert code == "def test():\n    assert True"

def test_parse_response_without_code_block():
    plugin = GptPlugin(None)

    response = """
    There is no code block present
    """

    code = plugin.parse_response(response)
    assert code is None
