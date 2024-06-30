from flask import Flask, render_template, send_from_directory, abort, jsonify, request, redirect, url_for
import os
import json
from datetime import datetime, timezone
import random
from humanize import naturalsize
from glob import glob

app = Flask(__name__)

DATA_DIR = 'data'

@app.route('/')
def index():
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
    
    return render_template('homepage.html', folders_data=folders_data, img_folder=img_folder, capture_amount=len(folders_data), file_size=file_size)

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
        img_folder = random.choice(results)
    except IndexError:
        img_folder = ""
    
    return render_template('search.html', folders_data=results, img_folder=img_folder, capture_amount=len(results))

# @app.route('/folder')
# def folder():
#     os.startfile(os.path.normpath("data"))
#     return redirect("/")

@app.route('/<folder>/<filename>')
def serve_file(folder, filename):
    folder_path = os.path.join(DATA_DIR, folder)
    if not os.path.isdir(folder_path):
        abort(404)
    return send_from_directory(folder_path, filename)

@app.template_filter('to_datetime')
def to_datetime_filter(unix_timestamp):
    return datetime.fromtimestamp(int(unix_timestamp), tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

if __name__ == '__main__':
    app.run(debug=True, port='1212')
