# fakerecall
My recreation of Windows Recall in Python
(it's goofy)
If you see an entry with title `N/A` that probably means it's still generating.
All the data is stored in the `data` directory.
### How it works
The script takes a screenshot of the computer's screen every 60 seconds, processes the text on screen, gets a list of running apps and supplies all of that information to the `llama3` model.
#### Workflow:
- Creates a new directory with the current timestamp in the `data` directory.
- Takes a screenshot of the screen.
- Saves the screenshot to `data/timestamp/capture.png`.
- Extracts text from the screenshot using pytesseract.
- Retrieves a list of running programs.
- Supplies information to `llama3:8b`.
- Saves AI response and running programs list to `data/timestamp/activity.json`.
- Generates HTML from the JSON and saves it to `data/timestamp/activity.html`.
## Setup
### Prerequisites:
- Windows 11 (This has been tested with only Windows 11. It should work on 10, however I cannot confirm that. )
- Python 3.11 (This has been tested with only Python 3.11.9. It should work on 3.12, however I cannot confirm that.)
- A decent computer (It runs fine on my PC's RX 7600, but it will struggle on lower-end hardware.
### Setup:
- Install Ollama (Download from https://ollama.com/ and run `ollama pull llama3:8b`. Make sure the server is running)
- Download and install [this thingy](https://github.com/UB-Mannheim/tesseract/releases/download/v5.4.0.20240606/tesseract-ocr-w64-setup-5.4.0.20240606.exe)
- Make a venv (`python -m venv venv`, activate with `venv\Scripts\activate`) (optional but recommended)
- Install the required libraries with `pip install pywin32 pillow flask requests pytesseract`
- Run both `main.py` (the web server) and `capture.py` (the ai thingy itself)
