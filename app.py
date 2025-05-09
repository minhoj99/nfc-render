from flask import Flask, render_template_string, abort
import json
import os
import requests

app = Flask(__name__)
DATA_FILE = "used_links.json"

# === Voximplant параметры ===
VOXIMPLANT_ACCOUNT_ID = "9709765"
VOXIMPLANT_API_KEY = "148ad449-80ea-4998-90f7-34c444a30f00"
VOXIMPLANT_APPLICATION_ID = "11849228"
VOXIMPLANT_RULE_ID = "3757262"

def make_voximplant_call(to_number):
    api_url = "https://api.voximplant.com/platform_api/StartScenarios/"
    payload = {
        "account_id": VOXIMPLANT_ACCOUNT_ID,
        "api_key": VOXIMPLANT_API_KEY,
        "rule_id": VOXIMPLANT_RULE_ID,
        "script_custom_data": json.dumps({"to": to_number}),
        "application_id": VOXIMPLANT_APPLICATION_ID
    }
    response = requests.post(api_url, data=payload)
    return response.json()


@app.route('/call/<link_id>')
def call(link_id):
    if not os.path.exists(DATA_FILE):
        return "Файл used_links.json не найден", 500

    with open(DATA_FILE, "r") as f:
        try:
            links = json.load(f)
        except json.JSONDecodeError:
            return "Ошибка чтения JSON", 500

    if link_id not in links:
        return "Ссылка не существует", 404

    entry = links[link_id]

    if entry["used"]:
        return "Ссылка уже использована.", 410

    entry["used"] = True
    with open(DATA_FILE, "w") as f:
        json.dump(links, f, indent=2)

    phone = entry["phone"]
    result = make_voximplant_call(phone)

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Маркер активирован</title>
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500&display=swap" rel="stylesheet">
        <style>
            body {
                font-family: 'Orbitron', sans-serif;
                background-color: #0f0f0f;
                color: #00ffe1;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                text-align: center;
                padding: 20px;
                margin: 0;
            }
            h1 {
                font-size: 1.8rem;
                line-height: 1.6;
                max-width: 500px;
            }
        </style>
    </head>
    <body>
        <h1>💠 Один звонок.<br>Один долг.<br>Он не повторится.</h1>
    </body>
    </html>
    """)
