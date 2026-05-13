from flask import Flask, render_template, request
import subprocess
import os
import shutil
import time

app = Flask(__name__)

STATIC_DIR = "static"

@app.route("/", methods=["GET", "POST"])
def index():
    images = None
    code = ""

    if request.method == "POST":
        code = request.form["code"]

        with open("debug.c", "w") as f:
            f.write(code)

        subprocess.run(["python", "optimizer.py"], check=True)

        timestamp = str(int(time.time()))

        output_files = {
            "ast": "ast.png",
            "original": "cfg_original.png",
            "optimized": "cfg_optimized.png",
            "pipeline": "pipeline_graph.png"
        }

        images = {}

        for key, filename in output_files.items():
            if os.path.exists(filename):
                new_name = f"{key}_{timestamp}.png"
                shutil.copy(filename, os.path.join(STATIC_DIR, new_name))
                images[key] = new_name

    return render_template("index.html", code=code, images=images)

if __name__ == "__main__":
    os.makedirs(STATIC_DIR, exist_ok=True)
    app.run(debug=True)
