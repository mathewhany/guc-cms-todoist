import re
import bs4
import requests
import pickle
import os
from enum import Enum
from requests_ntlm import HttpNtlmAuth

CMS_BASE_URL = 'https://cms.guc.edu.eg'
COURSES_TABLE_ID = '#ContentPlaceHolderright_ContentPlaceHoldercontent_GridViewcourses'

COURSES_DATA_FILE = 'courses.pkl'


def normalize_item_title(title):
    number_matches = re.compile(r'\d+\W*-\D+(\d+|\d+.\d+)\D*\(.*\)').findall(title)

    if len(number_matches) != 1:
        return title

    num = number_matches[0]
    item_type = get_item_type(title)

    if item_type == ItemType.LECTURE:
        return 'Lecture ' + num
    elif item_type == ItemType.SOLUTION:
        return f'Assignment {num} Solutions'
    elif item_type == ItemType.ASSIGNMENT:
        return 'Assignment ' + num
    else:
        return title


def get_item_type(item_title):
    if re.search('lecture', item_title, re.IGNORECASE):
        return ItemType.LECTURE

    if re.search('assignment', item_title, re.IGNORECASE):
        return ItemType.ASSIGNMENT

    if re.search('solution', item_title, re.IGNORECASE):
        return ItemType.SOLUTION

    return ItemType.OTHERS


class ItemType(Enum):
    LECTURE = 'Lecture'
    ASSIGNMENT = 'PA'
    SOLUTION = 'Solutions'
    OTHERS = 'Others'


class CourseItem:
    def __init__(self, item_title, item_full_link, type: ItemType):
        self.title = item_title
        self.full_link = item_full_link
        self.type = type


class Course:
    material: dict[str, CourseItem]

    def __init__(self, code, title, id, season, material):
        self.code = code
        self.title = title
        self.id = id
        self.season = season
        self.material = material


class CmsScrapper:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def scrap_cms_page(self, uri):
        req = requests.get(CMS_BASE_URL + uri, auth=HttpNtlmAuth(self.username, self.password))
        return bs4.BeautifulSoup(req.content, 'html.parser')

    def get_courses(self):
        soup = self.scrap_cms_page('/')
        courses_table = soup.select_one(COURSES_TABLE_ID)

        courses = {}

        for course_row in courses_table.select('tr')[1:]:
            course_columns = course_row.find_all('td')
            course_label = course_columns[1].get_text(strip=True)
            season = course_columns[-1].get_text(strip=True)

            course_code, course_title, course_id = re.findall(r'\(\|(.*)\|\) (.*) \((.*)\)', course_label)[0]
            material = self.get_course_material(course_id, season)

            courses[course_id] = Course(course_code, course_title, course_id, season, material)

        return courses

    def get_course_material(self, course_id, season):
        soup = self.scrap_cms_page(f'/apps/student/CourseViewStn?id={course_id}&sid={season}')
        items = {}

        for link in soup.select('#download'):
            item_original_title = link.find_parent(attrs={'class': 'card-body'}).find('div').get_text(strip=True)
            item_normalized_title = normalize_item_title(item_original_title)
            item_full_link = CMS_BASE_URL + link['href']
            item_type = get_item_type(item_original_title)
            items[item_full_link] = CourseItem(item_normalized_title, item_full_link, item_type)

        return items


def save_courses(courses: list[Course]):
    with open(COURSES_DATA_FILE, 'wb+') as f:
        pickle.dump(courses, f)


def load_courses() -> dict[str, Course]:
    if not os.path.isfile(COURSES_DATA_FILE):
        return {}

    with open(COURSES_DATA_FILE, 'rb') as f:
        return pickle.load(f)

def has_saved_courses():
    return os.path.isfile(COURSES_DATA_FILE)