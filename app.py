from flask import Flask, request, jsonify, render_template
from services.db import *
from services.spx_api import get_tracking

app = Flask(__name__)

init_db()

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
    code = request.json["tracking_number"]
    data = get_tracking(code)

    records = data["data"]["sls_tracking_info"]["records"]

    return jsonify(records)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)