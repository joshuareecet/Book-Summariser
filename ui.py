from __future__ import annotations

import tkinter
import tkinter.filedialog
from pathlib import Path


def get_file_path() -> Path:
    """Opens a native file-picker dialog and returns the selected .epub path.

    Raises:
        KeyboardInterrupt: If the user cancels the dialog.
    """
    root = tkinter.Tk()
    root.withdraw()
    path = tkinter.filedialog.askopenfilename(
        title="Select an ebook",
        filetypes=[("ePub files", "*.epub")],
    )
    root.destroy()
    if not path:
        raise KeyboardInterrupt("File selection cancelled.")
    return Path(path)


def get_int(
    prompt: str,
    *,
    min_val: int | None = None,
    max_val: int | None = None,
) -> int:
    """Prompts the user for an integer, repeating until a valid value is given.

    If both *min_val* and *max_val* are provided the accepted range is the
    exclusive interval (min_val, max_val).
    
    Raises:
        KeyboardInterrupt: If the user cancels the dialog.
    """
    try:
      while True:
          try:
              value = int(input(prompt).strip())
          except ValueError:
              print("Please enter a valid number.")
              continue
          
          if min_val is not None and max_val is not None:
              if not (min_val < value < max_val):
                  print(
                      f"Please enter a number between {min_val + 1}"
                      f" and {max_val - 1} (inclusive)."
                  )
                  continue
          
          return value
    except KeyboardInterrupt:
        raise KeyboardInterrupt