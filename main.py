from dotenv import load_dotenv

load_dotenv()

from banner_scraper import parse_banner, get_banner
from db import upload_data

def main():
    get_banner(2022, 1)
    '''data = parse_banner()
    print("Beginning Upload...")
    upload_data(data)'''

if __name__ == "__main__":
    main()