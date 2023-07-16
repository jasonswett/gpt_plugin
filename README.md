# GptPlugin for Neovim

The GptPlugin is a Neovim plugin that connects your text editor to OpenAI's GPT-3 model. You can use this plugin to generate code snippets directly in your current buffer.

## Features

- Generate code snippets using OpenAI's GPT-3 model
- User-customizable prompts for GPT-3
- Ability to clear the current buffer and replace it with the AI-generated code
- Error handling for cases when no code is returned

## Installation

Before you begin, make sure you have [Neovim](https://neovim.io/) installed.

1. Clone the GptPlugin repository to your local machine:

    ```bash
    git clone https://github.com/YOUR_GITHUB_USERNAME/gpt_neovim.git
    ```

2. Create a symbolic link from the GptPlugin directory to your Neovim remote plugin directory:

    ```bash
    ln -s /path/to/your/gpt_neovim/gpt_plugin.py ~/.config/nvim/rplugin/python3/gpt_plugin.py
    ```

3. Open Neovim and run the command `:UpdateRemotePlugins` then restart Neovim.

## Usage

Use the `:Gpt` command in command mode, followed by the prompt that you want to send to GPT-3.

```vim
:Gpt write a function that reverses a string
```

The plugin will then replace the current buffer with the generated code. If no code is found in the response, the buffer will be replaced with a message saying "No code found in response".

## Setting up OpenAI API key

You need to have your OpenAI API key as an environment variable named `OPENAI_API_KEY`. You can set this in your shell's configuration file (like `.bashrc` or `.zshrc`) as follows:

```bash
export OPENAI_API_KEY='your-openai-api-key'
```

Remember to replace 'your-openai-api-key' with your actual OpenAI API key.

## Contributions

Contributions are welcome! Feel free to open a pull request.

## License

[MIT](LICENSE)

---

Please replace `YOUR_GITHUB_USERNAME` with your actual GitHub username and `/path/to/your/gpt_neovim/` with the actual path to your cloned repository.

Don't forget to also include a LICENSE file in your repository if you choose to specify a license. If you don't know which license to use, [choosealicense.com](https://choosealicense.com/) is a great resource to help you pick an appropriate license for your project.
