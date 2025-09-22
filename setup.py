from dotenv import load_dotenv
import os

def setup():
    try:
        load_dotenv()
        api_key = os.getenv("API_KEY")
        print(api_key)
        return api_key
        #https://pypi.org/project/python-dotenv/
    except FileNotFoundError:
        with open(".env", "w") as environment:
            #Get input for API key
            pass
