from flask import Flask, jsonify
import os

app = Flask(__name__)


@app.route("/", methods=["GET"])
def root():
    return jsonify(status="ok", service="minizinc-solvers")


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(host="127.0.0.1", port=5000, debug=debug_mode)
