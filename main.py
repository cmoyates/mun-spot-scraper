from dotenv import load_dotenv

load_dotenv()

from banner_scraper import parse_banner
from db import upload_banner

def main():
    banner_data = parse_banner()
    upload_banner(banner_data)


if __name__ == "__main__":
    main()