from dotenv import load_dotenv
import os
from pathlib import Path
import json
from core_classes import Bookshelf

#Constants
environment_file_path = Path(".env")
shelf = Bookshelf()


#Getting API key and setting as environment variable
if environment_file_path.exists():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
else:
    try:
        api_key = input("Please enter your gemini API key: ")
        with open(".env", "w") as environment:
            environment.write(f"GEMINI_API_KEY = \"{api_key}\"")
    except:
        raise FileNotFoundError("There was an error writing the API_Keys, please manually create the environment file")


#Loading prompts
try:
    with open("query_fiction.txt") as file:
        query_fiction = file.read()

    with open("query_non_fiction.txt") as file:
        query_non_fiction = file.read()
except FileNotFoundError:
    raise FileNotFoundError("ERROR: could not find one of query_fiction.txt or query_non_fiction.txt.")