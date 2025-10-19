TODO (HIGH to LOW priority): 

0. Implement textual for a more user-friendly CLI interface.

1. Add exceptions for edge cases e.g:
    1.1 Book may not have any chapters at all? need to decide what to do here..
    1.2 User does not have an epub, cannot escape the while loop. Should allow the user to cancel.
    1.3 What if the chapter is longer than a the context window - need to split chapter up multiple parts as well.

2. Rewrite find implementation in bookshelf (currently just calls find_by_title)

3. Rewrite to implement enums

2. Integrate with a book tracker
    5.1 Calibre - primary target

3. Create GUI interface 

4. Look into if sending the preivous chapter in addition to the current improves context for chapter summary 