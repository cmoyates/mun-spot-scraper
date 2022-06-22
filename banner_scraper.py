import requests
from bs4 import BeautifulSoup
import json
from db import people_collection

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

    f = open("raw_banner.html", "w")
    f.write(response.text)
    f.close()

    soup = BeautifulSoup(response.text, features="html.parser")
    return soup


def parse_banner():
    out = {}
    with open('raw_banner.html') as f:
        text = f.read()
        soup = BeautifulSoup(text, features="html.parser")
        pre_tag = soup.find("pre")
        campuses_raw = pre_tag.text.split("Campus: ")
        campuses_raw.pop(0)
        for campus_raw in campuses_raw:
            campus = campus_raw.split("\n", 1)
            campus[0] = campus[0].strip()
            out[campus[0]] = parse_campus(campus[1])

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=4)
    
    return out

def parse_campus(campus_info):
    subjects_raw = campus_info.split("Subject: ")
    subjects_raw.pop(0)
    subjects = {}

    for subject_raw in subjects_raw:
        subject = subject_raw.split("\n", 1)
        subject[0] = subject[0].strip()
        if subject[0] == "Biochemistry":
            subjects[subject[0]] = parse_subject(subject[1], subject[0])

    return subjects

def parse_subject(subject_info, subject_name):
    courses = {}
    subject_lines = subject_info.split("\n")
    for i in range(len(subject_lines))[0:]:
        if len(subject_lines[i]) > 0 and subject_lines[i][0] != " " and subject_lines[i][10:20] != "Laboratory":
            if subject_lines[i][5:9] != "4210":
                continue
            course_lines = [subject_lines[i]]
            j = i + 1
            while len(subject_lines[j]) > 0 and (subject_lines[j][0] == " " or subject_lines[j][10:20] == "Laboratory"):
                course_lines.append(subject_lines[j])
                j += 1
            courses[subject_lines[i][5:9]] = parse_course(course_lines, subject_name)

    return courses

def parse_course(course_info, subject_name):
    offerings = {}
    for i in range(len(course_info)):
        if len(course_info[i]) > 38 and course_info[i][38] != " " and course_info[i][42:47].isdigit():
            offering_lines = [course_info[i]]
            j = i + 1
            while j < len(course_info) and len(course_info[j]) > 38 and course_info[j][38] == " ":
                offering_lines.append(course_info[j])
                j += 1
            offerings[course_info[i][38:41]] = parse_offering(offering_lines, course_info[0][:5].strip(), subject_name)
        break
    return offerings

def parse_offering(offering_info, subject_code, subject_name):
    
    room = offering_info[0][77:85].strip()
    room = room if room else "N/A"
    
    time = {
        "sunday": [],
        "monday": [],
        "tuesday": [],
        "wednesday": [],
        "thursday": [],
        "friday": [],
        "saturday": []
    }
    notes = []
    associated_sections = []
    cross_listed = []
    reserved_for = {}

    for line in offering_info:
        is_note = True
        if line[67:70].isdigit() and line[72:76].isdigit():
            is_note = False
            parse_time(line[53:76], time)
        if line[92:95].isdigit() and line[91]==" " and line[95]==" ":
            is_note = False
            parse_associated_sections(line[92:103], associated_sections)
        if is_note:
            if line[42:55] == "CROSS LISTED:":
                cross_listed_line = line[55:].strip()
                cross_listed = [cross_listed_line[i:i+13] for i in range(0, len(cross_listed_line), 14)]
            elif line[57:63] in ["DEGREE", "MAJOR ", "MINOR "]:
                reserved_for[line[57:63].strip().lower()] = line[63:].strip().split()

    prof = offering_info[0][148:].strip()

    offering = {
        "prof": prof,
        "prof_full": get_prof_full_name(prof, subject_name),
        "crn": offering_info[0][42:47],
        "room": room,
        "type": offering_info[0][86:89],
        "times": time,
        "notes": notes,
        "subject_code": subject_code,
        "associated_sections": associated_sections,
        "cross_listed": cross_listed,
        "reserved_for": reserved_for
    }

    return offering

def parse_time(time_string, time_dict):
    if time_string[0] == "M": time_dict["monday"].append(time_string[14:])
    if time_string[2] == "T": time_dict["tuesday"].append(time_string[14:])
    if time_string[4] == "W": time_dict["wednesday"].append(time_string[14:])
    if time_string[6] == "R": time_dict["thursday"].append(time_string[14:])
    if time_string[8] == "F": time_dict["friday"].append(time_string[14:])
    if time_string[10] == "S": time_dict["saturday"].append(time_string[14:])
    if time_string[12] == "U": time_dict["sunday"].append(time_string[14:])

def get_prof_full_name(prof, faculty):
    prof_name_parts = prof.split(" ", 1)
    if (len(prof_name_parts) < 2):
        return prof

    test = people_collection.aggregate([{
                    "$search": {
                        "index": 'People Search',
                        "compound": {
                            "should": [
                                {
                                    "text": {
                                        "query": prof_name_parts[0],
                                        "path": "fname",
                                    }
                                },
                                {
                                    "text": {
                                        "query": prof_name_parts[1],
                                        "path": "lname",
                                        "score": {
                                            "boost": {
                                                "value": 5
                                            }
                                        }
                                    }
                                },
                                {
                                    "text": {
                                        "query": faculty,
                                        "path": "department",
                                        "score": {
                                            "boost": {
                                                "value": 5
                                            }
                                        }
                                    }
                                }
                            ]
                        }
                    }
                }, {
                    "$limit": 1
                }
            ])
    
    test = list(test)
    if len(test) < 1:
        return prof
    first_name = test[0]["fname"]
    last_name = test[0]["lname"]
    if first_name[0] == prof_name_parts[0][0] and last_name in prof_name_parts[1]:
        
        return f"{first_name} {last_name}"
    else:
        return prof
    
def parse_associated_sections(associated_sections_string, associated_sections_list):
    associated_sections_list += associated_sections_string.strip().split(" ")

def parse_notes(notes_string, notes_list):
    print(notes_string)