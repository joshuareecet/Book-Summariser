import ebooklib , ebooklib.epub
from ebooklib import epub

from bs4 import BeautifulSoup
import tkinter , tkinter.filedialog

#Using for storing class object as a dict
import jsons

"""
TODO (HIGH to LOW priority): 
1. Add exceptions for edge cases e.g:
    1. Book may not have any chapters at all? what do we do
    2. User does not have an epub, cannot escape the while loop

2. Add book class: gives easy access to key features of the book even after processing:
    2.1 Add more parsing for ebook!
        2.1.1 Chapter titles should be associated with each chapter
    2.2 Add class attributes:
        2.2.1 author
        2.2.2 title
        2.2.3 language
        2.2.4. num. chapters
        2.2.5. chapter titles (maybe?)
        2.2.4. **path?
    2.3 Store gemini calls for chapter summaries
    2.4 Integrate an SQL database for storage

3. Combine epub_to_html and html_to_str into one function / Make them class functions
    3.1 Add both str and html to the book class
    3.2 Then can call straight from object of book class for searching in gemini
    
4. Integrate with a book tracker
    4.1 Calibre - primary target
    4.2

5. Create GUI interface 
    
"""


class Book():
    def __init__(self, file_path: str):
        self._path: str = file_path
        
        #Getting the metadata using ebooklib
        epub_book: ebooklib.epub.EpubBook = epub.read_epub(file_path)
        author_metadata: str = epub_book.get_metadata('DC','author')
        title_metadata: str = epub_book.get_metadata('DC','title')
        language_metadata: str = epub_book.get_metadata('DC','language') #this can return the format e.g. XML maybe we can use this
        
        #Converting metadata into information for storage
        self._title = title_metadata[0][0] if title_metadata else "Unknown title"
        self._author: list = [str(a) for a in author_metadata] if author_metadata else "Unknown Author"
        self._language = language_metadata[0][0] if language_metadata else "Unknown Language"
        

    def author(self):
        return self._author
    def path(self):
        return self._path #may remove this or add some sort of redundancy if the host changes the file path
    def title(self):
        return self._title
    def language(self):
        return self._language
    
    def summary(self):
        pass #Should integrate epub_to_html into class first

def store_book(book: Book):
    with open("bookshelf.json", 'w') as bookshelf:
        bookshelf.write(jsons.dumps(book, indent=4, sort_keys=True))


def epub_to_html(file_path: str):
    """Function to convert an ebook to a list containing chapter content in html format
    Arguments:
        file_path (str): The path to the epub file
    Returns:
        chapters (list): w
    """
    book = epub.read_epub(file_path)
    chapters = []
    #chapters = book.get_items_of_type(ebooklib.ITEM_DOCUMENT)
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            chapters.append(item.get_content())
    return chapters

def html_to_str(chapters):
    """Converts the html ebook format to pure text
    Arguments:
        chapters (list):
    Returns:
        book (list):  
    """
    
    book = []
    for chapter in chapters:
        soup = BeautifulSoup(chapter, 'html.parser')
        text = [soup.get_text()]
        book.append(' '.join(text))
    return book

def get_file_path():
    book_path = tkinter.filedialog.askopenfilename(title = "Please select an ebook file.")
    while book_path.endswith('.epub') is not True:
        book_path = tkinter.filedialog.askopenfilename(title = "Please select an ebook file.")
    return book_path

if __name__ == "__main__":
    # file_path = get_file_path()
    # html_book = epub_to_html(file_path)
    # str_book = html_to_str(html_book)
    # print(str_book[18])
    file_path = get_file_path()
    fakeBook = Book(file_path)
    store_book(fakeBook)