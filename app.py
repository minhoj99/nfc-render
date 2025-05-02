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

    # Проверка ID
    if link_id not in links:
        return "Ссылка не существует", 404

    entry = links[link_id]

    if entry["used"]:
        return "Ссылка уже использована.", 410

    # Отмечаем как использованную
    entry["used"] = True
    with open(DATA_FILE, "w") as f:
        json.dump(links, f, indent=2)

    phone = entry["phone"]

    # Возвращаем HTML с задержкой редиректа
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Звонок</title>
        <meta http-equiv="refresh" content="2;url=tel:{{ phone }}">
        <style>
            body { font-family: sans-serif; background: #111; color: #eee; text-align: center; margin-top: 20%; }
        </style>
    </head>
    <body>
        <h1>⏳ Выполняется звонок...</h1>
    </body>
    </html>
    """, phone=phone)
