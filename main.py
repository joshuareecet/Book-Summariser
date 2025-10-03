#Imports required for gemini access
from google import genai
from google.genai import types
from time import sleep #to limit the no. of requests per minute on free api
from llama_cpp import Llama

#Imports from project
import initial_setup
from core import Book, Bookshelf
from user_interaction import get_file_path, get_int

#Importing constants + module variables
from initial_setup import (combine_summary, part_summary, 
                           query_fiction, query_non_fiction, combine_chunk_fiction,
                           combine_chunk_non_fiction, chunk_fiction, chunk_non_fiction,
                           local_model, shelf, use_local_model, context_window_limit, gpu_layers) # (lol)

print(r"""
  ___           _     ___                           _             
 | _ ) ___  ___| |__ / __|_  _ _ __  _ __  __ _ _ _(_)___ ___ _ _ 
 | _ \/ _ \/ _ \ / / \__ \ || | '  \| '  \/ _` | '_| (_-</ -_) '_|
 |___/\___/\___/_\_\ |___/\_,_|_|_|_|_|_|_\__,_|_| |_/__/\___|_|  
""")

#Setting constants
gemini_token_limit = 250000 #for gemini 2.5 flash. maybe can add option to use pro?
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
    query = summary_query + chapter_as_str
    
    if use_local_model == False:
        
        response = queryGemini(query)
        return response
    
    elif use_local_model == True and local_model != None:
        
        #loading model
        llm = Llama(
        model_path = local_model._raw_path,
        n_gpu_layers = gpu_layers, 
        # seed=1337, # Uncomment to set a specific seed
        n_ctx = int(context_window_limit / 30) # .env file this
        )

        #generating response
        response = llm(
            query, # Prompt
            max_tokens = None, # Generate up to 32 tokens, set to None to generate up to the end of the context window
            stop = None, 
            echo = False #
        ) # Generate a completion, can also call create_completion
        return response
    else:
        print("Something went wrong loading the local model.")

def get_book_summary(book: Book, chunk_type: str, combiner_type: str):
    
    print("Please wait, this may take a long time....")
    joined_chapters = join_chapters(book) 
    parts = []
    
    #Getting summaries for each individual chunk and joining them
    query_wait_time = 15     #we can do 5 queries per minute on free gemini api, so around once every 12 seconds should stop us being rate limited.

    for query in joined_chapters:
        appender = get_summary(query,chunk_type)
        parts.append(appender)
        sleep(query_wait_time)
    final_summary = "".join(parts)
    
    response = get_summary(final_summary, combiner_type)
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
    while current_chapter  < target_book.length-1:
        if current_length > summary_limit:
            current_index += 1
            joined_chapters.append("")
        joined_chapters[current_index] += "".join(target_book.chapter_text(current_chapter))
        current_length = len(joined_chapters[current_index]) + len(target_book.chapter_text(current_chapter))
        current_chapter += 1
    return joined_chapters

def join_long_chapter(target_book: Book, current_chapter):
    """ 
    WORK IN PROGRESS
    Arguments:
        current_chapter (int): The target chapter to split
    Returns:
        split_chapter (list[str]): A list containing a split version of each chapter within the context window limit
    
    """
    
    text = target_book.chapter_text(current_chapter)
    split_chapter = []
    index = 0
    length = 0
    for chars in text:
        if length < summary_limit:
            split_chapter[index] = ''.join(chars)
        else:
            index += 1
            length = 0
    return split_chapter


def queryGemini(query: str):
    """Sends query to gemini and returns the response text
    """
    client = genai.Client()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=query,
        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0) #Disables thinking
        )
    )
    return response.text


#Logic for running script
def start():
    select_mode()

def select_mode():
    prompt = (
        "Please select a mode using numbers 1-2: \n" \
        "1: Upload Book (Summary Generation)\n" \
        "2: Select from Library (Summary Generation)\n"
        #"3: Open Library\n"
            )
    mode = get_int(prompt,0,3)
    
    if mode == 1:
        file_path = get_file_path()
        shelf.add_book(file_path)
    elif mode == 2:
        select_book()
    elif mode == 3:
        browse_library()
    
    select_book()

def browse_library():
    shelf.list_books()
    prompt = """
    Would you like to:\n
    1. Rate a book
    2. View book information
    3. Sort books by Author / Rating / Publish date 
    """

def select_book():
    shelf.list_books()
    print("")
    prompt_2 = "Please enter the corresponding number book you would like to summarise: "
    number = get_int(prompt_2) - 1
    print("")
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

    book_type = get_int(prompt,0,3)
    #THIS NEEDS TO BE MORE DESCRIPTIVE
    if book_type == 1: 
        if book_or_chap == 1:       #1 is whole book
            type = chunk_non_fiction
            combiner_type = combine_chunk_non_fiction
        else:                       #2 is chapter
            type = query_non_fiction
    else:
        if book_or_chap == 1:       #1 is whole book
            type = chunk_fiction
            combiner_type = combine_chunk_fiction          
        else:                       #2 is chapter
            type = query_fiction

    prompt = (
        "Would you like to add custom flags to the prompt?\n" \
        "1. Yes\n" \
        "2. No \n"
    )

    flags = get_int(prompt, min=0, max=3)
    if flags == 1: #yes custom flags
        flags = input("Please enter the flags to append to the prompt: \n")
        type += "".join(f"User custom flags to use are: {flags}. \n The book text is as follows: \n")
    if flags == 2: #no custom flags
        type += "".join(f"No user custom flags, the text is as follows: \n")
    
    #Generating summary
    if book_or_chap == 1:
        response = get_book_summary(target_book, type, combiner_type)
        print(response)
    else:
        prompt = "Please enter the chapter number you would like to be summarised: "
        for chapter_title in target_book.chapter_titles():
            print(chapter_title)
        target_chapter = get_int(prompt)
        text = target_book.chapter_text(target_chapter)
    
        response = get_summary(text, type)
        print(response)
    
    stop_or_restart()
    
def stop_or_restart():
    print("")
    input("Press enter to restart...")
    start()

start()