from flask import Flask, render_template_string, abort, request, jsonify
import json
import os
import requests

app = Flask(__name__)
DATA_FILE = "used_links.json"

# Voximplant параметры
ACCOUNT_ID = "9709765"
API_KEY = "148ad449-80ea-4998-90f7-34c444a30f00"
APPLICATION_ID = "11849228"
RULE_ID = "3757262"

# Заменить на номер клиента (тестового пользователя, например)
CLIENT_NUMBER = "+998901111111"

def make_voximplant_call(from_number, to_number):
    url = "https://api.voximplant.com/platform_api/StartScenarios/"
    payload = {
        "account_id": ACCOUNT_ID,
        "api_key": API_KEY,
        "application_id": APPLICATION_ID,
        "rule_id": RULE_ID,
        "script_custom_data": json.dumps({
            "from": from_number,
            "to": to_number
        })
    }
    response = requests.post(url, data=payload)
    return response.ok

@app.route('/call/<link_id>')
def call(link_id):
    user_agent = request.headers.get('User-Agent', '').lower()
    if any(bot in user_agent for bot in ['bot', 'telegram', 'preview']):
        return "🔒 Доступ запрещён для ботов", 403

    if not os.path.exists(DATA_FILE):
        return "used_links.json не найден", 500

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

    # Отмечаем как использованную
    links[link_id]["used"] = True
    with open(DATA_FILE, "w") as f:
        json.dump(links, f, indent=2)

    phone = entry["phone"]
    success = make_voximplant_call(CLIENT_NUMBER, phone)

    if not success:
        return "Ошибка звонка", 500

    # HTML с задержкой перехода
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
