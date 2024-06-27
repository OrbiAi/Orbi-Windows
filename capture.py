from PIL import ImageGrab, Image
from win32gui import GetWindowText, GetForegroundWindow # pywin32 # type: ignore
import win32gui # type: ignore
import pytesseract
import datetime
import os
import time
import requests
import json
from time import sleep

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

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

def screenshot(path):
    img = ImageGrab.grab()
    img.save(os.path.join(path, 'capture.png'))

def gettext(imgpath):
    img = Image.open(imgpath)
    text = pytesseract.image_to_string(img)
    return text

def genai(text):
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
        response = requests.post(url, json=data)
        response.raise_for_status()
        aresponse = response.json()['response']
    except Exception as e:
        print(e)
    while aresponse == "not yet":
        sleep(1)
    return aresponse

def capturescr():
    timenow = time.time()
    if not os.path.exists(os.path.join('data', str(int(timenow)))):
        os.makedirs(os.path.join('data', str(int(timenow))))
    screenshot(os.path.join('data', str(int(timenow))))
    wininfo = getopenwindows()
    description = genai(gettext(os.path.join('data', str(int(timenow)), 'capture.png')))
    activity = {
        'time': int(timenow),
        'activity': description,
        'focused': wininfo['focused'],
        'open': wininfo['open'],
        'took': round(time.time()-timenow)
    }
    with open(os.path.join('data', str(int(timenow)), 'activity.json'), 'w') as f:
        json.dump(activity, f)

    with open('template.html', 'r') as file:
        templateh = file.read()
    dt_object = datetime.datetime.fromtimestamp(activity['time'])
    readabletime = dt_object.strftime("%A, %B %d, %Y %I:%M:%S %p")
    templateh = (templateh
        .replace("{{ primarywindow }}", str(activity['focused']))
        .replace("{{ description }}", str(activity['activity']))
        .replace("{{ date }}", str(readabletime))
        .replace("{{ allwindows }}", str(activity['open']))
        .replace("{{ img }}", str('capture.png'))
        .replace("{{ took }}", str(activity['took']))
    )
    with open(os.path.join('data', str(int(timenow)), 'activity.html'), 'w') as newfile:
        newfile.write(templateh)

while True:
    capturescr()
    sleep(60)
