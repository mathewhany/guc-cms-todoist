from chatgpt_helper import ChatGPTHelper
from initializer import initialize
from config import load_config
from cms_scrapper import CmsScrapper, load_courses, save_courses, Course
from todoist_helpers import TodoistHelper


def main():
    initialize()

    config = load_config()

    scrapper = CmsScrapper(config)
    todoist = TodoistHelper(config)
    chatgpt = ChatGPTHelper(config)

    old_courses_data = load_courses()

    print("Checking for new course material...")
    new_courses_data = scrapper.get_courses()
    found_updates = False

    for course_id, course in new_courses_data.items():
        old_announcement = old_courses_data[
            course_id].announcements if course_id in old_courses_data else ''
        new_announcement = course.announcements

        if new_announcement and old_announcement != new_announcement:
            found_updates = True
            announcement = new_announcement.replace(old_announcement, '')
            if announcement.strip() != '':
                announcement_title = chatgpt.generate_title_for_announcement(
                    announcement)
                announcement_content = chatgpt.get_announcement_content(
                    announcement, course)
                print(
                    f'{config.course_aliases[course_id]} | {announcement_title}')
                todoist.add_course_announcement(
                    course_id, announcement_title, announcement_content)

        for item_link, item in course.material.items():
            if course_id not in old_courses_data or item_link not in old_courses_data[course_id].material:
                found_updates = True
                todoist.add_task_for_course_item(course, item)
                print(
                    f'{config.course_aliases[course_id]} | {item.title} | {item.full_link}')

    if not found_updates:
        print("No new material found. Everything has already been added to your Todoist account.")

    save_courses(new_courses_data)


if __name__ == '__main__':
    main()
