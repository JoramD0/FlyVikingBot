import logging
from flask import Flask, request, jsonify

app = Flask(__name__)
@app.route("/webhook", methods=["POST"])
def webhook_receiver():
    data = request.json
    logging.info(f"webhook: {data}")
