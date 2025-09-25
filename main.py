#Imports required for gemini access
from google import genai
from google.genai import types

#Imports from project
import initial_setup
from core_classes import Book
from user_interaction import get_file_path

#Loading constants + module variables
query_fiction = initial_setup.query_fiction
query_non_fiction = initial_setup.query_non_fiction
shelf = initial_setup.shelf

#Function definitions
def get_book_summary(chapter_as_str: str, summary_query = None):
    pass

def get_chapter_summary(chapter_as_str: str, summary_query = query_fiction):
    """Queries Gemini API to get a summary of the chapter
    Arguments:
        summary_query (str): the query *for now summary of fiction or non fiction = default
        chapter_as_str (str): The chapter to get a summary of
    Returns:
        summary (str): The summary of the chapter
    """
    response = queryGemini(query=(summary_query+chapter_as_str))

def queryGemini(query: str):
  """Sends query to gemini and returns the response text
  """
  # The client gets the API key from the environment variable `GEMINI_API_KEY`.
  client = genai.Client()
  response = client.models.generate_content(
      model="gemini-2.5-flash",
      contents=query,
      config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=0) #Disables thinking
      )
  )
  print(response.text)
  return response.text

#RUN
def test():
    file_path = get_file_path()
    new_book = Book(file_path)
    shelf.store_book(new_book)
    get_chapter_summary(new_book.chapter_text(3))

test()