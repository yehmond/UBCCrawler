import bs4
import requests
import time
import json


class CourseScraper:
    """Command line app that scrapes the given session's course sections into a json file found in ./resources"""

    def __init__(self):
        self.course_dict = {}
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:46.0) Gecko/20100101 Firefox/46.0'}
        self.start_time = 0
        self.ubc_url = 'https://courses.students.ubc.ca/cs/courseschedule?'

    def get_user_input(self):
        print()
        while True:
            year_session = input("Enter year session (Ex: 2019 W): ")
            try:
                year = int(year_session.split()[0])
                session = year_session.split()[1].upper()
                if session != 'W' and session != 'S':
                    raise Exception('Please enter a valid year session!')
                break
            except ValueError:
                print("Please input a valid year session!")
        print("Starting crawler...")
        print("....................................................................")
        print()
        self.start_time = time.time()

        return year_session

    def crawl(self, year, session):
        """Creates a JSON file containing the courses and their respective sections. """

        payload = {'tname': 'subj-all-departments',
                   'sessyr': year,
                   'sesscd': session.upper(),
                   'pname': 'subjarea'}

        # Get HTML from website
        response = requests.get(self.ubc_url, params=payload,
                                headers=self.headers, timeout=15)

        # Passes the html object to Beautiful Soup
        soup = bs4.BeautifulSoup(response.text, 'lxml')

        # Extracting the subjects table
        subject_table = soup.find("table", attrs={'id': 'mainTable'}).findNext('tbody')

        subjects = []

        # Iterate through courses, which contains all the <tr> objects
        for row in subject_table:
            # Find <td> tag
            data = row.find('td')

            '''
            The first condition, isinstance(course, bs4.element.Tag), prevents accessing an int object at the end
            of the list. The second condition, course.find('b') is None, prevents adding courses not offered in the
            current session, which is indicated by a <b> tag. Thus if there is no <b> tag, the course is offered this
            session
            '''

            if isinstance(data, bs4.element.Tag) and data.find('b') is None:
                subjects.append(data.text)

        # Call crawl_subject() on every subject from subjects
        for subject in subjects:
            print('Crawling {}......................................'.format(subject))
            self.course_dict[subject] = {}
            self.crawl_subject(year, session.upper(), subject)

        # Export JSON file
        with open('./resources/' + year + session.upper() + '.json', 'w') as f:
            json.dump(self.course_dict, f, indent=1)

        print()
        print('##############################################')
        print('Runtime:', time.time() - self.start_time, 'seconds')
        print('##############################################')

    def crawl_subject(self, year, session, subject):
        """Creates course code entries in self.course_dict of the given subject"""

        payload = {'tname': 'subj-department',
                   'sessyr': year,
                   'sesscd': session,
                   'dept': subject,
                   'pname': 'subjarea'}

        response = requests.get(self.ubc_url, params=payload,
                                headers=self.headers, timeout=15)
        soup = bs4.BeautifulSoup(response.text, 'lxml')

        course_table = soup.find('table', attrs={'id': 'mainTable'}).findNext('tbody')
        courses = []

        # Iterate through sections, which contains all the <tr> objects
        for row in course_table:
            # Find <td> tag
            data = row.find('td')

            if isinstance(data, bs4.element.Tag):
                name = data.text
                # Extract only the section code without the course name from name
                code = name.split()[1]
                self.course_dict[subject][code] = []
                courses.append(code)

        for course in courses:
            print('.....Crawling', course)
            self.crawl_course(year, session, subject, course)

    def crawl_course(self, year, session, subject, course):
        """Creates entries of sections and their respective url links inside self.course_dict for the given course"""

        # time.sleep(1)

        payload = {'tname': 'subj-course',
                   'course': course,
                   'sessyr': year,
                   'sesscd': session,
                   'dept': subject,
                   'pname': 'subjarea'}

        response = requests.get(self.ubc_url, params=payload,
                                headers=self.headers, timeout=15)
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        section_table = soup.find('table', class_='table table-striped section-summary').find_all('a')

        for data in section_table:
            section = data.text.split()

            # if statement prevents adding incorrect text to self.course_dict
            if len(section) == 3:
                self.course_dict[subject][course].append(section[2])



if __name__ == '__main__':
    w = CourseScraper()
    year_session = w.get_user_input()
    w.crawl(year_session.split()[0], year_session.split()[1])
