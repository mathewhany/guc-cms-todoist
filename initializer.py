from todoist_helpers import get_todoist_token, get_todoist_auth_code, create_uni_project
from cms_scrapper import CmsScrapper, save_courses, has_saved_courses
from config import Config, is_configured, save_config, load_config

def show_welcome_message():
    print("Welcome to CmsNotifier!")
    print("CmsNotifier is a tool that notifies you about new course material on the GUC CMS.")

def ask_for_credentials():
    print("CmsNotifier needs to be configured first. This is a one-time process.")
    print("This tool requires your GUC credentials to access the CMS.")
    print("Don't worry, your credentials are stored locally and are not shared with anyone.")
    guc_username = input('What is your GUC username? ')
    guc_password = input('What is your GUC password? ')
    print("Now, we need to authorize CmsNotifier to access your Todoist account.")
    print("A browser window will open, please authorize CmsNotifier to access your Todoist account.")
    todoist_auth_code = get_todoist_auth_code()
    todoist_token = get_todoist_token(todoist_auth_code)
    print("CmsNotifier is now authorized to access your Todoist account.")
    print("CmsNotifier will create a new project called 'Uni' in your Todoist account to store the course material notifications.")
    todoist_project_id = create_uni_project(todoist_token)

    return Config(guc_username, guc_password, todoist_token, todoist_project_id)

def discover_courses():    
    print("Discovering new courses...")
    config = load_config()
    scrapper = CmsScrapper(config)
    courses = scrapper.get_courses()
    found_new_courses = False

    for course_id, course in courses.items():
        if course_id not in config.course_aliases:
            found_new_courses = True
            alias = input(f'Choose an alias for {course.title} ({course.code}) [Leave empty for {course.code}]: ')
            config.course_aliases[course_id] = alias or course.code

    if not found_new_courses:
        print("No new courses discovered.")

    save_config(config)


def initialize():
    show_welcome_message()
    
    if not is_configured():
        config = ask_for_credentials()
        save_config(config)

    discover_courses()