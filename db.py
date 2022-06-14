from urllib.parse import urlparse
import psycopg2
import os
import json
import traceback


connection = None
cursor = None

# https://stackoverflow.com/questions/15634092/connect-to-an-uri-in-postgres
result = urlparse(os.environ["DATABASE_URL"])
username = result.username
password = result.password
database = result.path[1:]
hostname = result.hostname
port = result.port

def upload_data(data):
    try:
        connection = psycopg2.connect(
            database = database,
            user = username,
            password = password,
            host = hostname,
            port = port
        )

        cursor = connection.cursor()


        insert_script = "INSERT INTO course (number, prof, crn, room, type, campus, times, notes, section, subject) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        for campus in data:
            for subject in data[campus]:
                for course in data[campus][subject]:
                    for offering in data[campus][subject][course]:
                        offering_data = data[campus][subject][course][offering]

                        offering_set = (
                            course, 
                            offering_data["Prof"], 
                            offering_data["CRN"],
                            offering_data["Room"],
                            offering_data["Type"],
                            campus,
                            json.dumps(offering_data["Time"]),
                            offering_data["Notes"],
                            offering,
                            subject
                        )

                        cursor.execute(insert_script, offering_set)

        connection.commit()
        
    except Exception as error:
        print(traceback.format_exc())
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()