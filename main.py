from flask import Flask, render_template, send_from_directory, abort, jsonify, request, redirect, url_for, flash
import os
import time
import threading
import webbrowser
import json
from datetime import datetime, timezone, timedelta
import random
import keyboard
from humanize import naturalsize
from glob import glob

app = Flask(__name__)
app.secret_key = 'sandcar'

DATA_DIR = 'data'

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
if os.path.exists(os.path.join(DATA_DIR, "config.json")):
    with open(os.path.join(DATA_DIR, "config.json"), 'r') as filep:
        filej = json.load(filep)
        SERVER_PORT = filej['port']
else:
    SERVER_PORT = '1212'

# heartbeat stuff
heartbeat_active = False
last_heartbeat_time = time.time() - 10

def monitor_heartbeat():
    global heartbeat_active, last_heartbeat_time
    while True:
        if time.time() - last_heartbeat_time > 10:
            heartbeat_active = False
        else:
            heartbeat_active = True
        time.sleep(1)

monitor_thread = threading.Thread(target=monitor_heartbeat)
monitor_thread.daemon = True
monitor_thread.start()

@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    global last_heartbeat_time
    last_heartbeat_time = time.time()
    return "Heartbeat received", 200
# ---

# keyb combination
def listenforkb():
    while True:
        time.sleep(0.1)
        if keyboard.is_pressed('alt+`+1'):
            while keyboard.is_pressed('alt+`+1'):
                time.sleep(0.1)
            webbrowser.open(f"http://localhost:{SERVER_PORT}", new=0, autoraise=True)

keyb_thread = threading.Thread(target=listenforkb)
keyb_thread.daemon = True
keyb_thread.start()
# ---

@app.route('/')
def index():
    if not os.path.exists(os.path.join(DATA_DIR, 'config.json')):
        return redirect(url_for('setupend'))

    folders_data = []

    try:
        folders = [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]
    except FileNotFoundError:
        folders = []

    folders.sort(key=lambda x: int(x), reverse=True)

    for folder in folders:
        activity_path = os.path.join(DATA_DIR, folder, 'activity.json')
        try:
            with open(activity_path, 'r') as file:
                activity_data = json.load(file)
                primary = activity_data.get("focused", "N/A")
        except (FileNotFoundError, json.JSONDecodeError):
            primary = "N/A"

        folders_data.append((folder, primary))

    try:
        img_folder = random.choice(folders)
    except IndexError:
        img_folder = ""
    
    file_size = naturalsize(sum(os.path.getsize(x) for x in glob('./data/**', recursive=True)))
    capture_status = "currently capturing" if heartbeat_active else "not capturing"
    
    # pages
    per_page = 50
    page = request.args.get('page', 1, type=int)
    total_pages = (len(folders_data) + per_page - 1) // per_page
    folders_data = folders_data[(page - 1) * per_page: page * per_page]

    return render_template(
        'homepage.html',
        folders_data=folders_data,
        img_folder=img_folder,
        capture_amount=len(folders),
        file_size=file_size,
        capture_status=capture_status,
        page=page,
        total_pages=total_pages
    )

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    if not query:
        return redirect(url_for('index'))

    results = []

    try:
        folders = [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]
    except FileNotFoundError:
        folders = []

    for folder in folders:
        activity_path = os.path.join(DATA_DIR, folder, 'activity.json')
        try:
            with open(activity_path, 'r') as file:
                activity_data = json.load(file)
                text = activity_data.get("text", "")
                if query.lower() in text.lower():
                    primary = activity_data.get("focused", "N/A")
                    results.append((folder, primary))
        except (FileNotFoundError, json.JSONDecodeError):
            continue

    try:
        img_folder = random.choice(folders)
    except IndexError:
        img_folder = ""
    
    total_results = len(results)

    # pages
    per_page = 50
    page = request.args.get('page', 1, type=int)
    total_pages = (total_results + per_page - 1) // per_page
    results = results[(page - 1) * per_page: page * per_page]

    return render_template(
        'search.html',
        folders_data=results,
        img_folder=img_folder,
        capture_amount=total_results,
        page=page,
        total_pages=total_pages
    )

@app.route('/folder')
def folder():
    os.startfile(os.path.normpath("data"))
    return redirect("/")

@app.route('/<folder>/<filename>')
def serve_file(folder, filename):
    folder_path = os.path.join(DATA_DIR, folder)
    if not os.path.isdir(folder_path):
        abort(404)
    return send_from_directory(folder_path, filename)

@app.template_filter('to_datetime')
def to_datetime_filter(unix_timestamp):
    return datetime.fromtimestamp(int(unix_timestamp), tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

@app.route('/setup', methods=['GET', 'POST'])
def setupend():
    if request.method == 'POST':
        porty = request.form['port']
        intervaly = request.form['interval']
        discy = 'accept_disc' in request.form

        errors = []
        # Validate disclaimer
        if not discy:
            errors.append('You must accept the disclaimer.')

        # Validate port
        try:
            porty = int(porty)
            if not (1 <= porty <= 65535):
                raise ValueError
        except ValueError:
            errors.append('Invalid port. Please enter a number between 1 and 65535.')

        # Validate interval
        try:
            intervaly = int(intervaly)
            if not (15 <= intervaly <= 300):
                raise ValueError
        except ValueError:
            errors.append('Invalid interval. Please enter a number between 15 and 300.')

        if len(errors) > 0:
            for erro in errors:
                flash(erro)
            return redirect(url_for('setupend'))
        else:
            config = {
                'port': porty,
                'interval': intervaly
            }

            with open(os.path.join(DATA_DIR, 'config.json'), 'w') as config_file:
                json.dump(config, config_file)

            return "Operation complete! Please, run main.py again in order for the changes to take effect."

    if os.path.exists(os.path.join(DATA_DIR, 'config.json')):
        flash('You already have a config file. Doing this will overwrite your previous one.')
    return render_template('setup.html')

if __name__ == '__main__':
    app.run(debug=True, port=str(SERVER_PORT))
