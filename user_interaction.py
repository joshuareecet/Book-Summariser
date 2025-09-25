import tkinter , tkinter.filedialog

def get_file_path():
    book_path = ""
    while book_path.endswith('.epub') is not True:
        book_path = tkinter.filedialog.askopenfilename(title = "Please select an ebook file.")
    return book_path

if __name__ == "__main__":
    pass