TODO (HIGH to LOW priority): 
1. Add exceptions for edge cases e.g:
    1. Book may not have any chapters at all? what do we do
    2. User does not have an epub, cannot escape the while loop

2. Add book class: gives easy access to key features of the book even after processing:
    2.1 Add more parsing for ebook!
        2.1.1 Chapter titles should be associated with each chapter
    2.2 Add class attributes:
        2.2.1 author
        2.2.2 title
        2.2.3 language
        2.2.4. num. chapters
        2.2.5. chapter titles (maybe?)
        2.2.4. **path?
    2.3 Store gemini calls for chapter summaries
    2.4 Integrate an SQL database for storage

3. Combine epub_to_html and html_to_str into one function / Make them class functions
    3.1 Add both str and html to the book class
    3.2 Then can call straight from object of book class for searching in gemini
    
4. Integrate with a book tracker
    4.1 Calibre - primary target
    4.2

5. Create GUI interface 

6. Investigate running local LLM: https://github.com/abetlen/llama-cpp-python
    6.1 investigate hardware requirements