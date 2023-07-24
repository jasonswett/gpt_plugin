import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from .openai_api_response_content import OpenAIAPIResponseContent

def test_code_block_with_ruby_code_block():
    body = 'test_spec.rb\n"rspec test_spec.rb"\n\n```ruby\nRSpec.describe "stuff" do\nend\n```'

    content = OpenAIAPIResponseContent(body)
    code = content.code_block()
    assert code == 'RSpec.describe "stuff" do\nend'

def test_code_block_with_python_code_block():
    body = 'test.py\n"pytest test.py"\n\n```python\ndef test_stuff():\n    assert True\n```'

    content = OpenAIAPIResponseContent(body)
    code = content.code_block()
    assert code == 'def test_stuff():\n    assert True'

def test_filename_extraction():
    body = 'test_spec.rb\n"rspec test_spec.rb"\n\n```ruby\nRSpec.describe "stuff" do\nend\n```'

    content = OpenAIAPIResponseContent(body)
    filename = content.filename()
    assert filename == 'test_spec.rb'

def test_sloppy_filename_extraction():
    body = 'filename: test_spec.rb\n"rspec test_spec.rb"\n\n```ruby\nRSpec.describe "stuff" do\nend\n```'

    content = OpenAIAPIResponseContent(body)
    filename = content.filename()
    assert filename == 'test_spec.rb'

def test_test_command_extraction():
    body = 'test_spec.rb\n"rspec test_spec.rb"\n\n```ruby\nRSpec.describe "stuff" do\nend\n```'

    content = OpenAIAPIResponseContent(body)
    test_command = content.test_command()
    assert test_command == 'rspec test_spec.rb'

def test_sloppy_test_command_extraction():
    body = 'test_spec.rb\n"test command: rspec test_spec.rb"\n\n```ruby\nRSpec.describe "stuff" do\nend\n```'

    content = OpenAIAPIResponseContent(body)
    test_command = content.test_command()
    assert test_command == 'rspec test_spec.rb'

def test_sloppy_test_command_extraction_2():
    body = 'test_spec.rb\nThe test command is: "rspec test_spec.rb"\n\n```ruby\nRSpec.describe "stuff" do\nend\n```'

    content = OpenAIAPIResponseContent(body)
    test_command = content.test_command()
    assert test_command == 'rspec test_spec.rb'
