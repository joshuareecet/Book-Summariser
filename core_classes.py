import ebooklib , ebooklib.epub
from ebooklib import epub
from bs4 import BeautifulSoup
import json, jsons

class Book():
    def __init__(self, file_path: str):
        self._path: str = file_path
        _epub_book: ebooklib.epub.EpubBook = epub.read_epub(file_path)
        self._length = 0

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

    #Getters
    def author(self):
        return self._author
    def path(self):
        return self._path #may remove this or add some sort of redundancy if the host changes the file path
    def title(self):
        return self._title
    def language(self):
        return self._language
    def length(self):
        return self._length
    def chapter_text(self, chapter_number):
        return self._chapters_text[chapter_number]
    def chapter_title(self, chapter_number):
        print(self._chapters_title[chapter_number])
        return self._chapters_title[chapter_number]
    
    #Setters
    def set_author(self, author): #should add way to input multiple authors. Authors should be a list of strings.
        self._author = author
    def set_path(self, path: str):
        self._path = path
    def set_title(self, title: str):
        self._title = title
    def set_language(self, lang: str):
        self._language = lang

    def add_chapter_summary(self, chapter, summary): #Maybe this can be part of the bookshelf?
        pass
    
    #Core functionality
    def epub_to_str(self, _epub_book):
        """Function to convert the ebook to a list containing chapter content in string format, each index contains an individual chapter
        Returns:
            chapters (list): w
        """
        
        #First convert epub to html format
        self._chapters_html = []
        #chapters = book.get_items_of_type(ebooklib.ITEM_DOCUMENT)
        for item in _epub_book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                self._chapters_html.append(item.get_content())

        #Now we can extract the raw text from the html
        for chapter in self._chapters_html:
            soup = BeautifulSoup(chapter, 'html.parser')
            
            #Section for extracting chapter titles
            
            #Attempting to find the title tag
            title_tag = soup.head
            try:
                self._chapters_title.append(title_tag['title'])
            except KeyError:
                try:
                    title_tag = soup.h1
                    self._chapters_title.append(title_tag['title'])
                except (KeyError, TypeError) as error:
                    self._chapters_title.append("Unknown Chapter Title")

            #Section for extracting chapter raw text
            text = [soup.get_text()]
            self._chapters_text.append(' '.join(text))
            
            #Adding a chapter to length for every iteration
            self._length += 1
    
    #Should add a to_dict function as this doesn't give me enough control over what is dumped using jsons
    def to_dict(self):
        attributes = {
            "path" : self._path,
            "author" : self._author,
            "title" : self._title,
            "language": self._language,
            "length" : self._length,
            "id" : self._id
        }
        return attributes


class Bookshelf():
    def __init__(self):
        #Initialising variables
        self._books = []
        self._length = 0

        #Populating variables
        self.get_stored_books()


    def get_stored_books(self):
        try:
            with open("bookshelf.json") as file:
                self._books = json.load(file)
                self._length = len(self._books)
        except FileNotFoundError:
            print("Bookshelf file missing, creating empty bookshelf. Ignore if this is the first run.")
            self._books = []
            with open("bookshelf.json", 'w') as file:
                pass
        except json.JSONDecodeError:
            print("Something went wrong when decoding the bookshelf file. Please create a back-up to proceed")

    def store_book(self, new_book: Book):
        attributes = new_book.to_dict()
        
        for book in range(0,self._length):
            if attributes['title'] in book['_title']: #this should change. should now check against id attribute.
                print("Book already in library")
                return
        else:
            # self._books.append(new_book)
            # #Should we sort the bookshelf as we build it?
            # with open("bookshelf.json", 'w') as bookshelf_file:
            #     bookshelf_file.write(jsons.dumps(self._books))
            # print("Book added to library")
            # return
            
            self._books.append(attributes)
            #Should we sort the bookshelf as we build it?
            with open("bookshelf.json", 'w') as bookshelf_file:
                bookshelf_file.write(json.dumps(self._books))
            print("Book added to library")
            return