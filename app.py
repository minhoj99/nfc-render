from flask import Flask, render_template_string, abort
import json
import os

app = Flask(__name__)

DATA_FILE = "used_links.json"

@app.route('/call/<link_id>')
def call(link_id):
    # Проверка наличия файла
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

    # HTML-страница со шрифтом Orbitron и стилем "маркер"
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Маркер активирован</title>
        <meta http-equiv="refresh" content="2;url=tel:{{ phone }}">
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
    """, phone=phone)

