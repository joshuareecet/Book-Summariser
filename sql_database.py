from core_classes import Book, Bookshelf
from rapidfuzz import fuzz
import sqlite3

"""
Currently non-functional.
"""


con = sqlite3.connect("bookshelf.db")
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS bookshelf(id, path, title, author, language, length)")


def add_to_bookshelf(new_book: Book):
    book_data = new_book.to_list()
    matches = cur.execute("SELECT * FROM bookshelf WHERE id=?",(new_book.uuid(),))
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
    titles = cur.execute("SELECT title, path, id,  FROM bookshelf")
    title_items = titles.fetchall()
    print(title_items)
    
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
    book_uuid = Book.uuid()
    cur.execute("DELETE FROM bookshelf WHERE id=?",(book_uuid,))
    con.commit()


#Test case
if __name__ == "__main__":
    import tkinter, tkinter.filedialog
    
    def get_file_path():
        book_path = ""
        while book_path.endswith('.epub') is not True:
            book_path = tkinter.filedialog.askopenfilename(title = "Please select an ebook file.")
        return book_path
    path = get_file_path()
    
    new_book = Book()
    new_book.populate(path)

    con = sqlite3.connect("bookshelf.db")
    cur = con.cursor()
    add_to_bookshelf(new_book)
    match = find_by_title()
    print(match)