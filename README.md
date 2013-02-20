# Flask-Reloaded

A kinda ghetto way to reload your [Flask](http://flask.pocoo.org/) page when
*any* file (templates, css, js, etc). Useful for rapid prototyping, probably
__totally unsafe in production__.

## Installation
Right now, this isn't up on PyPi, so the best deal would be to clone the repo,
`cd` into it, activate your `virtualenv` (you use virtualenv, right?!) and

    pip install .

## Configuration
_For a full example, see `example/simple/app.py`._

Up around your `import`s, add

    from flask.ext.reloaded import Reloaded

after you've created your `app` object, add `Reloaded(app)`, like this:

    app = Flask()
    reloaded = Reloaded(app)

Use as normal. See the API section for more goodies.

## Template Macro
There's probably some magic way to inject random content into your page, (see
Flask Debug-toolbar integration!) but for the time being flask-reloaded needs to
be invoked as a Jinja2 macro in your template. At the top of the template, add:

    {% from 'reloaded/macros.html' import reloaded %}

then put it someplace in `<body>` or `<head>`:

    {{ reloaded() }}

## [Flask Debug-toolbar](https://github.com/mgood/flask-debugtoolbar) integration
You can use Reloaded with the excellent Flask Debug-toolbar. Check out the full
example in `example/panel/app.py`. Make sure you have installed Flask
Debug-toolbar, and specify the Reloaded panel:

    app.config['DEBUG_TB_PANELS'] = (
        # ...
        'flask_reloaded.panels.ReloadedDebugPanel',
    )
    
Though you still have to use Reloaded...

    DebugToolbarExtension(app)
    reloaded = Reloaded(app)
    
...you _don't_ need the macro, as Flask Debug-toolbar does a great job of
injecting itself automagically. Plus, you might need to override some settings,
and want to use the defaults.

## API    
    
### Python `RELOADED_` config options
All config options are optional, and have fairly sensible defaults.

#### `RELOADED_TEMP_FILE`
The name of the file whose modification time is used to determine whether the
reloader should reload.
Default: `.reloaded`.

#### `RELOADED_URL_PREFIX`
A URL fragment that should be appended to the `reloaded` endpoint and all
static files.
Default: `/reloaded`    

#### `RELOADED_EXTENSIONS`
A list of extensions that will trigger a refresh. You can get this list
from a `Reloaded` instance with `reloaded.default_extensions`.
Default: `coffee css html jpg js less md png svg swf ttf sass woff`

### `app.run()` arguments

#### `reloaded_files`
The non-python files to be monitored: python modules are still handled by
`extra_files`. If you specify this, you'll need to re-add the defaults. You can
get this list from a `Reloaded` instance with `reloaded.default_paths`.
Default: the app's `app.static_folder` and `app.template_folder`. 

### Jinja2 `reloaded()` arguments
All macro arguments are optional.

#### `interval`
How many seconds should elapse between successive checks whether something has
changed? Default: 1 sec.

## It Doesn't Work!
You'll need to make sure you have either:

- set `app.debug` to a truthy value, or
- that you specify `run(use_reloader=True)`

## How Does it Work?
flask-reloaded hacks two different parts of the werkzeug/flask stack.
### reloader
I copy and pasted `_reloader_stat_loop` and added a `touch`-like thing to
modify a temporary file.

### run
I wrap your `app.run` in a thing that injects a bunch of extra files to,
erm, `extra_files`.

## Known Limitations
I've been having some weird behavior with IE 8 (surprise). YMMV.
