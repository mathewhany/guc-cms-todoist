import os.path
import jsonpickle

CONFIG_FILE = 'config.json'


class Config:
    def __init__(self, guc_username, guc_password, todoist_token, todoist_project_id, openai_api_key = ''):
        self.guc_username = guc_username
        self.guc_password = guc_password
        self.todoist_token = todoist_token
        self.todoist_project_id = todoist_project_id
        self.course_aliases = {}
        self.todoist_courses_sections = {}
        self.openai_api_key = openai_api_key


def save_config(config: Config):
    with open(CONFIG_FILE, 'w+') as f:
        f.write(jsonpickle.encode(config))


def load_config() -> Config:
    if not os.path.isfile(CONFIG_FILE):
        return Config()

    with open(CONFIG_FILE, 'r') as f:
        return jsonpickle.decode(f.read())


def is_configured():
    return os.path.isfile(CONFIG_FILE)
