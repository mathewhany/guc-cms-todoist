import pickle
import os.path

CONFIG_FILE = 'config.pkl'


class Config:
    def __init__(self, guc_username, guc_password, todoist_token, todoist_project_id):
        self.guc_username = guc_username
        self.guc_password = guc_password
        self.todoist_token = todoist_token
        self.todoist_project_id = todoist_project_id
        self.course_aliases = {}


def save_config(config: Config):
    with open(CONFIG_FILE, 'wb+') as f:
        pickle.dump(config, f)


def load_config():
    with open(CONFIG_FILE, 'rb') as f:
        return pickle.load(f)


def is_configured():
    return os.path.isfile(CONFIG_FILE)
