import sys
import os

# this is hackish, you won't need it!
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
)

from flask import (
    Flask,
    render_template,
)

from flask.ext.debugtoolbar import DebugToolbarExtension
from flask.ext.reloaded import Reloaded

# create the app
app = Flask(__name__, static_url_path="/static")
app.debug = True

app.config['SECRET_KEY'] = 'totallyinsecure'

app.config['DEBUG_TB_PANELS'] = (
    'flask_reloaded.panels.ReloadedDebugPanel',
    'flask_debugtoolbar.panels.headers.HeaderDebugPanel',
    'flask_debugtoolbar.panels.logger.LoggingPanel',
    'flask_debugtoolbar.panels.timer.TimerDebugPanel',
)

# wrap the app
DebugToolbarExtension(app)
Reloaded(app)

@app.route('/')
def hello_world():
    return render_template("hello.html")

if __name__ == "__main__":
    app.run()