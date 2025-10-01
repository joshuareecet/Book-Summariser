import tkinter , tkinter.filedialog

def get_file_path():
    book_path = ""
    while book_path.endswith('.epub') is not True:
        book_path = tkinter.filedialog.askopenfilename(title = "Please select an ebook file.")
    return book_path

def get_int(prompt: str, min = None, max = None):
    output = input(prompt)
    try:
        output = int(output)
    except ValueError:
        output = get_int(prompt, min, max)

    if min is not None and max is not None:
        while output <= min or output >= max:
            print(f"Please enter a valid number within (not inclusive of): \n"
                  f"min: {min}\n"
                  f"max: {max}"
            )
            output = int(input(prompt))
    return output   