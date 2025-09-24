#import ebooklib
#from ebooklib import epub
#from core_classes import Book
#from bs4 import BeautifulSoup
#from initial_setup import get_bookshelf
#Using for storing class object as a dict
#import jsons

import tkinter , tkinter.filedialog
#Constants


#Function definitions
# def store_book(new_book: Book):
#     bookshelf = get_bookshelf()
#     for book in bookshelf:
#         if new_book._title in book['_title']: #this should change. we need a unique identifier in the book class for each book.
#             print("Book already in library")
#             return
#     else:
#         bookshelf.append(new_book)
#         #Should we sort the bookshelf as we build it?
#         with open("bookshelf.json", 'w') as bookshelf_file:
#             bookshelf_file.write(jsons.dumps(bookshelf))
#         print("Book added to library")
#         return

# def epub_to_html(file_path: str):
#     """Function to convert an ebook to a list containing chapter content in html format
#     Arguments:
#         file_path (str): The path to the epub file
#     Returns:
#         chapters (list): w
#     """
#     book = epub.read_epub(file_path)
#     chapters = []
#     #chapters = book.get_items_of_type(ebooklib.ITEM_DOCUMENT)
#     for item in book.get_items():
#         if item.get_type() == ebooklib.ITEM_DOCUMENT:
#             chapters.append(item.get_content())
#     return chapters

# def html_to_str(chapters, chapter_title):
#     """Converts the html ebook format to pure text
#     Arguments:
#         chapters (list):
#     Returns:
#         book (list):  
#     """
    
#     book = []
#     for chapter in chapters:
#         soup = BeautifulSoup(chapter, 'html.parser')
#         title_tag = soup.head
#         chapter_title.append(title_tag['title'])
#         text = [soup.get_text()]
#         book.append(' '.join(text))
#     return book

def get_file_path():
    book_path = tkinter.filedialog.askopenfilename(title = "Please select an ebook file.")
    while book_path.endswith('.epub') is not True:
        book_path = tkinter.filedialog.askopenfilename(title = "Please select an ebook file.")
    return book_path

if __name__ == "__main__":
    pass