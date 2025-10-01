#Imports required for processing ebooks
import ebooklib , ebooklib.epub
from ebooklib import epub
#Imports required for parsing html content
from bs4 import BeautifulSoup
#Imports required for storing books as dict
import json
#Imports required for interacting with sql database
import sql_database
from sql_database import add_to_bookshelf, remove_from_bookshelf, find_by_title
#Imports required for copying epub files to local directory
from pathlib import Path
import shutil


#Constants
ebook_directory_str = 'ebooks'
abs_root_path = Path.cwd()

class Book():  
    def __init__(self, file_path: str = None, length: int = None, title: str = None,
                  author: list = None, lang: str = None, id: list = None):
        """Please remember to properly populate using Bookobject.populate() when calling from bookshelf
        """
        #Initialising as complete unknown
        self._path: str = file_path if file_path else "Unknown path"
        self._length = length if length else 0
        self._title: str = title if title else "Unknown title"
        self._author: str = author if author else "Unknown Author"
        self._language: str = lang if lang else "Unknown Language"
        self._id = id if id else "Unknown id"
        self._populated = False

    def populate(self, file_path: Path):
        if self._populated == False:
            self._path = file_path
            try:
                _epub_book: ebooklib.epub.EpubBook = epub.read_epub(file_path)
            except FileNotFoundError:
                raise FileNotFoundError(f"File not found, please remove {self._title} from bookshelf.")
            #Getting the metadata using ebooklib
            author_metadata: str = _epub_book.get_metadata('DC','author')
            title_metadata: str = _epub_book.get_metadata('DC','title')
            language_metadata: str = _epub_book.get_metadata('DC','language') #this can return the format e.g. XML maybe we can use this
            id_metadata = _epub_book.get_metadata('DC','identifier')

            #Converting metadata into information for storage
            self._title = title_metadata[0][0] if title_metadata else "Unknown title"
            self._author: list = [str(a) for a in author_metadata] if author_metadata else "Unknown Author"
            self._language = language_metadata[0][0] if language_metadata else "Unknown Language"
            self._id = id_metadata if id_metadata else "Unknown id"
            
            #Initialising book info 
            self._chapters_title = []
            self._chapters_text = []
            
            #Populating book info
            self.epub_to_str(_epub_book)
            self._populated = True


    #Getters
    def author(self):
        """
        Returns:
            self._author (list): A list containing the author name / names
        """
        return self._author
    def path(self):
        """
        Returns:
            self._path (str): The path to the book
        """
        return self._path #may remove this or add some sort of redundancy if the host changes the file path
    def title(self):
        """
        Returns:
            self._title (str): The title of the book
        """        
        return self._title
    def language(self):
        """
        Returns:
            self._language (str): The language of the book e.g. 'en'
        """        
        return self._language
    def length(self):
        """
        Returns:
            self._length (int): The number of chapters - 0 = 0 chapters
        """
        return self._length
    def id(self):
        """
        Returns:
            self._id (list): A list **************************************** needs to be finished --------------------------------------------------------------------------
        """
        return list(self._id)
    def uuid(self):
        uuid = str(self._id[0][0])
        return uuid
    
    def chapter_text(self, chapter_number):
        """
        Arguments:
            chapter_number (int): The number of the chapter to be accessed
        Returns:
            self._chapters_text[chapter_number] (str): The text in the accessed chapter
        """
        return self._chapters_text[chapter_number]
    def chapter_titles(self):
        """
        Returns:
            self._chapters_title (list): A list containing the chapter titles
        """
        return list(self._chapters_title)
    
    #Setters
    def set_author(self, author: list): #should add way to input multiple authors. Authors should be a list of strings.
        """
        Arguments:
            author : Either a list of strings or a string containing the author name / names
        """
        self._author = author
    def _set_path(self, path: Path):
        """
        Arguments:
            path (Path): Path to the new location as a pathlib.Path object
        """
        self._path = path

    def set_title(self, title: str):
        """
        Arguments:
            title (str): The new title
        """
        self._title = title
    def set_language(self, lang: str):
        """
        Arguments:
            lang (str): The new language e.g. 'en'
        """
        self._language = lang
    
    #Core functionality
    def epub_to_str(self, _epub_book):
        """
        Function converts an epub to string format for processing
        
        Side effects:
            self._chapters_html (list) -> a list with the html version of each chapter at each index
            self._chapters_text (list) -> The raw text version of self._chapters_html
            self._chapters_title (list) -> A list containing the titles of each chapter
            self._length (int) -> The total num. of chapters
        """        
        #First convert epub to html format
        self._chapters_html = []
        backup_titles = []
        #chapters = book.get_items_of_type(ebooklib.ITEM_DOCUMENT)
        for item in _epub_book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                content = item.get_content()
                #We can ignore any chapters that have less than 2000 characters in them 
                min_character_count = 2000
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
    
    def to_dict(self):
        """A function to translate the core attributes of the class to a dictionary
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
        attributes = [
            self.uuid(),      
            self._path,
            self._title,          
            self._author if isinstance(self._author, str) else self._author.copy(),
            self._language,       
            self._length
        ]
        return attributes

class Bookshelf():
    def __init__(self):
        #Initialising variables
        self._books_as_dict = []
        self._books = []
        self._length = 0

        #Populating variables
        self.get_stored_books()

    #Functions for interacting with storage
    def get_stored_books(self):
        #Getting the books as a dict
        try:
            with open("bookshelf.json") as file:
                self._books_as_dict = json.load(file)
                self._length = len(self._books_as_dict)
        except FileNotFoundError:
            print("Bookshelf file missing, creating empty bookshelf. Ignore if this is the first run.")
            self._books_as_dict = []
            with open("bookshelf.json", 'w') as file:
                pass
        except json.JSONDecodeError:
            print("Something went wrong when decoding the bookshelf file. Please create a back-up, and manually inspect to proceed")
        
        #Turning the dict into a list of book objects
        for books in self._books_as_dict:
            self._books.append(Book(
                Path(books['path']),
                books['length'],
                books['title'],
                books['author'],
                books['language'],
                books['id']
                ))
    def load_bookshelf(self):
        pass

    def add_book(self, file_path):

        new_book = Book()
        new_book.populate(file_path)
        
        #Getting the path to the ebook and it's new path inside /ebooks
        original_path = Path(file_path)
        file_name = original_path.parts[-1]
        new_path = abs_root_path / ebook_directory_str / file_name
        #Copying the ebook and altering the self._path to lead to the new copy
        if new_path.exists() == False:
            try:
                shutil.copy2(original_path, new_path)
                new_book._set_path(new_path)
            except shutil.Error:
                raise shutil.Error("Something went wrong when copying the ebook file to the storage directory.")
        else:
            print("File already exists in new location")

        
        #Getting attributes of new book for storage
        attributes = new_book.to_dict()
        
        #Returning if the book is already stored
        for book in self._books_as_dict:
            if attributes['id'][0][0] in book['id'][0][0]: #this should change. should now check against id attribute.
                print("Book already in library")
                return
        
        #Updating books and books as dict
        self._books_as_dict.append(attributes)
        self._books.append(new_book)
        
        #Dumping to bookshelf file for later retreival
        self.__store_in_json()

    def __store_in_json(self):
        #Note: Should we sort the bookshelf as we build it?
        with open("bookshelf.json", 'w') as bookshelf_file:
            bookshelf_file.write(json.dumps(self._books_as_dict))
        print("Book added to library")
        return
    
    def get_book(self, target):
        """Finds a book in self._books and populates it's properties through loading the epub.
        Arguments:
            target (int): the index of the target in self._books
        Returns:
            book (Book): The fully populated book.
            
        """
        location = self._books[target].path()
        book = Book()
        book.populate(location)
        return book

    #FIND FUNCTION NOT FINISHED
    def find(self, target: str):
        """
        Arguments:
            target (str): The book title
        Returns:
            index (tuple): The index of the item in self._books and self._books_as_dict
        """
        index = (0, 0)
        for book in self._books:
            if book.title() == target:
                break
            else:
                index[0] += 1
        for book in self._books_as_dict:
            if book['title'] == target:
                break
            else:
                index[1] += 1
        return index

    #UNFINISHED FUNCTION
    def remove_book(self, target: str):
        self.find(target)
        self._books.__delitem__(target[0])
        self._books.__delitem__(target[1])
        pass

    #Functions for interacting with object
    def books(self):
        """
        Returns:
            self._books (list): a list of all the books stored in the Bookshelf object
        """
        return self._books
    def list_books(self):
        """Lists all the books stored in the Bookshelf object
        """
        print("Books currently in Library: ")
        i = 1
        for book in self.books():
            print(f"{i}: {book.title()}")
            i+=1


if __name__ == "__main__":
    fake_shelf = Bookshelf()
    import tkinter, tkinter.filedialog
    
    def get_file_path():
        book_path = ""
        while book_path.endswith('.epub') is not True:
            book_path = tkinter.filedialog.askopenfilename(title = "Please select an ebook file.")
        return book_path


    path = get_file_path()
    new_book = Book()
    new_book.populate(path)
    print(new_book.id())