from flask import Flask, redirect, abort
import json
import os

app = Flask(__name__)
LINKS_FILE = "used_links.json"

def load_links():
    if not os.path.exists(LINKS_FILE):
        return {}
    with open(LINKS_FILE, "r") as f:
        return json.load(f)

def save_links(data):
    with open(LINKS_FILE, "w") as f:
        json.dump(data, f)

@app.route("/call/<string:link_id>")
def call_once(link_id):
    data = load_links()

    if link_id not in data:
        return abort(404, "Ссылка не существует")

    if data[link_id]["used"]:
        return "Ссылка уже использована."

    data[link_id]["used"] = True
    save_links(data)

    phone_number = data[link_id]["phone"]
    return redirect(f"tel:{phone_number}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
