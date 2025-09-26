# Book Summariser (In Beta Development)
A tool to generate summaries from ebooks (currently supports epub format).

## Features
- **EPUB Support**: Read and process EPUB format ebooks
- **AI-Powered Summaries**: Uses Google Gemini  for intelligent content analysis
- **Dual Summary Modes**: 
  - Chapter summary: Generates summaries of individual chapters.
  - Full book summary: Uses a smart context maintaining algorithm to generate focused summaries of entire books.
- **Supports Fiction + Non Fiction**: 
  - Fiction / Story books: Character-focused summaries with detailed plot analysis for casual readers.
  - Non-fiction / Academic texts: Concept-focused summaries for scientific textbooks and literature.
- **Maintains Context in larger texts**:
  - Splits larger books into sections, generating smaller summaries based on each section, then analysing each smaller summary to create a final detailed summary.
- **Maintains a record of books**
  - Records previously uploaded books, so you don't have to re-upload every time.

## Quick Start

### Prerequisites

- Python 3.7+
- Google Gemini API key (get one from [Google AI Studio](https://aistudio.google.com/))

### Installation

1. Clone the repository:
```bash
git clone https://github.com/joshuareecet/Book-Summariser.git
cd Book-Summariser
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your API key:
   - The app will prompt you for your Gemini API key on first run, please generate your own API key using: https://ai.google.dev/gemini-api/docs/api-key
   - You can also manually create a `.env` file before running with:
     ```
     GEMINI_API_KEY="your-api-key-here"
     ```

### Usage

Run the main application:
```bash
python main.py
```

### Planned Features
- [ ] Integration of local LLM for processing of books (using meta Llama models)
- [ ] Searching Book classes for previously generated summaries to reduce gemini API / local LLM usage.
- [ ] Calibre integration for book management
- [ ] GUI interface
- [ ] Support for additional ebook formats (e.g. pdf)


**Note**: This tool is designed for personal use and educational purposes, please respect copyright laws - use of AI features should be restricted to books you own, and any generated content is not to be distributed. If you use Gemini API to process ebooks, ensure that you are using the paid tier to opt out of data being used for training future models.