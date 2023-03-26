from threading import Thread
import webbrowser
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
from todoist_api_python.api import TodoistAPI
from cms_scrapper import CourseItem, Course
from config import Config

TODOIST_CLIENT_ID = '95f69e7339ad43a1a6217574f45115c5'
TODOIST_CLIENT_SECRET = '8043a99ef29746e4aa482bdb666cc738'
TODOIST_AUTHORIZE_URL = f'https://todoist.com/oauth/authorize?client_id={TODOIST_CLIENT_ID}&scope=data:read_write'
TODOIST_GET_TOKEN_URL = 'https://todoist.com/oauth/access_token'
SERVER_PORT = 5199


def get_todoist_auth_code():
    class AuthorizeServer(BaseHTTPRequestHandler):
        auth_code = ''
        token_retrieved = False

        def do_GET(self):
            AuthorizeServer.token_retrieved = True
            AuthorizeServer.auth_code = parse_qs(
                urlparse(self.path).query)['code'][0]
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(
                bytes('Authorization completed. You can close this.', 'utf-8'))

        def log_message(self, format, *args):
            return

    webbrowser.open(TODOIST_AUTHORIZE_URL)
    server = HTTPServer(('', SERVER_PORT), AuthorizeServer)

    while not AuthorizeServer.token_retrieved:
        server.handle_request()

    return AuthorizeServer.auth_code


def get_todoist_token(auth_code):
    req = requests.post(url=TODOIST_GET_TOKEN_URL, data={
        'client_id': TODOIST_CLIENT_ID,
        'client_secret': TODOIST_CLIENT_SECRET,
        'code': auth_code
    })

    data = req.json()

    return data['access_token']


def create_uni_project(token):
    todoist = TodoistAPI(token)
    project = todoist.add_project('Uni')

    return project.id


class TodoistHelper:
    def __init__(self, config: Config):
        self.todoist = TodoistAPI(config.todoist_token)
        self.config = config

    def add_task_for_course_item(self, course: Course, item: CourseItem):
        course_alias = self.config.course_aliases[course.id]
        course_section = self.config.todoist_courses_sections[course.id]

        def addTask():
            self.todoist.add_task(
                content=f'__{course_alias}__ | {item.title}',
                project_id=self.config.todoist_project_id,
                labels=[item.type],
                section_id=course_section,
                description=item.full_link
            )

        Thread(target=addTask).start()

    def create_courses_sections(self):
        created_sections = {}

        for course_id, course_alias in self.config.course_aliases.items():
            if course_id not in self.config.todoist_courses_sections:
                section = self.todoist.add_section(
                    project_id=self.config.todoist_project_id, name=course_alias)
                created_sections[course_id] = section.id

        return created_sections

    def add_course_announcement(self, course_id, announcement):
        course_alias = self.config.course_aliases[course_id]
        course_section = self.config.todoist_courses_sections[course_id]

        self.todoist.add_task(
            content=f'__{course_alias}__ | Announcement',
            description=announcement,
            project_id=self.config.todoist_project_id,
            section_id=course_section,
            labels=['announcement']
        )
