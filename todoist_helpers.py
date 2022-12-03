import webbrowser
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
from todoist_api_python.api import TodoistAPI
from cms_scrapper import CourseItem, Course

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
            AuthorizeServer.auth_code = parse_qs(urlparse(self.path).query)['code'][0]
            self.send_response(200)
            self.send_header('Content-Type', 'text/html');
            self.end_headers()
            self.wfile.write(bytes('Authorization completed. You can close this.', 'utf-8'))

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
    def __init__(self, token, project_id):
        self.todoist = TodoistAPI(token)
        self.project_id = project_id

    def add_task_for_course_item(self, course: Course, item: CourseItem):
        self.todoist.add_task(
            content=course.code + ' ' + item.title,
            project_id=self.project_id,
            labels=[course.code],
            description=item.full_link
        )
