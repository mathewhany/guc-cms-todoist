from initializer import initialize
from config import load_config
from cms_scrapper import CmsScrapper, load_courses, save_courses, Course
from todoist_helpers import TodoistHelper


def main():
    initialize()

    config = load_config()

    scrapper = CmsScrapper(config.guc_username, config.guc_password)
    todoist = TodoistHelper(config.todoist_token, config.todoist_project_id)

    old_courses_data = load_courses()
    new_courses_data = scrapper.get_courses()

    for course_id, course in new_courses_data.items():
        if course_id not in old_courses_data:
            print(f"A new course ({course.code} | {course.title} has been discovered." )
            course.alias = input(f"Choose an alias for it (Default: {course.code}) ")
            old_courses_data[course_id] = Course(course.code, course.title, course.id, course.season, {}, course.alias)
            
        for item_link, item in course.material.items():
            if item_link not in old_courses_data[course_id].material:
                todoist.add_task_for_course_item(course, item)
                print(f'{course.alias} | {item.title} | {item.full_link}')

    save_courses(new_courses_data)


if __name__ == '__main__':
    main()
