from dotenv import load_dotenv
import os
from pathlib import Path
environment_file_path = Path(".env")


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


#Getting queries
with open("query_fiction.txt") as file:
  query_fiction = file.read()

with open("query_non_fiction.txt") as file:
  query_non_fiction = file.read()