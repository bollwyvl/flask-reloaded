# Flask-Reloaded

A kinda ghetto way to reload your Flask page when *any* file (templates, css,
js, etc). Probably totally unsafe in production.

# Installation
Right now, this isn't up on PyPi, so the best deal would be to clone the repo,
`cd` into it and

    pip install .

# Configuration
Up around your `import`s, add

    from flask.ext.reloaded import Reloaded
    
after you've created your `app` object, add `Reloaded(app)`, or like this:

    app = Flask()
    Reloaded(app)
    
You'll need to make sure you have either set `app.debug` to a truthy value,
or that you specify `use_reloader=True` in `run()`.