import requests as requests
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import date
import json
from dataclasses import dataclass, field

# The only global variable will be the holidayObjects list. This is the list of objects. This is being used as a global
# because this allows me to use it more easily in the user interface of this code - being able to grab it from main
# instead of using it as a parameter in every function.
global holidayObjects
holidayObjects = []


def deletingHoliday(decorated_func):
    def inner_fn(*args, **kwargs):
        print('Deleted %s from the list of holidays' % str(args[0]))
        evaluated = decorated_func(*args, **kwargs)
        return evaluated

    return inner_fn


@dataclass
class Holiday:
    """Creating Holiday Object"""
    name: str
    date: datetime

    def __str__(self):
        return self.__name + ' (' + self.__date + ')'


# This function takes the list of dictionaries from the JSON and the website and creates holiday objects.
# any holidays added through the user interface will be automatically be created as an object and appended to the list
# of objects.
def listToObject(listHolidays):
    global holidayObjects
    # This iterates through every dictionary in the list, taking the name and the date and creating a holiday object.
    # This newly created object is appended to holidayObjects, a global list that can be grabbed by and changed by any
    # function.
    for i in range(len(listHolidays)):
        holidayObjects.append(Holiday(str(listHolidays[i]['name']), (listHolidays[i]['date'])))


def getJSON():
    with open('holiday.json') as holiday:
        holidayJSON = json.load(holiday)
    return holidayJSON


def JSONtoDict(holidayJSON, holiday):
    listJSON = []
    listJSON = holidayJSON['holidays']
    # print(listJSON)
    for i in holiday:
        listJSON.append(i)
    return listJSON


def getHTML(url):
    response = requests.get(url)
    return response.text


# This function performs the web scraping of the holidays data.
def webScrape():
    holiday = []
    # The for loop is run to grab the years 2020-2024 from the website's holiday tables.
    # 2021 has a different URL from the rest, so there is an exception that catches this discrepancy.
    for i in range(2020, 2025):
        if i == 2021:
            response = requests.get('https://www.timeanddate.com/holidays/us/')
            html = getHTML('https://www.timeanddate.com/holidays/us/')
        else:
            response = requests.get('https://www.timeanddate.com/holidays/us/' + str(i))
            html = getHTML('https://www.timeanddate.com/holidays/us/' + str(i))
        holidayParse = BeautifulSoup(html, 'html.parser')
        table1 = holidayParse.find('tbody')
        listName = []

        # This for loop runs through the table itself, finding every name and date for each holiday we want to create
        # at this beginning point, a list of dictionaries is created which will used to create holiday objects.
        for row in table1.find_all_next('tr'):
            nameHoliday = row.find_next('a').string
            if nameHoliday != 'let us know' and nameHoliday not in listName:
                holidays = {}
                holidays['name'] = row.find_next('a').string
                if row.find_next('th') is not None:
                    holidays['date'] = str(
                        datetime.strptime(row.find_next('th').string + ' ' + str(i), '%b %d %Y').date())
                listName.append(nameHoliday)
                holiday.append(holidays)
        # print(holiday)
        # print(holidayDict)
    return holiday
    # print(listName)


def toJSON(holiday):
    # acted as the starting base of exporting, prior to creating the user interface or any intractability in the code
    holidayDict = {}
    holidayDict['holidays'] = holiday
    print('Exporting Holiday List to JSON')
    listJSON = json.dumps(holidayDict, indent=4)
    with open('holidays.json', "w") as outfile:
        outfile.write(listJSON)


def saveToJSON():
    # Creates a list to append the list of objects to and create the desired format for the JSON.
    # The dictionary acts as a formatting tool, as the desired format for the JSON is a dictionary of a list of
    # dictionaries.
    holidayList = []
    JSONformat = {}
    for i in holidayObjects:
        holidayDict = {'name': i.name, 'date': str(i.date)}
        holidayList.append(holidayDict)
    JSONformat['holidays'] = holidayList
    listJSON = json.dumps(JSONformat, indent=4)
    with open('holidays.json', 'w') as outfile:
        outfile.write(listJSON)


def saveHoliday():
    save = str(input('Would you like to save the holiday list? Type y or n : '))
    if save == 'y':
        saveToJSON()
    else:
        goBack = str(input('Would you like to go back to the home menu? Type y or n : '))
        if goBack == 'y':
            userInterface()
        else:
            saveHoliday()

