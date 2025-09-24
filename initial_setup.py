from dotenv import load_dotenv
import os
from pathlib import Path
import jsons


#Constants
environment_file_path = Path(".env")


#Functions
def get_api_key():
    if environment_file_path.exists():
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        print(api_key)
        return api_key
        #https://pypi.org/project/python-dotenv/
    else:
        try:
            api_key = input("Please enter your gemini API key: ")
            with open(".env", "w") as environment:
                environment.write(f"GEMINI_API_KEY = \"{api_key}\"")
                #return api_key
        except:
            raise FileNotFoundError("There was an error writing the API_Keys, please manually create the environment file")


#Loading files
try:
    with open("query_fiction.txt") as file:
        query_fiction = file.read()

    with open("query_non_fiction.txt") as file:
        query_non_fiction = file.read()
except FileNotFoundError:
    raise FileNotFoundError("ERROR: could not find one of query_fiction.txt or query_non_fiction.txt.")

def get_bookshelf():
    try:
        with open("bookshelf.json") as file:
            bookshelf = jsons.load(file.read()) #This is causing issues. jsons doc gives more info on deserialisation. Need to find a way to seperate each book class.
    except FileNotFoundError:
        print("Bookshelf file missing, creating empty bookshelf. Ignore if this is the first run.")
        bookshelf = []
        with open("bookshelf.json", 'w') as file:
            pass
    return bookshelf