import requests
import bs4
import time
import re
from ubccrawler import mail


class SeatScraper:

    def __init__(self, main_window):
        self.main_window = main_window
        self.prev = 0
        self.curr = 0
        self.count = 0
        self.start_time = time.time()

    def crawl(self, year, session, subject, course_num, section, receiver_email, general_seats_only):

        self.count += 1

        try:

            payload = {'sesscd': session,
                       'pname': 'subjarea',
                       'tname': 'subj-section',
                       'sessyr': year,
                       'course': course_num,
                       'section': section,
                       'dept': subject
                       }

            # GET request
            response = requests.get('https://courses.students.ubc.ca/cs/courseschedule?', params=payload, timeout=15)
            # response.text contains all web page content
            soup = bs4.BeautifulSoup(response.text, 'lxml')
            # Find desired table from soup
            table = soup.find('table', class_="\'table").text

            # Get number of seats available for each type
            total_seats = self.get_seat_num("Total Seats Remaining", table)
            currently_registered = self.get_seat_num("Currently Registered", table)
            general_seats = self.get_seat_num("General Seats Remaining", table)
            restricted_seats = self.get_seat_num("Restricted Seats Remaining", table)

            seats_dict = self.form_table(year, session, subject, course_num, section, total_seats,
                                         general_seats, currently_registered, restricted_seats)
            self.prev = self.curr

            # If general seats only checkbox is checked, then self.curr will only be updated from general_seats number
            if general_seats_only:
                self.curr = int(general_seats)
            else:
                self.curr = max(int(restricted_seats), int(general_seats))

            # Send email if there is an empty seat available
            if self.prev == 0 and self.curr > 0:
                mail.send_mail(seats_dict, receiver_email)

            # Prints table on command line for debug purposes
            self.print_table(seats_dict)

            self.change_statusbar('Waiting until restart...')
            return seats_dict

        except requests.exceptions.ConnectionError as e:
            print("Error connecting: ", e)
            print()
            print("Retrying...")
            self.change_statusbar("Error connecting: " + str(e) + ". Retrying...")
            return {}
        except requests.exceptions.Timeout as e:
            print("Request time out")
            self.change_statusbar("Request time out: " + str(e) + ". Retrying...")
            return {}
        except requests.exceptions.HTTPError as e:
            print("HTTP Error!", e)
            self.change_statusbar("HTTP Error!" + str(e))
            return {}
        except requests.exceptions.RequestException as e:
            print(e)
            self.change_statusbar(str(e))
            return {}
        except IndexError as e:
            print("Table \" Seats Remaining\" not found!")
            self.change_statusbar(str(e) + ": Are you sure you entered a valid course section?")
            return {}
        except AttributeError as e:
            print('Attribute Error:', e)
            self.change_statusbar(str(e) + ": Are you sure you entered a valid course section?")
            return {}

    def get_seat_num(self, text, table):
        """ Extracts seat number from table html text  """

        string_index = table.index(text)
        # Using regex to extract only digits from the substrings
        return re.sub(r'\D', "", table[string_index + len(text): string_index + len(text) + 4])

    @staticmethod
    def form_table(year, session, subject, course_num, section, total_seats,
                   general_seats, currently_registered, restricted_seats):
        """Creates table to be displayed on the textBrowser """

        curr_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        return {"Session: ": year + session,
                "Course Name: ": subject + ' ' + course_num + ' ' + section,
                "Total Seats: ": total_seats,
                "General Seats: ": general_seats,
                "Currently Registered: ": currently_registered,
                "Restricted Seats: ": restricted_seats,
                "Updated On: ": str(curr_time)}

    def change_statusbar(self, text):
        self.main_window.statusBar().showMessage(text)

    def reset(self):
        self.prev = self.curr = 0

    def print_table(self, table):
        print('########################')
        for key, value in table.items():
            print(key + ': ' + value)
        print('Requests sent:', self.count)
        print('Total runtime:', round(time.time() - self.start_time, 3), 'seconds')
        print('########################')
        print()




