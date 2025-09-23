# Book Summariser
A tool to generate summaries from ebooks (currently only in epub format).
- Currently supports chapter by chapter summary generation

## Features
- **EPUB Support**: Read and process EPUB format ebooks
- **AI-Powered Summaries**: Uses Google Gemini  for intelligent content analysis
- **Dual Summary Modes**: 
  - Fiction books: Character-focused summaries with plot analysis
  - Non-fiction books: Concept-focused summaries with key definitions


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
- [ ] Enhanced Book class for storage of key book attributes and summaries.
- [ ] Searching Book classes for previously generated summaries to reduce gemini API usage.
- [ ] Calibre integration for book management
- [ ] GUI interface
- [ ] Support for additional ebook formats (e.g. pdf)


**Note**: This tool is designed for personal use and educational purposes. Please respect copyright laws and only process books you own or have permission to analyze.