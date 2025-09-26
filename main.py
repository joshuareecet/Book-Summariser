#Imports required for gemini access
from google import genai
from google.genai import types
from time import sleep #to limit the no. of requests per minute on free api

#Imports from project
import initial_setup
from core_classes import Book
from user_interaction import get_file_path, get_int

#Loading constants + module variables

combine_summary = initial_setup.combine_summary
part_summary = initial_setup.part_summary
query_fiction = initial_setup.query_fiction
query_non_fiction = initial_setup.query_non_fiction

shelf = initial_setup.shelf
gemini_token_limit = 250000 
chars_per_token = 3
summary_limit = gemini_token_limit - (len(part_summary)/chars_per_token)


    
#Function definitions
def get_summary(chapter_as_str: str, summary_query = query_fiction):
    """Queries Gemini API to get a summary of the chapter
    Arguments:
        summary_query (str): the query *for now summary of fiction or non fiction = default
        chapter_as_str (str): The chapter to get a summary of
    Returns:
        summary (str): The summary of the chapter
    """
    response = queryGemini(query=(summary_query+chapter_as_str))
    return response

def get_book_summary(book: Book, summary_query = None):
    print("Please wait, this may take a long time....")
    joined_chapters = join_chapters(book)
    parts = []
    for query in joined_chapters:
        appender = get_summary(query,part_summary)
        parts.append(appender)
        delay = 15 #we can do 5 queries per minute on free gemini api, so once every 12 seconds. unfortunately this just doesnt work so limiting to once per minute.
        sleep(delay)
    final_summary = "".join(parts)
    response = get_summary(final_summary, combine_summary)
    return response

def join_chapters(target_book: Book):
    """
    Arguments:
        target_book (Book)
        limit_type (int): either fiction_limit or non_fiction_limit
    
    Returns:
        joined_chapters (list): a list with each index containing as many tokens as fit in the context window
    """

    joined_chapters = [""] #each index contains as many chapters as can fit in the token limit
    current_chapter = 0
    current_index = 0
    current_length = len(joined_chapters)+len(target_book.chapter_text(current_chapter))
    while current_chapter  < target_book.length()-1:
        if current_length > summary_limit:
            current_index += 1
            joined_chapters.append("")
        joined_chapters[current_index] += "".join(target_book.chapter_text(current_chapter))
        current_length = len(joined_chapters[current_index]) + len(target_book.chapter_text(current_chapter))
        current_chapter += 1
    return joined_chapters

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
    return response.text

def select_mode():
    prompt = (
        "Please select a mode using numbers 1-2: \n" \
        "1: Upload Book\n" \
        "2: Select from Library\n"
            )
    mode = get_int(prompt,0,3)
    if mode == 1:
        file_path = get_file_path()
        shelf.add_book(file_path)
    
    #move to next
    select_book()

def select_book():
    shelf.list_books()
    prompt_2 = "Please enter the corresponding number book you would like to summarise: "
    number = get_int(prompt_2) - 1
    target_book = shelf.get_book(number)
    
    #move to next -> carry target_book
    book_or_chapter(target_book)

def book_or_chapter(target_book: Book):
    prompt = (
    "Would you like to summarise either: \n" \
    "1. Whole book\n" \
    "2. A Chapter\n"
    )
    book_or_chap = get_int(prompt, 0,3)
    #move to next -> carry target_book
    select_book_type(target_book, book_or_chap)


def select_book_type(target_book: Book, book_or_chap: int):
    prompt = (
        "Please select the type of book: \n" \
        "1. Non fiction\n" \
        "2. Fiction\n"
    )
    type = get_int(prompt,0,3)
    if type == 1:
        type = query_non_fiction
    else:
        type = query_fiction




    if book_or_chap == 1:
        response = get_book_summary(target_book)
        print(response)
    else:
        prompt = "Please enter the chapter number you would like to be summarised: "
        for chapter_title in target_book.chapter_titles():
            print(chapter_title)
        target_chapter = get_int(prompt)
        text = target_book.chapter_text(target_chapter)
    
        response = get_summary(text, type)
        print(response)



#RUN
def test2():
    

    prompt_2 = "Please enter the corresponding number book you would like to summarise: "
    prompt_3 = "Please enter the chapter number you would like to be summarised: "
    prompt_4 = ("Please select the type of book: \n" \
                "1. Non fiction\n" \
                "2. Fiction\n")



    shelf.list_books()
    number = get_int(prompt_2) - 1
    target_book = shelf.get_book(number)

    for chapter_title in target_book.chapter_titles():
        print(chapter_title)

    target_chapter = get_int(prompt_3)
    text = target_book.chapter_text(target_chapter)
    type = get_int(prompt_4,0,3)
    if type == 1:
        type = query_non_fiction
    else:
        type = query_fiction
    response = get_summary(text, type)
    print(response)

def test():
    select_mode()

test()