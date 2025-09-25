TODO (HIGH to LOW priority): 


0. FINISH FIND FUNCTION IN BOOKSHELF

1. Add exceptions for edge cases e.g:
    1.1 Book may not have any chapters at all? what do we do
    1.2 User does not have an epub, cannot escape the while loop

2. Book class:
    2.1 Store gemini calls for chapter summaries (blows up storage so maybe not)
    2.2 Switch to SQL database from json - either sqlalchemy or sqlite seem to be suited for this.

3. Combine epub_to_html and html_to_str into one function / Make them class functions
    3.1 Add both str and html to the book class (done ?)
    3.2 Then can call straight from object of book class for searching in gemini (done ?)
    
4. Add unique identifier for each stored book. Could use ISBN number.
    This is potentially implemented now. Need to research more into how id numbers are generated internally using ebooklib.

5. Integrate with a book tracker
    5.1 Calibre - primary target


6. Create GUI interface 

7. Investigate running local LLM: https://github.com/abetlen/llama-cpp-python
    7.1 investigate hardware requirements

BUGS FOUND:
1. if bookshelf.json exits but is empty breaks storage function