#Imports required for gemini access
from google import genai
from google.genai import types
#For tcl/tk access
from tkinter import *
from tkinter import tkk

#Imports from project
from initial_setup import get_api_key



api_key = get_api_key()
def get_ebook():
  pass
  

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client(api_key = api_key)
"""
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Please explain how I'm using the gemini api",
    config = types.GenerateContentConfig(
      thinking_config=types.ThinkingConfig(thinking_budget=0) #Disables thinking
    )
)
print(response.text)
"""
