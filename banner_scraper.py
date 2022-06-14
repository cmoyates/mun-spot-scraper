import requests
from bs4 import BeautifulSoup
import json

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'https://selfservice.mun.ca',
    'Referer': 'https://selfservice.mun.ca/direct/hwswsltb.P_CourseSearch?p_term=202103&p_levl=01*04',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

def get_banner(year, term, campus="%", faculty="%", prof="%", crn="%"):

    data = {
        'p_term': f"{year}0{term}",
        'p_levl': "01*00",
        'campus': campus,
        'faculty': faculty,
        'prof': prof,
        'crn': crn
    }

    response = requests.post('https://selfservice.mun.ca/direct/hwswsltb.P_CourseResults', headers=headers, data=data)

    f = open("demofile3.html", "w")
    f.write(response.text)
    f.close()

    soup = BeautifulSoup(response.text, features="html.parser")
    return soup


def parse_banner():
    out = {}
    with open('raw.html') as f:
        text = f.read()
        soup = BeautifulSoup(text, features="html.parser")
        pre_tag = soup.find("pre")
        campuses_raw = pre_tag.text.split("Campus: ")
        campuses_raw.pop(0)
        for campus_raw in campuses_raw[:1]:
            campus = campus_raw.split("\n", 1)
            campus[0] = campus[0].strip()
            out[campus[0]] = parse_campus(campus[1])

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=4)

def parse_campus(campus_info):
    subjects_raw = campus_info.split("Subject: ")
    subjects_raw.pop(0)
    subjects = {}
    for subject_raw in subjects_raw[:1]:
        subject = subject_raw.split("\n", 1)
        subject[0] = subject[0].strip()
        subjects[subject[0]] = parse_subject(subject[1])

    return subjects

def parse_subject(subject_info):
    courses = {}
    subject_lines = subject_info.split("\n")
    for i in range(len(subject_lines)):
        if len(subject_lines[i]) > 0 and subject_lines[i][0] != " ":
            course_lines = [subject_lines[i]]
            j = i + 1
            while len(subject_lines[j]) > 0 and subject_lines[j][0] == " ":
                course_lines.append(subject_lines[j])
                j += 1
            courses[subject_lines[i][5:9]] = parse_course(course_lines)
            break

    return courses

def parse_course(course_info):
    offerings = {}
    for i in range(len(course_info)):
        if len(course_info[i]) > 38 and course_info[i][38] != " ":
            offering_lines = [course_info[i]]
            j = i + 1
            while j < len(course_info) and len(course_info[j]) > 38 and course_info[j][38] == " ":
                offering_lines.append(course_info[j])
                j += 1
            offerings[course_info[i][38:41]] = parse_offering(offering_lines)

    return offerings

def parse_offering(offering_info):
    
    room = offering_info[0][77:85].strip()
    room = room if room else "N/A"
    
    time = {
        "Sunday": [],
        "Monday": [],
        "Tuesday": [],
        "Wednesday": [],
        "Thursday": [],
        "Friday": [],
        "Saturday": []
    }
    notes = []
    for line in offering_info:
        if line[67:70].isdigit() and line[72:76].isdigit():
            parse_time(line[53:76], time)
        else:
            notes.append(line.strip())

    offering = {
        "Prof": offering_info[0][148:].strip(),
        "CRN": offering_info[0][42:47],
        "Room": room,
        "Type": offering_info[0][86:89],
        "Time": time,
        "Notes": notes
    }

    return offering

def parse_time(time_string, time_dict):
    if time_string[0] == "M": time_dict["Monday"].append(time_string[14:])
    if time_string[2] == "T": time_dict["Tuesday"].append(time_string[14:])
    if time_string[4] == "W": time_dict["Wednesday"].append(time_string[14:])
    if time_string[6] == "R": time_dict["Thursday"].append(time_string[14:])
    if time_string[8] == "F": time_dict["Friday"].append(time_string[14:])
    if time_string[10] == "S": time_dict["Saturday"].append(time_string[14:])
    if time_string[12] == "U": time_dict["Sunday"].append(time_string[14:])