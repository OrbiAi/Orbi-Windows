import asyncio
from PIL import ImageGrab, Image
from win32gui import GetWindowText, GetForegroundWindow # pywin32 # type: ignore
import win32gui # type: ignore
import pytesseract
import datetime
import os
import time
import aiohttp
import json
import re
from aiofiles import open as aio_open

DATA_DIR = 'data'

if os.path.exists(os.path.join(DATA_DIR, "config.json")):
    with open(os.path.join(DATA_DIR, "config.json"), 'r') as filep:
        filej = json.load(filep)
        SERVER_PORT = filej['port']
        INTERVAL = filej['interval']
else:
    print("No configuration file found. Please, run main.py")
    exit()

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# heartbeat stuff
async def send_heartbeat():
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://localhost:{SERVER_PORT}/heartbeat"):
                    pass
        except Exception as e:
            print(f"Unable to reach Web UI server (is it running?): {e}")
# ---

def fixspacedupe(text):
    text = text.replace('\t', ' ').replace('\n', ' ')
    ctext = re.sub(r' +', ' ', text)
    return ctext

def getopenwindows():
    focusedwindow = GetWindowText(GetForegroundWindow())
    openwindows = []
    def getopwin(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            if not win32gui.GetWindowText(hwnd) == '':
                openwindows.append(win32gui.GetWindowText(hwnd))
    win32gui.EnumWindows(getopwin, None)
    thelist = {
        'focused': focusedwindow,
        'open': openwindows
    }
    return thelist

async def screenshot(path):
    img = ImageGrab.grab()
    img.save(os.path.join(path, 'capture.png'))

async def gettext(imgpath):
    img = Image.open(imgpath)
    text = pytesseract.image_to_string(img)
    return text

async def genai(text):
    aresponse = "not yet"
    try:
        wininfo = getopenwindows()
        contextstring = f"Focused Window: {wininfo['focused']}\nOpen Windows: {str(wininfo['open'])}"
        url = 'http://localhost:11434/api/generate'
        data = {
            "system": ("You will be given text, which is seen on someone's computer screen. Your ONLY job is to respond with an assumption of what you think they're doing on their computer.  You shouldn't mention why you think so, you should just say what they're doing, say it clearly, be confident. You should provide it in a documentation-style text, should be 1-6 sentences in a 3rd person view and past simple time, refer to the user as 'user'. You should ONLY say about what the user is currently doing on the MAIN window, unless the other windows are clearly related."),
            "model": "llama3:8b",
            "prompt": f"{contextstring}\n{text}",
            "stream": False
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                try:
                    response.raise_for_status()
                except Exception as e:
                    print(f"Unable to reach Ollama server (is it running?): {e}")
                res = await response.json()
                aresponse = res['response']
    except Exception as e:
        print(e)
    while aresponse == "not yet":
        await asyncio.sleep(1)
    return aresponse

async def capturescr():
    timenow = time.time()
    dir_path = os.path.join(DATA_DIR, str(int(timenow)))
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        with open(os.path.join(dir_path, ".lock"), mode='a'): pass

    async with aio_open(os.path.join('templates', 'incomplete.html'), 'r') as file:
        templateh = await file.read()

        async with aio_open(os.path.join(dir_path, 'activity.html'), 'w', encoding="utf-8") as newfile:
            await newfile.write(templateh)

    await screenshot(dir_path)
    wininfo = getopenwindows()
    textonscr = await gettext(os.path.join(dir_path, 'capture.png'))
    description = await genai(textonscr)
    activity = {
        'time': int(timenow),
        'activity': description,
        'focused': wininfo['focused'],
        'open': wininfo['open'],
        'took': round(time.time() - timenow),
        'text': str(fixspacedupe('\n'.join(textonscr.split('\n')[1:])))
    }
    async with aio_open(os.path.join(dir_path, 'activity.json'), 'w') as f:
        await f.write(json.dumps(activity))
    
    async with aio_open(os.path.join('templates', 'template.html'), 'r') as file:
        templateh = await file.read()
    dt_object = datetime.datetime.fromtimestamp(activity['time'])
    readabletime = dt_object.strftime("%A, %B %d, %Y %I:%M:%S %p")
    templateh = (templateh
        .replace("{{ primarywindow }}", str(activity['focused']))
        .replace("{{ description }}", str(activity['activity']))
        .replace("{{ date }}", str(readabletime))
        .replace("{{ allwindows }}", str(activity['open']))
        .replace("{{ took }}", str(activity['took']))
        .replace("{{ img }}", str('capture.png'))
    )
    async with aio_open(os.path.join(dir_path, 'activity.html'), 'w', encoding="utf-8") as newfile:
        await newfile.write(templateh)

    if os.path.exists(os.path.join(dir_path, ".lock")):
        os.remove(os.path.join(dir_path, ".lock"))

async def main():
    async def run_capturescr():
        while True:
            await capturescr()
            await asyncio.sleep(INTERVAL)
    
    async def run_heartbeat():
        while True:
            await send_heartbeat()
            await asyncio.sleep(5)
    
    await asyncio.gather(
        run_capturescr(),
        run_heartbeat()
    )

if __name__ == "__main__":
    asyncio.run(main())
