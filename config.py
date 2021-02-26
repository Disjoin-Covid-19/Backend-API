from pymongo import MongoClient

mongo_client = MongoClient(
    "mongodb+srv://DisJoin:1234@cluster0-bk4u2.mongodb.net/test?retryWrites=true&w=majority"
)
db = mongo_client["DisJoin_data"]
DEBUG = True
