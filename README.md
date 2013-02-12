# Flask-Reloaded

A kinda ghetto way to reload your [Flask](http://flask.pocoo.org/) page when
*any* file (templates, css, js, etc). Useful for rapid prototyping, probably
__totally unsafe in production__.

## Installation
Right now, this isn't up on PyPi, so the best deal would be to clone the repo,
`cd` into it, activate your `virtualenv` (you use virtualenv, right?!) and

    pip install .

## Configuration
_For a full example, see `example/app.py`._

Up around your `import`s, add

    from flask.ext.reloaded import Reloaded

after you've created your `app` object, add `Reloaded(app)`, like this:

    app = Flask()
    Reloaded(app)
    
Then, when you're ready to run

## Template Macro
There's probably some magic way to inject random content into your page,
but for the time being flask-reloaded needs to be invoked as a Jinja2 macro in
your template. At the top of the template, add:

    {% from 'reloaded/macros.html' import reloaded %}

then put it someplace in `<body>` or `<head>`:

    {{ reloaded() }}

## API    
    
### Python `Reloaded()` arguments
All arguments are optional.

#### `tmp_file`
The name of the file whose modification time is used to determine whether the
reloader should reload.
Default: `.reloaded`.

#### `url_prefix`
A URL fragment that should be appended to the `reloaded` endpoint and all
static files.
Default: `/reloaded`    
    
### Jinja2 `reloaded()` arguments
All macro arguments are optional.

#### `interval`
How many seconds should elapse between successive checks whether something has
changed? Default: 1 sec.

## It doesn't work!
You'll need to make sure you have either:

- set `app.debug` to a truthy value, or
- that you specify `run(use_reloader=True)`

## How does it works?
flask-reloaded hacks two different parts of the werkzeug/flask stack.
### reloader
I copy and pasted `_reloader_stat_loop` and added a `touch`-like thing to
modify a temporary file.

### run
I wrap your `app.run` in a thing that injects a bunch of extra files to,
erm, `extra_files`.