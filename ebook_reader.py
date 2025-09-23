import ebooklib
from bs4 import BeautifulSoup
import tkinter
import tkinter.filedialog
from ebooklib import epub

def epub_to_html(file_path: str):
    book = epub.read_epub(file_path)
    chapters = []
    #chapters = book.get_items_of_type(ebooklib.ITEM_DOCUMENT)
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            chapters.append(item.get_content())
    return chapters

def chapter_to_str(chapter):
    soup = BeautifulSoup(chapter.get_body_content(), 'html.parser')

def chapter_to_str(chapter):
    soup = BeautifulSoup(chapter.get_body_content(), 'html.parser')
    text = [para.get_text() for para in soup.find_all('p')]
    return ' '.join(text)


book_path = tkinter.filedialog.askopenfilename()
chapters = epub_to_html(book_path)
print(chapters)

#book = epub.read_epub(selected_book.name)
#book_items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
#print(book_items)