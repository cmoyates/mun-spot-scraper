from globals import CALENDAR_LISTINGS
import requests
from bs4 import BeautifulSoup
import json

def get_calendar():

    course_list = []

    for key in CALENDAR_LISTINGS:
        for sectionNumber in CALENDAR_LISTINGS[key]:
            response = requests.get(f"https://www.mun.ca/regoff/calendar/sectionNo={sectionNumber}")
            with open('raw_calendar.html', 'w', encoding='utf-8') as f:
                json.dump(response.text, f, ensure_ascii=False, indent=4)
            soup = BeautifulSoup(response.text, features="html.parser")
            courses = soup.find_all("div", {"class": "course"})
            for course in courses:
                name = course.find("p", {"class", "courseTitle"}).text.strip()
                number = course.find("p", {"class", "courseNumber"}).text.strip()
                description = course.find("div", {"class": "courseDesc"}).find("p", {"class": "inlinePara"})
                description = " - No available description." if description == None else description.text.strip()
                course_data = {
                    "Name": name,
                    "Number": number,
                    "Description": f"{name} {description}",
                    "Subject": key
                }
                course_list.append(course_data)
    
    return course_list