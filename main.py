from flask import Flask, render_template_string, send_from_directory, abort
import os
import json
from datetime import datetime, timezone
app = Flask(__name__)

DATA_DIR = 'data'

@app.route('/')
def index():
    folders_data = []

    try:
        folders = [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]
    except FileNotFoundError:
        folders = []

    folders.sort(key=lambda x: int(x))

    for folder in folders:
        activity_path = os.path.join(DATA_DIR, folder, 'activity.json')
        try:
            with open(activity_path, 'r') as file:
                activity_data = json.load(file)
                primary = activity_data.get("focused", "N/A")
        except (FileNotFoundError, json.JSONDecodeError):
            primary = "N/A"

        folders_data.append((folder, primary))

    html_template = '''
    <!DOCTYPE html>
    <html xmlns="http://www.w3.org/1999/xhtml" 
          xmlns:ms="urn:schemas-microsoft-com:xslt" 
          xmlns:bat="http://schemas.microsoft.com/battery/2012" 
          xmlns:js="http://microsoft.com/kernel">
    <head>
        <meta http-equiv="X-UA-Compatible" content="IE=edge"/>
        <meta name="ReportUtcOffset" content="+3:00"/>
        <title>Activity report</title>
        <style type="text/css">
            body {
                font-family: Segoe UI Light;
                background-color: #181818;
                color: #F0F0F0;
                margin-left: 5.5em;
            }
            h1 {
                color: #11D8E8;
                font-size: 42pt;
            }
            h3 {
                color: #F0A500;
                font-size: 18pt;
            }
            p {
                font-size: 14pt;
                margin-bottom: 1em;
            }
            .small-text {
                font-size: 12pt;
                font-style: italic;
            }
            img {
                margin-top: 1em;
                border: 1px solid #F0F0F0;
                max-width: 55%;
            }
            ul {
                list-style-type: none;
                padding: 0;
            }
            li {
                margin: 0.5em 0;
            }
            a {
                color: #11D8E8;
                text-decoration: none;
                font-size: 18pt;
            }
        </style>
    </head>
    <body>
        <h1>Activity report</h1>
        <h3>Available Reports</h3>
        <ul>
            {% for folder, primary in folders_data %}
            <li>
                <a href="/{{ folder }}/activity.html">{{ folder | to_datetime }} - {{ primary }}</a>
            </li>
            {% endfor %}
        </ul>
    </body>
    </html>
    '''
    
    return render_template_string(html_template, folders_data=folders_data)

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
