import openai
from cms_scrapper import Course
from config import Config


class ChatGPTHelper:
    def __init__(self, config: Config):
        openai.api_key = config.openai_api_key
        self.model = 'gpt-3.5-turbo'

    def generate_title_for_announcement(self, announcement):
        res = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "user", "content": f"Give me a short title for this announcement: {announcement}"},
            ]
        )

        return res['choices'][0]['message']['content']

    def get_announcement_content(self, announcement, course: Course):
        is_exam = 'yes' in openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "user", "content": f"Does this announcement include an exam, quiz or test or anykind? Answer with yes/no only.: '{announcement}'"},
            ]
        )['choices'][0]['message']['content'].lower()

        if is_exam:
            course_content = ""
            for item in course.material.values():
                course_content += item.title + " => " + item.full_link + "\n"

            res = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": f"Here is a list of all course content: {course_content}"},
                    { "role": "user", "content": f"Try to be funny cheerful and positive. Use emojis.'"},
                    {"role": "user", "content": f"From the list of couse content, what do I need to study for this announcement, include links: {announcement}"},
                ]
            )

            return res['choices'][0]['message']['content']
        else:
            return announcement
