import pymongo
from pymongo.mongo_client import MongoClient
import os

cluster = MongoClient(os.environ["MONGO_URI"])

db = cluster["MUNSpot"]
banner_collection = db["Banner"]
calendar_collection = db["Calendar"]
people_collection = db["People"]

def upload_banner(data):

    all_offerings = []

    for campus in data:
        for subject in data[campus]:
            for course in data[campus][subject]:
                for offering in data[campus][subject][course]:
                    offering_data = data[campus][subject][course][offering]

                    offering_data["Campus"] = campus
                    offering_data["Subject"] = subject
                    offering_data["Number"] = course
                    offering_data["Section"] = offering

                    all_offerings.append(offering_data)
    
    print("Starting Banner upload...")

    banner_collection.insert_many(all_offerings)

def upload_calendar(data):
    print("Starting Calendar upload...")
    calendar_collection.insert_many(data)

def upload_people(data):
    print("Starting People upload...")
    people_collection.insert_many(data)