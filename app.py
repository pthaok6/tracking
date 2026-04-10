import os
import threading
from flask import Flask, request, jsonify, render_template

from services.db import *
from services.spx_api import get_tracking

app = Flask(__name__, static_folder="static", template_folder="templates")

# ======================
# INIT DB
# ======================
init_db()


# ======================
# BOT THREAD
# ======================


threading.Thread(target=run_bot, daemon=True).start()


# ======================
# ROUTES
# ======================
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/orders")
def orders():
    return jsonify(get_orders())


@app.route("/orders/add", methods=["POST"])
def add():
    data = request.json
    add_order(data["code"], data["note"])
    return {"ok": True}


@app.route("/orders/delete", methods=["POST"])
def delete():
    delete_order(request.json["id"])
    return {"ok": True}


@app.route("/track_one", methods=["POST"])
def track():
    code = request.json.get("tracking_number")

    data = get_tracking(code)

    try:
        records = data["data"]["sls_tracking_info"]["records"]
    except Exception:
        return jsonify([])

    return jsonify(records)


# ======================
# HEALTH CHECK
# ======================
@app.route("/health")
def health():
    return "OK"


# ======================
# START SERVER
# ======================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10003))
    app.run(host="0.0.0.0", port=port)
