LOG_FILENAME = '/Users/jasonswett/Documents/code/gpt_plugin/log/gpt_plugin.log'

class APILogger:
    def write(self, message):
        with open(LOG_FILENAME, 'a') as f:
            f.write(f"{message}\n")

