import json
from dotenv import load_dotenv

load_dotenv()

from banner_scraper import parse_banner, get_banner
from people_scraper import parse_people, get_people
from calendar_scraper import get_calendar
from db import upload_banner, upload_calendar, upload_people, delete_all_in_collection


def main():
    print("Deleting...")
    delete_all_in_collection("Banner")
    print("Getting...")
    text = get_banner(2022, 1)
    print("Parsing...")
    data = parse_banner(text)
    upload_banner(data, 2022, 1)
    for year in range(2019, 2022):
        for term in range(1, 4):
            print(f"{year}: Term {term}")
            print("Getting...")
            text = get_banner(year, term)
            print("Parsing...")
            data = parse_banner(text)
            upload_banner(data, year, term)


if __name__ == "__main__":
    main()
