# Orbi
[![nikolan123 - Orbi](https://img.shields.io/static/v1?label=nikolan123&message=Orbi&color=blue&logo=github)](https://github.com/nikolan123/Orbi)
[![stars - Orbi](https://img.shields.io/github/stars/nikolan123/Orbi?style=social)](https://github.com/nikolan123/Orbi)
[![forks - Orbi](https://img.shields.io/github/forks/nikolan123/Orbi?style=social)](https://github.com/nikolan123/Orbi)
[![License](https://img.shields.io/badge/License-GPLv3-blue)](#license)
<br>
My recreation of Windows Recall in Python. It's fully open-source and locally hosted.
<br><br>
If you see an entry with title `N/A` that probably means it's still generating.<br>
All the data is stored in the `data` directory.
> [!WARNING]
> Orbi ("the software") is provided "as is" without warranties of any kind. We are not liable for any damages arising from its use, including the capture or misuse of screenshots containing sensitive information. The software may capture passwords, DRM-protected content, and copyrighted material.
>
> By using Orbi, you agree to comply with all applicable laws. Your use of the software is at your own risk. We do not warrant it will be error-free or free from harmful components.
>
> We are not affiliated with Microsoft. Orbi is licensed under GPLv3. By downloading, installing, or using the software, you acknowledge that you have read, understood, and agree to this disclaimer.
## How it works
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
- Repeats this every 60 seconds
## Setup
### Prerequisites:
- Windows 11 (This has been tested with only Windows 11. It should work on 10, however I cannot confirm that.)
- Python 3.11 (This has been tested with only Python 3.11.9. It should work on 3.12, however I cannot confirm that.)
- A decent computer (It runs fine on my PC's RX 7600, but it will struggle on lower-end hardware.)
### Setup:
- Install Ollama (Download from https://ollama.com/ and run `ollama pull llama3:8b`. Make sure the server is running)
- Download and install [this thingy](https://github.com/UB-Mannheim/tesseract/releases/download/v5.4.0.20240606/tesseract-ocr-w64-setup-5.4.0.20240606.exe)
- Make a venv (`python -m venv venv`, activate with `venv\Scripts\activate`) (optional but recommended)
- Install the required libraries with `pip install pywin32 pillow flask pytesseract humanize aiohttp aiofiles keyboard`
- Run both `main.py` (the web server) and `capture.py` (the ai thingy itself)
## Credits
- [RestartB](https://github.com/RestartB) for doing the frontend <3
## License
Released under [GPLv3](/LICENSE) by [@nikolan123](https://github.com/nikolan123).

![sand cat](http://i.ipg.pw/sandcats/sunaaa0720-20210425-0005.jpg)
