from initializer import initialize
from config import load_config
from cms_scrapper import CmsScrapper, load_courses, save_courses, Course
from todoist_helpers import TodoistHelper


def main():
    initialize()

    config = load_config()

    scrapper = CmsScrapper(config)
    todoist = TodoistHelper(config)

    old_courses_data = load_courses()
    
    print("Checking for new course material...")
    new_courses_data = scrapper.get_courses()
    found_new_material = False

    for course_id, course in new_courses_data.items():            
        for item_link, item in course.material.items():
            if course_id not in old_courses_data or item_link not in old_courses_data[course_id].material:
                found_new_material = True
                todoist.add_task_for_course_item(course, item)
                print(f'{config.course_aliases[course_id]} | {item.title} | {item.full_link}')
    
    if not found_new_material:
        print("No new material found. Everything has already been added to your Todoist account.")

    save_courses(new_courses_data)


if __name__ == '__main__':
    main()
