import re
from threading import Thread
import bs4
import jsonpickle
import requests
import os
from enum import Enum
from requests_ntlm import HttpNtlmAuth
from config import Config

CMS_BASE_URL = 'https://cms.guc.edu.eg'
COURSES_TABLE_ID = '#ContentPlaceHolderright_ContentPlaceHoldercontent_GridViewcourses'

COURSES_DATA_FILE = 'courses.json'


class ItemType(str, Enum):
    LECTURE = 'Lecture'
    ASSIGNMENT = 'PA'
    PA_SOLUTION = 'PA Solutions'
    LAB_ASSINMENT = 'Lab Assignment'
    LAB_MANUAL = 'Lab Manual'
    LAB_SOLUTION = 'Lab Solution'
    OTHERS = 'Others'


def normalize_item_title(title: str, original_type: str):
    type = normalize_item_type(title, original_type)
    title = re.sub(r'^\d+\W*-', '', title).strip()

    if type == ItemType.OTHERS:
        return f'{title} {original_type}'

    numbers_at_end = re.findall(r'(\d+)\W*$', title)

    if not numbers_at_end:
        return title

    item_number = numbers_at_end[0]

    if type == ItemType.LECTURE:
        return f'Lecture {item_number}'

    if type == ItemType.ASSIGNMENT:
        return f'PA {item_number}'

    if type == ItemType.PA_SOLUTION:
        return f'PA {item_number} (Solutions)'

    if type == ItemType.LAB_ASSINMENT:
        return f'Lab Assignment {item_number}'

    if type == ItemType.LAB_MANUAL:
        return f'Lab Manual {item_number}'

    if type == ItemType.LAB_SOLUTION:
        return f'Lab Assignment {item_number} (Solutions)'


def normalize_item_type(item_title: str, item_type: str) -> ItemType:
    combined = item_title + item_type
    has_lecture = re.search('lecture', combined, re.IGNORECASE)
    has_lab = re.search('lab', combined, re.IGNORECASE)
    has_assignment = re.search('assignment', combined, re.IGNORECASE)
    has_solution = re.search('solution', combined, re.IGNORECASE)

    if has_lecture:
        return ItemType.LECTURE

    if has_lab:
        if has_solution:
            return ItemType.LAB_SOLUTION
        elif has_assignment:
            return ItemType.LAB_ASSINMENT
        else:
            return ItemType.LAB_MANUAL

    if has_assignment:
        if has_solution:
            return ItemType.PA_SOLUTION
        else:
            return ItemType.ASSIGNMENT

    return ItemType.OTHERS


class CourseItem:
    def __init__(self, item_title, item_full_link, type: ItemType):
        self.title = item_title
        self.full_link = item_full_link
        self.type = type


class Course:
    material: dict[str, CourseItem]

    def __init__(self, code, title, id, season, material={}, announcements=""):
        self.code = code
        self.title = title
        self.id = id
        self.season = season
        self.material = material
        self.announcements = announcements


class CmsScrapper:
    cached_courses: dict[str, Course] = {}
    cached_pages: dict[str, bs4.BeautifulSoup] = {}

    def __init__(self, config):
        self.config = config

    def scrap_cms_page(self, uri):
        if uri not in CmsScrapper.cached_pages:
            req = requests.get(
                CMS_BASE_URL + uri, auth=HttpNtlmAuth(self.config.guc_username, self.config.guc_password))
            CmsScrapper.cached_pages[uri] = bs4.BeautifulSoup(
                req.content, 'html.parser')

        return CmsScrapper.cached_pages[uri]

    def get_courses(self) -> dict[str, Course]:
        if CmsScrapper.cached_courses:
            print("Using cached courses...")
            return CmsScrapper.cached_courses

        soup = self.scrap_cms_page('/')
        courses_table = soup.select_one(COURSES_TABLE_ID)

        courses: dict[str, Course] = {}

        def scrap_course(course_id, season):
            courses[course_id].material = self.get_course_material(
                course_id, season)
            courses[course_id].announcements = self.get_course_announcements(
                course_id, season)

        threads = []
        for course_row in courses_table.select('tr')[1:]:
            course_columns = course_row.find_all('td')
            course_label = course_columns[1].get_text(strip=True)
            season = course_columns[-1].get_text(strip=True)

            course_code, course_title, course_id = re.findall(
                r'\(\|(.*)\|\) (.*) \((.*)\)', course_label)[0]

            courses[course_id] = Course(
                course_code, course_title, course_id, season)

            thread = Thread(target=scrap_course, args=(course_id, season))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        CmsScrapper.cached_courses = courses

        return courses

    def scrap_course_page(self, course_id, season):
        return self.scrap_cms_page(
            f'/apps/student/CourseViewStn?id={course_id}&sid={season}')

    def get_course_material(self, course_id, season):
        soup = self.scrap_course_page(course_id, season)
        items = {}

        for link in soup.select('#download'):
            item_title_tag = link.find_parent(
                attrs={'class': 'card-body'}).find('div').find('strong')
            item_extracted_title = item_title_tag.get_text(strip=True)
            item_extracted_type = item_title_tag.next_sibling.get_text(
                strip=True)
            item_full_link = CMS_BASE_URL + link['href']
            item_type = normalize_item_type(
                item_extracted_title, item_extracted_type)
            item_title = normalize_item_title(
                item_extracted_title, item_extracted_type)

            items[item_full_link] = CourseItem(
                item_title, item_full_link, item_type)

        return items

    def get_course_announcements(self, course_id, season):
        # https://stackoverflow.com/questions/30337528/make-beautifulsoup-handle-line-breaks-as-a-browser-would
        def get_text(tag: bs4.Tag) -> str:
            _inline_elements = {"a", "span", "em", "strong", "u", "i", "font", "mark", "label",
                                "s", "sub", "sup", "tt", "bdo", "button", "cite", "del", "b", "a", "font", }

            def _get_text(tag: bs4.Tag):
                for child in tag.children:
                    if isinstance(child, bs4.Tag):
                        # if the tag is a block type tag then yield new lines before after
                        is_block_element = child.name not in _inline_elements

                        if is_block_element:
                            yield "\n"
                        if child.name == 'br':
                            yield "\n"
                        elif child.name == 'a':
                            yield f'[{child.text}]({child.attrs["href"]})'
                        else:
                            yield from _get_text(child)
                        if is_block_element:
                            yield "\n"
                    elif isinstance(child, bs4.NavigableString):
                        yield child.string

            return "".join(_get_text(tag))

        soup = self.scrap_course_page(course_id, season)
        announcements_container = soup.select_one('#ContentPlaceHolderright_ContentPlaceHoldercontent_desc')
        announcements = get_text(announcements_container)
        return announcements


def save_courses(courses: list[Course]):
    with open(COURSES_DATA_FILE, 'w+') as f:
        f.write(jsonpickle.encode(courses))


def load_courses() -> dict[str, Course]:
    if not os.path.isfile(COURSES_DATA_FILE):
        return {}

    with open(COURSES_DATA_FILE, 'r') as f:
        courses = jsonpickle.decode(f.read())

        for course_id in courses:
            if not hasattr(courses[course_id], 'announcements'):
                courses[course_id].announcements = ""

        return courses


def has_saved_courses():
    return os.path.isfile(COURSES_DATA_FILE)
