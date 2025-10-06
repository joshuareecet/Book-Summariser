#For fuzzy matching during search
from rapidfuzz import fuzz

#For SQL database storage
import sqlite3, shutil, os, ebooklib
from pathlib import Path
from user_interaction import get_int

#For parsing books
from bs4 import BeautifulSoup
from ebooklib import epub



"""
Currently non-functional.
"""
#Required for classes
ebook_directory_str = 'ebooks'
abs_root_path = Path.cwd()

class Book():  
    def __init__(self, id: list = None, file_path: str = None,  title: str = None,
                  author: list = None, lang: str = None, length: int = None):
        self._path: str = file_path if isinstance(file_path, Path) else Path(file_path)
        self._file = None
        self._chapters_title = []
        self._chapters_text = []
        
        if id:
            self._id = id
            self._title: str = title if title else "Unknown title"
            self._author: str = author if author else "Unknown Author"
            self._language: str = lang if lang else "Unknown Language"
            self._length = length if length else 0
        else:
            self.read_book()

            author_metadata: str = self._file.get_metadata('DC','author')
            title_metadata: str = self._file.get_metadata('DC','title')
            language_metadata: str = self._file.get_metadata('DC','language') #this can return the format e.g. XML maybe we can use this
            id_metadata = self._file.get_metadata('DC','identifier')

            #Converting metadata into information for storage
            self._title = title_metadata[0][0] if title_metadata else "Unknown title"
            self._author: list = [str(a) for a in author_metadata] if author_metadata else "Unknown Author"
            self._language = language_metadata[0][0] if language_metadata else "Unknown Language"
            #ID comes as a list but we really just want uuid
            self._id = str(id_metadata[0][0]) if id_metadata else "Unknown ID"
            self._length = length if length else 0 # I'm not sure if we should even keep the length value


    def _set_path(self, path):
        self._path = path

    @property
    def id(self):
        return (self._id.copy() if isinstance(id,list) else self._id)
    
    @id.setter
    def id(self, value):
        print("Are you sure you want to modify the id?")
        self._id = value
    
    @property
    def author(self):
        return self._author.copy() if isinstance(self._author, list) else self._author
    
    @author.setter
    def author(self, value):
        if isinstance(value, str):
            self._author = value
        elif isinstance(value, list):
            self._author = value
        else:
            raise ValueError("ValueError: author can only be str or list!")        
    
    @property
    def title(self):
        return self._title
   
    @title.setter
    def title(self, value):
        if isinstance(value, str):
            self._title = value
        else:
            raise ValueError("Title can only be set as a string.")
    
    @property
    def lang(self):
        return self._language
    @lang.setter
    def lang(self, value):
        if isinstance(value, str):
            self._lang = value
        else:
            raise ValueError("Language can only be set as a string!")
    
    @property
    def length(self):
        if self._length == 0:
            self.get_content()
        return self._length
    @length.setter
    def length(self, value):
        print("This should be internal logic only. Length is unchanged.")

    def chapter_titles(self):
        """
        Returns:
            self._chapters_title (list): A list containing the chapter titles
        """
        if self._chapters_title == []:
            self.get_content()
        return list(self._chapters_title)

    def chapter_text(self, chapter_number):
        """
        Arguments:
            chapter_number (int): The number of the chapter to be accessed
        Returns:
            self._chapters_text[chapter_number] (str): The text in the accessed chapter
        """
        if self._chapters_text == []:
            self.get_content()
        return self._chapters_text[chapter_number]
    
    def read_book(self):
        """
        Please call self.read() whenever you are accessing book metadata
        """
        if self._file == None:
            try:
                self._file: ebooklib.epub.EpubBook = epub.read_epub(self._path)
            except FileNotFoundError:
                raise FileNotFoundError(f"File not found, please remove {self._title} from bookshelf.")
    
    def to_dict(self):
        """A (deprecated?) function to translate the core attributes of the class to a dictionary
        """
        attributes = {
            "path" : str(self._path),
            "length" : self._length,
            "title" : self._title,
            "author" : self._author,
            "language": self._language,
            "id" : self._id
        }
        return attributes
    
    def to_list(self): 
        """A function to translate the core attributes of the class to a list for SQL storage
        """        
        
        attributes = [
            self._id,      
            str(self._path),
            self._title,          
            self._author if isinstance(self._author, str) else self._author.copy(),
            self._language,       
            self._length
        ]
        return attributes
    
    def get_content(self):
        """
        Function converts an epub to string format for processing
        
        Side effects:
            self._chapters_html (list) -> a list with the html version of each chapter at each index
            self._chapters_text (list) -> The raw text version of self._chapters_html
            self._chapters_title (list) -> A list containing the titles of each chapter
            self._length (int) -> The total num. of chapters
        """
        self.read_book()

        #First convert epub to html format
        self._chapters_html = []
        backup_titles = []

        for item in self._file.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                content = item.get_content()
                
                min_character_count = 2000
                #We can ignore any chapters that have less than 2000 characters in them.
                #I just made up 2000 maybe there is a proper number somewhere we can use. i doubt it though
                
                if len(content) > min_character_count:
                    self._chapters_html.append(content)
                    backup_titles.append(item.file_name)

        chapter_number = 0
        for chapter, backup_title in zip(self._chapters_html, backup_titles):
            soup = BeautifulSoup(chapter, 'lxml-xml')
            
            #Extracting the title tag 
            title_tags = [soup.title, soup.head, soup.h1, soup.h2]
            secondary_tags = ['title', 'head', 'h1', 'h2']

            for tag, tag2 in zip(title_tags, secondary_tags):
                if tag and tag.attrs and "title" in tag.attrs:
                    self._chapters_title.append(f"{str(chapter_number)}: {tag['title']}")
                    break
                elif soup.find(tag2) and soup.find(tag2).string:
                    self._chapters_title.append(f"{str(chapter_number)}: {soup.find(tag2).string}")
                    break
            else:
                self._chapters_title.append(f"{str(chapter_number)}: {backup_title}")

            #Extracting each chapter's raw text
            text = [soup.get_text()]
            self._chapters_text.append(' '.join(text))
            
            #Updating chapter number and self._length each loop
            chapter_number += 1
            self._length += 1

