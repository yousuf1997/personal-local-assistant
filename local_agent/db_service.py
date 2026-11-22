from pymongo import MongoClient
import os


class DBService:

    def __init__(self):
        self.__uri = f"mongodb+srv://{os.getenv("MONGO_DB_USER")}:{os.getenv("MONGO_DB_PASS")}@local-agent.1elpt96.mongodb.net/"
        print("Welcome to the application here its the application " + self.__uri)
        self.__client = MongoClient(self.__uri)
        self.__ping()

    def __ping(self):
        try:
            self.__client.admin.command("ping")
            print("Connected successfully")
            self.__client.close()
        except Exception as e:
            raise Exception("The following error occurred: ", e)
