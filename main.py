from initializer import initialize
from config import load_config
from cms_scrapper import CmsScrapper, load_courses, save_courses
from todoist_helpers import TodoistHelper


def main():
    initialize()

    config = load_config()

    scrapper = CmsScrapper(config.guc_username, config.guc_password)
    todoist = TodoistHelper(config.todoist_token, config.todoist_project_id)

    old_courses_data = load_courses()
    new_courses_data = scrapper.get_courses()

    for course_id, course in new_courses_data.items():
        for item_link, item in course.material.items():
            if not old_courses_data or item_link not in old_courses_data[course_id].material:
                todoist.add_task_for_course_item(course, item)
                print(f'{course.code} | {item.title} | {item.full_link}')

    save_courses(new_courses_data)


if __name__ == '__main__':
    main()
