import sys
import os

# this is hackish, you won't need it!
sys.path.append(os.path.join("..", os.path.dirname(__file__)))

from flask import (
    Flask,
    render_template,
)

from flask.ext.reloaded import Reloaded

# create the app
app = Flask(__name__, static_url_path="/static")

# wrap the app
Reloaded(app)

@app.route('/')
def hello_world():
    return render_template("hello.html")

if __name__ == "__main__":
    app.run(use_reloader=True)