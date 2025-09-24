import ebooklib , ebooklib.epub
from ebooklib import epub

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