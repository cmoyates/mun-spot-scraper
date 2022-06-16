import requests
from bs4 import BeautifulSoup
import json

def get_people():
    response = requests.get("https://www.mun.ca/appinclude/bedrock/public/api/v1/ua/people.php?type=advanced&nopage=1")

    return response.json()["results"]

def parse_people():

    out = {}

    with open('raw_people.html') as f:
        data = json.loads(f.read())

        for prof in data["results"]:
            if out.get(prof["department"]) == None:
                out[prof["department"]] = "here"


