import json
from pathlib import Path

from flask import Flask, render_template

app = Flask(__name__, template_folder="frontend")


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/plan")
def plan():
    # ponytail: ignores the intake and always returns the mock; generate_plan() replaces this
    mock_path = Path(app.root_path, "mock_plan.json")
    return json.loads(mock_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    app.run(debug=True)