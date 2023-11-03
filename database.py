import pymongo
import os

from dotenv import load_dotenv

load_dotenv()

# Initialize the MongoDB client
client = pymongo.MongoClient(os.getenv("CONNECTION_STRING"))

# Select the database for your bot
db = client["functions_db"]

ideas_collection = db["ideas"]


# Store an idea in the collection
def store_idea(ai_question: str):
    idea = {
        "function_idea": ai_question,
    }

    ideas_collection.insert_one(idea)


def get_ideas():
    return ideas_collection.find()
