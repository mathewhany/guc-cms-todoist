from todoist_helpers import get_todoist_token, get_todoist_auth_code, create_uni_project
from cms_scrapper import CmsScrapper, save_courses, has_saved_courses
from config import Config, is_configured, save_config, load_config


def ask_for_credentials():
    guc_username = input('What is your GUC username? ')
    guc_password = input('What is your GUC password? ')
    todoist_auth_code = get_todoist_auth_code()
    todoist_token = get_todoist_token(todoist_auth_code)
    todoist_project_id = create_uni_project(todoist_token)

    return Config(guc_username, guc_password, todoist_token, todoist_project_id)


def initialize():
    if not is_configured():
        config = ask_for_credentials()
        save_config(config)

    if not has_saved_courses():
        config = load_config()

        scrapper = CmsScrapper(config.guc_username, config.guc_password)
        courses = scrapper.get_courses()

        save_courses(courses)
