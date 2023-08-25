import logging
import os

class Logger:
    def __init__(self):
        self.logs = []

    def add_log(self, log):
        self.logs.append(log)
        if len(self.logs) > 200:
            self.logs = self.logs[-200:]

    def get_logs(self):
        return '\n'.join(self.logs)
    
class LogHandler(logging.Handler):
    def __init__(self, text_input : list):
        super().__init__()
        self.text_input = text_input

    def emit(self, record):
        log_entry = self.format(record)
        self.text_input.append(log_entry)

def delete_directory(path):
    if os.path.exists(path):
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    delete_directory(item_path)
            os.rmdir(path)

def empty_directory(path):
    if os.path.exists(path) and os.listdir(path):
        delete_directory(path)
        os.makedirs(path)