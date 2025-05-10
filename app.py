from flask import Flask, render_template_string, abort, request
import json
import os

app = Flask(__name__)
DATA_FILE = "used_links.json"

@app.route('/call/<link_id>')
def call(link_id):
    user_agent = request.headers.get('User-Agent', '').lower()
    bot_signatures = ['telegrambot', 'facebookexternalhit', 'discordbot', 'bot']

    # Защита от ботов-предпросмотра
    if any(bot in user_agent for bot in bot_signatures):
        return "🔒 Доступ запрещён для ботов", 403

    if not os.path.exists(DATA_FILE):
        return "Файл used_links.json не найден", 500

    try:
        with open(DATA_FILE, "r") as f:
            links = json.load(f)
    except json.JSONDecodeError:
        return "Ошибка чтения JSON", 500

    if link_id not in links:
        return "Ссылка не существует", 404

    entry = links[link_id]

    if entry["used"]:
        return "Ссылка уже использована.", 410

    # Помечаем как использованную
    links[link_id]["used"] = True
    with open(DATA_FILE, "w") as f:
        json.dump(links, f, indent=2)

    phone = entry["phone"]

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Маркер активирован</title>
        <meta name="robots" content="noindex,nofollow">
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
        <script>
            setTimeout(() => {
                window.location.href = "tel:{{ phone }}";
            }, 1000);
        </script>
    </head>
    <body>
        <h1>💠 Один звонок.<br>Один долг.<br>Он не повторится.</h1>
    </body>
    </html>
    """, phone=phone)
