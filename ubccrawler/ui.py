from PyQt5.QtWidgets import QMainWindow, QApplication, QDesktopWidget, QMessageBox, QPushButton, QTextBrowser, \
    QComboBox, QGridLayout, QWidget, QLabel, QLineEdit, QCheckBox
from PyQt5.QtCore import QTimer
from ubccrawler import seat_scraper
import sys
import json
import re
import os


class UBCCrawler(QMainWindow):

    def __init__(self):
        super().__init__()
        self.debug = False
        self.path = ''
        self.initUI()

    def initUI(self):
        """Initiates main window UI."""

        self.setFixedSize(600, 300)
        self.centre()
        self.setWindowTitle('UBCCrawler')
        self.statusBar().showMessage('Ready')

        self.initTextBrowser()
        self.initDropDownMenus()
        self.show()

    def initTextBrowser(self):
        """Initiates TextBrowser for empty table."""

        self.textBrowser = QTextBrowser(self)
        self.textBrowser.resize(250, 220)
        self.textBrowser.move(40, 25)

    def centre(self):
        """Centres the window on the screen."""

        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                  (screen.height() - size.height()) / 2)

    def initDropDownMenus(self):
        """Initiates UI of drop down menus."""

        # Labels
        l_year_session = QLabel(' Year Session')
        l_subject = QLabel(' Subject')
        l_course_num = QLabel(' Course Number')
        l_section = QLabel(' Section')
        l_email = QLabel(' Enter your email to be notified')
        l_blank = QLabel('')
        l_blank.setMinimumHeight(27)

        # ComboBoxes
        self.year_session = QComboBox(self)
        self.year_session.setEditable(True)
        self.subject = QComboBox(self)
        self.subject.setEditable(True)
        self.course_num = QComboBox(self)
        self.course_num.setEditable(True)
        self.section = QComboBox(self)
        self.section.setEditable(True)
        # self.year_session.setMinimumHeight(27)
        # self.subject.setMinimumHeight(27)
        # self.section.setMinimumHeight(27)
        # self.course_num.setMinimumHeight(27)


        # Email QLineEdit
        self.email = QLineEdit(self)
        self.email.setMinimumHeight(22)
        self.email.returnPressed.connect(self.submit)

        # General Seats Only QCheckbox
        self.general_seats_only = QCheckBox('General Seats Only', self)
        self.general_seats_only.resize(self.general_seats_only.sizeHint())


        # TODO
        if self.debug:
            self.year_session.setCurrentText('2019W')
            self.subject.setCurrentText('CPSC')
            self.course_num.setCurrentText('310')
            self.section.setCurrentText('L1E')
            self.email.setText('raymondyeh98@gmail.com')
        else:
            self.loadYearSession()

        self.year_session.currentIndexChanged.connect(self.loadSubject)
        self.year_session.currentIndexChanged.connect(self.deleteStartHere)
        self.subject.currentIndexChanged.connect(self.loadCourseNum)
        self.course_num.currentIndexChanged.connect(self.loadSection)

        # Submit Button
        submit_button = QPushButton('Submit', self)
        submit_button.resize(submit_button.sizeHint())
        submit_button.clicked.connect(self.submit)

        # Stop Button
        stop_button = QPushButton('Stop', self)
        stop_button.resize((submit_button.sizeHint()))
        stop_button.clicked.connect(self.stop)

        # Central widget to placed on QMainWindow
        self.drop_down = QWidget(self)
        self.drop_down.resize(self.textBrowser.size())
        self.drop_down.move(300, 25)

        # grid_layout imposed on drop_down widget and adding widgets
        self.grid_layout = QGridLayout(self.drop_down)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setHorizontalSpacing(20)
        self.grid_layout.addWidget(l_year_session, 0, 0, 1, 1)
        self.grid_layout.addWidget(self.year_session, 1, 0, 1, 1)
        self.grid_layout.addWidget(l_subject, 0, 1, 1, 1)
        self.grid_layout.addWidget(self.subject, 1, 1, 1, 1)
        self.grid_layout.addWidget(l_course_num, 2, 0, 1, 1)
        self.grid_layout.addWidget(self.course_num, 3, 0, 1, 1)
        self.grid_layout.addWidget(l_section, 2, 1, 1, 1)
        self.grid_layout.addWidget(self.section, 3, 1, 1, 1)
        self.grid_layout.addWidget(l_email, 4, 0, 1, 2)
        self.grid_layout.addWidget(self.email, 5, 0, 1, 2)
        self.grid_layout.addWidget(self.general_seats_only, 6, 0, 1, 2)
        self.grid_layout.addWidget(submit_button, 7, 0, 1, 1)
        self.grid_layout.addWidget(stop_button, 7, 1, 1, 1)

    def loadYearSession(self):
        """loads year sessions into Year Session combobox"""

        self.year_session.addItem('Start Here')

        self.path = os.getcwd()
        if 'ubccrawler' not in self.path:
            self.path += '/ubccrawler'

        for f in os.listdir(self.path + '/resources'):
            if f.endswith('.json'):
                self.year_session.addItem(f.split('.',)[0])

    def loadSubject(self):
        """loads subjects into Subject combobox"""

        self.subject.clear()
        self.subject.addItem('')
        with open(self.path + '/resources/' + self.year_session.currentText() + '.json') as f:
            data = json.load(f)
            for i in data:
                # Check if data[i] is empty
                if data.get(i) != {}:
                    self.subject.addItem(i)

        self.subject.showPopup()

    def loadCourseNum(self):
        self.course_num.clear()
        self.course_num.addItem('')

        if self.subject.currentText() == '':
            return

        with open(self.path + '/resources/' + self.year_session.currentText() + '.json') as f:
            data = json.load(f)
            self.course_num.addItems(data[self.subject.currentText()])
        self.course_num.showPopup()

    def loadSection(self):
        self.section.clear()
        self.section.addItem('')

        if self.subject.currentText() == '' or self.course_num.currentText() == '':
            return

        with open(self.path + '/resources/' + self.year_session.currentText()+'.json') as f:
            data = json.load(f)
            self.section.addItems(data[self.subject.currentText()][self.course_num.currentText()])

        self.section.showPopup()


    def deleteStartHere(self):

        if self.year_session.findText('Start Here') != -1:
            self.year_session.removeItem(0)

    def submit(self):
        """Submits input course section and sends request to UBC course website."""

        email = self.email.text()

        if self.section.currentText() == '':
            self.statusBar().showMessage("Please enter a course section")

        elif email == '':
            self.statusBar().showMessage("Please enter an email")

        elif '@' not in email or '.' not in email:
            self.statusBar().showMessage("Please enter a valid email")

        else:
            self.statusBar().showMessage('Requesting')
            self.spider = seat_scraper.SeatScraper(self)
            # Delay 1 ms so status bar can update
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.requestCrawl)
            self.timer.singleShot(1, self.requestCrawl)
            self.timer.start(60 * 1000)

    def requestCrawl(self):
        """Used to delay 1ms to allow statusbar to update and show 'Requesting...'
         and disable drop down menu, email form, and checkbox """

        self.year_session.setDisabled(True)
        self.subject.setDisabled(True)
        self.course_num.setDisabled(True)
        self.section.setDisabled(True)
        self.email.setDisabled(True)
        self.general_seats_only.setDisabled(True)
        self.statusBar().showMessage('Requesting...')

        t = QTimer(self)
        t.singleShot(1, self.startCrawl)

    def startCrawl(self):
        """ Starts crawling"""
        table = self.spider.crawl(re.sub(r'\D', '', self.year_session.currentText()),
                                  self.year_session.currentText()[4],
                                  self.subject.currentText(),
                                  self.course_num.currentText(),
                                  self.section.currentText(),
                                  self.email.text(),
                                  self.general_seats_only.isChecked())

        self.displayTable(table)

    def stop(self):
        """Stops crawling and re-enable drop down menu"""

        # Checks whether crawler has been started
        if hasattr(self, 'timer'):
            self.timer.stop()
            self.statusBar().showMessage('Ready')
            self.spider.reset()
            self.year_session.setDisabled(False)
            self.subject.setDisabled(False)
            self.course_num.setDisabled(False)
            self.section.setDisabled(False)
            self.email.setDisabled(False)
            self.general_seats_only.setDisabled(False)

    def displayTable(self, seats_table):
        """Displays seat table on self.textBrowser"""

        self.textBrowser.setText('')
        self.textBrowser.insertPlainText("\n")
        self.textBrowser.insertPlainText("\n")
        for key, value in seats_table.items():
            self.textBrowser.insertHtml('&nbsp;&nbsp;&nbsp;&nbsp;<b>' + key + '</b> &nbsp;' + value + "<br>")

    def closeEvent(self, event):

        # QMessageBox.question(self, <Title Bar>, <Message Text>, <Buttons that appear in the dialog>, <Default Button>)
        reply = QMessageBox.question(self, 'Message', "Are you sure you want to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


def run():
    app = QApplication(sys.argv)
    ubc_crawler = UBCCrawler()
    sys.exit(app.exec_())
