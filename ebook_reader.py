import ebooklib
from ebooklib import epub

selected_book = None
book = epub.read_epub(selected_book)

for image in book.get_items_of_type(ebooklib.ITEM_IMAGE):
    print(image)