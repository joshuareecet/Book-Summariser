TODO (HIGH to LOW priority): 

1. Add exceptions for edge cases e.g:
    1.1 Book may not have any chapters at all? what do we do
    1.2 User does not have an epub, cannot escape the while loop

2. Add book class: gives easy access to key features of the book even after processing:
    2.1 Store gemini calls for chapter summaries (not sure about this feature anymore)
    2.2 Integrate an SQL database for storage (definitely investigate)

3. Combine epub_to_html and html_to_str into one function / Make them class functions
    3.1 Add both str and html to the book class (done ?)
    3.2 Then can call straight from object of book class for searching in gemini (done ?)
    
4. Add unique identifier for each stored book. Could use ISBN number. - easy implement now!

5. Integrate with a book tracker
    5.1 Calibre - primary target


6. Create GUI interface 

7. Investigate running local LLM: https://github.com/abetlen/llama-cpp-python
    7.1 investigate hardware requirements

BUGS FOUND:
1. if bookshelf.json exits but is empty breaks storage function