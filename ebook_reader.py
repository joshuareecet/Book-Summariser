import ebooklib
from bs4 import BeautifulSoup
import tkinter
import tkinter.filedialog
from ebooklib import epub

"""
TODO (HIGH to LOW priority): 
1. Add exceptions for edge cases e.g:
    1. Book may not have any chapters at all? what do we do
    2. User does not have an epub, cannot escape the while loop

2. Add book class: gives easy access to key features of the book even after processing:
    1. author
    2. title
    3. language
    4. num. chapters
    5. chapter titles (maybe?)
    4. **path?
    5. Store gemini calls for chapter summaries

3. Combine epub_to_html and html_to_str into one function
    1. Add both str and html to the book class
    2. Then can call straight from object of book class for searching in gemini
    3.
    
4. Integrate with a book tracker? maybe calibre

5. Create GUI interface 
    
"""


class Book():
    def __init__(self, file_path):
        self._path = file_path
        self.__epub = epub.read_epub(file_path) #Do we need this? 
        self._author = self._epub.get_metadata('DC','author')
        self._title = self._epub.get_metadata('DC','title')
        self._language = self._epub.get_metadata('DC','language')

    def author(self):
        return self._author
    def path(self):
        return self._path #may remove this or add some sort of redundancy if the host changes the file path
    def title(self):
        return self.title
    def language(self):
        return self._language
    
    def summary(self):
        pass #Should integrate epub_to_html into class first

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
    file_path = get_file_path()
    html_book = epub_to_html(file_path)
    str_book = html_to_str(html_book)
    print(str_book[18])