#new workflow -> bookshelf just finds in the sql database and pulls file data when you need!
class Bookshelf():
    def __init__(self):
        self._books = []
        self._length = 0
        self.load_from_file()
        
    def load_from_file(self):
        books = get_stored_books()
        for book in books:
            #There's probably a better way of writing this but i just need it to work for now
            
            id_positional = 0
            path_positional = 1
            title_positional = 2
            author_positional = 3
            language_positional = 4
            length_positional = 5
            new_book = Book(book[id_positional],book[path_positional],
                            book[title_positional],book[author_positional],
                            book[language_positional],book[length_positional])
            
            self._books.append(new_book)

    def add_book(self, path):
        new_book = Book(file_path=path)
        
        #Making a local copy of the ebook
        if isinstance(path, Path) == False:
            original_path = Path(path)
        
        file_name = original_path.parts[-1]
        new_path = abs_root_path / ebook_directory_str / file_name

        if new_path.exists() == False:
            try:
                shutil.copy2(original_path, new_path)
                new_book._set_path(new_path)
            except shutil.Error:
                raise shutil.Error("in Bookshelf.add_book: Something went wrong copying the ebook file to the local folder")
        else:
            print("File already exists in library folder.")
        attributes = new_book.to_list()
        for book in self._books:
            if attributes[0] in book.id:
                print("Book already in library")
                return

        self._books.append(new_book)
        add_to_bookshelf(new_book)

    def find(self):
        """
        Arguments:
            target (str): The book id
        Returns:
            index : The index of the item in self._books
        """
        return find_by_title() #Fix this implementation
    
    def get_book(self, target):
        """Finds a book in self._books
        Arguments:
            target (int): the index of the target in self._books
        Returns:
            book (Book): The book object.
        """
        book = self._books[target]
        return book

    def remove(self, target: Book = None):
        if target == None:
            self.list_books()
            book_index = get_int("Please enter the book number you would like to remove")
            book_index -= 1
            book: Book = self.get_book(book_index)
            remove_from_bookshelf(book)
            self._books.remove(book)
            print("Book successfully removed from bookshelf!")
            
        else:
            remove_from_bookshelf(target)
            self._books.remove(target)
            print("Book successfully removed from bookshelf!")        
        #raise NotImplementedError("Bookshelf.remove function not implemented")

    def list_books(self):
        """Lists all the books currently stored in the bookshelf object
        """
        print("Books currently in library: ")
        i = 1
        for book in self._books:
            print(f"{i}: {book.title}")
            i+=1
        return self._books

con = sqlite3.connect("bookshelf.db")
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS bookshelf(id, path, title, author, language, length)")

def get_stored_books():
    all_books = cur.execute("SELECT * FROM bookshelf")
    all_books = all_books.fetchall()
    return all_books
    

def add_to_bookshelf(new_book: Book):
    book_data = new_book.to_list()
    matches = cur.execute("SELECT * FROM bookshelf WHERE id=?",(new_book.id,))
    if matches.fetchall() == []:
        cur.execute("INSERT INTO bookshelf VALUES(?, ?, ?, ?, ?, ?)", book_data)
        con.commit()
        print("book added to database")
    else:
        print("Book already stored in bookshelf")

def find_by_title():
    """
    Returns:
        match
    """
    
    #target = input("Please enter the title of the book that you would like to find: \n")
    print('')
    titles = cur.execute("SELECT title, path, id FROM bookshelf")
    title_items = titles.fetchall()
    
    search_term = input("Please enter the title of the book to search for: \n")
    matches = []
    for item in title_items:
        if fuzz.partial_ratio(item[0].lower(), search_term) > 80:
            matches.append(item)
    
    if matches == []:
        print("No matches found!")
    
    elif len(matches) == 1:
        print(f"Match found: {matches[0][0]}")
        match = matches[0]
        return match
    
    elif len(matches) > 1:
        print("Found matches: ")

        i = 0
        for items in matches:
            print(f"{i}: {items[0]}")
            i += 1
        print(f"{i}: Cancel / Match not in list")
        
        user_selection = int(input("Please enter your selection: "))
        if user_selection == i:
            return None
        else:
            try:
                match = matches[user_selection]
                return match
            except ValueError:
                raise ValueError("Something went wrong.")

def remove_from_bookshelf(target_book: Book):
    book_id = target_book.id
    cur.execute("DELETE FROM bookshelf WHERE id=?",(book_id,))
    con.commit()
    shelf.load_from_file()


#Test case
if __name__ == "__main__":
    import tkinter, tkinter.filedialog
    
    shelf = Bookshelf()
    shelf.list_books()
    
    # def get_file_path():
    #     book_path = ""
    #     while book_path.endswith('.epub') is not True:
    #         book_path = tkinter.filedialog.askopenfilename(title = "Please select an ebook file.")
    #     return book_path
    # path = get_file_path()
    # shelf.add_book(path)
    # shelf.list_books()

    match = find_by_title()
    shelf.remove()