def addHoliday():
    # The user is prompted whether they would like to add a holiday to the system.
    add = str(input('Would you like to add a holiday to the system? Type y or n : '))
    if add == 'y':
        # If the user wants to add a holiday, then we prompt them to type in the name of the holiday, the year, month
        # and day of the holiday. I decided to separate out year month day to avoid a user having to use a specific
        # format for their date.
        nameHoliday = str(input('What is the name of the holiday? Type here: '))
        dateYear = str(input('What year is the holiday in? Type here: '))
        dateMonth = str(input('What is the month number of the holiday? Type here:  '))
        dateDay = str(input('What is the day of the holiday? Type here: '))
        # With the data given by the user, a new holiday object is created, for the date, the correct format is made.
        holidayObjects.append(Holiday((nameHoliday), (dateYear + '-' + dateMonth + '-' + dateDay)))
        # The user is prompted if they would like to go back to the home menu or make another holiday.
        # depending on the answer, the user will be brought back into the addHoliday() function, or taken back to
        # userInterface().
        goBack = str(input('Would you like to go back to the home menu? Typing \'n\' will allow you to add another '
                           'holiday. Type y or n : '))
        if goBack == 'y':
            userInterface()
        else:
            addHoliday()
    else:
        goBack = str(input('Would you like to go back to the home menu? Type y or n : '))
        if goBack == 'y':
            userInterface()


def delHolidayQuestion():
    objectRemoved = str(input('What holiday would you like to remove? Type here:')).lower()
    delHoliday(objectRemoved)

# Uses a decorator to display what is being removed from the list of holidays.
@deletingHoliday
def delHoliday(objectRemoved):
    found = False
    for i in range(len(holidayObjects)):
        if holidayObjects[i].name.lower() == objectRemoved:
            found = True
            instance = i
    if found:
        holidayObjects.pop(instance)
    if not found:
        print('======================')
        print('Holiday does not exist')
        print('======================')
        tryAgain = str(input('Would you like to enter another? Type y or n : '))
        if tryAgain == 'y':
            delHolidayQuestion()
        else:
            userInterface()
    goBack = str(input('Would you like to go back to the home menu? Type y or n : '))
    if goBack == 'y':
        userInterface()
    else:
        delHolidayQuestion()


def viewHoliday():
    # First thing the function does is ask the user for a year and week to filter by in the data.
    selectYear = str(input('Which year would you like to filter by? Leave blank to fetch current year. Type here : '))
    selectWeek = str(input('Which week would you like to filter by? Leave blank to fetch current week. Type week '
                           '# 1-52 : '))
    # This if statement catches if the person left the year option blank, if they did so, it will filter holidays by
    # the current year, it will set selectYear as the current year and run the filter w/ the selected week.
    if selectYear == '':
        today = date.today()
        selectYear = today.year
    # This if statement catches if the person left the week option blank, if they did so, it will filter holidays by the
    # current week, it will set selectWeek as the current week and run the filter.
    if selectWeek == '':
        today = date.today()
        selectWeek = today.isocalendar().week
    # These lambda functions filter the list of objects by the year and week they occur in.
    # it converts the date of a holiday to its year # and makes sure it matches the selected year by the
    # user. It then converts the filter to a list, and runs a second filter lambda function to grab the week number
    # and filter the data by its week number.
    filteredYear = filter(lambda x: datetime.strptime(x.date, '%Y-%m-%d').year == int(selectYear), holidayObjects)
    filteredYear = list(filteredYear)
    filteredWeek = filter(lambda x: datetime.strptime(x.date, '%Y-%m-%d').isocalendar().week == int(selectWeek), filteredYear)
    filteredWeek = list(filteredWeek)
    # With the filteredWeek list, it is printed out in a desired format to display the holidays of the selected
    # year and week by the user.
    print('==================================')
    print('Holidays for week %s of the year: ' % str(selectWeek))
    print('==================================')
    for i in range(len(filteredWeek)):
        print(filteredWeek[i].name + ', ' + filteredWeek[i].date)
    goBack = str(input('Would you like to go back to the home menu? Type y or n : '))
    if goBack == 'y':
        userInterface()
    else:
        viewHoliday()


def userInterface():
    print('''
    ==================
    Holiday Management
    ==================
    ''')
    print('''
    ==========================
    What would you like to do?
    ==========================
    1. Add a Holiday
    2. Remove a Holiday
    3. Save Holiday List
    4. View Holidays
    5. Exit
    ''')

    userChoice = input(str('Please input the number of the option you select here: '))
    if userChoice == '1':
        # Adds a holiday to the list of objects created.
        addHoliday()
    elif userChoice == '2':
        delHolidayQuestion()
    elif userChoice == '3':
        saveHoliday()
    elif userChoice == '4':
        viewHoliday()
    elif userChoice == '5':
        print('''
        ==========================
            Have a great day!
        ==========================''')
        exit()


if __name__ == '__main__':
    # The first few functions bring back lists from the webpage, and the JSON file. These are then combined to create a
    # list of dictionaries, and a list of objects of the existing holidays prior to adding or removing any others.
    # This is the starting point, and must be performed prior to entering into the user interface.
    holiday = webScrape()
    holidayJSON = getJSON()
    combined = JSONtoDict(holidayJSON, holiday)
    listToObject(combined)
    userInterface()
