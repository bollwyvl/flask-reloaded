import os
import sys
import time

from flask import (
    Blueprint,
    jsonify,
    request
)

class Reloaded(object):
    def __init__(self, app=None):
        from werkzeug import serving
        from werkzeug.serving import (
            _iter_module_files,
            _log,
        )
        
        # lifted from werkzeug.serving
        def _reloader_stat_loop(extra_files=None, interval=1): 
            """When this function is run from the main thread, it will force other
            threads to exit when any modules currently loaded change.

            Copyright notice.  This function is based on the autoreload.py from
            the CherryPy trac which originated from WSGIKit which is now dead.

            :param extra_files: a list of additional files it should watch.
            """
            from itertools import chain
            mtimes = {}
            
            def touch(fname, times=None):
                with file(fname, 'a+'):
                    os.utime(fname, times)
            
            while 1:
                for filename in chain(_iter_module_files(), extra_files or ()):
                    try:
                        mtime = os.stat(filename).st_mtime
                    except OSError:
                        continue

                    old_time = mtimes.get(filename)
                    if old_time is None:
                        mtimes[filename] = mtime
                        continue
                    elif mtime > old_time:
                        _log('info', ' * Detected change in %r, reloading, '
                            'browser will update soon' % filename)
                        touch(".reloaded")
                        sys.exit(3)
                time.sleep(interval)
        
        # patch the reloader
        serving.reloader_loop = _reloader_stat_loop
    
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        reloaded = Blueprint(
            "reloaded",
            __name__,
            static_folder="static",
            template_folder="templates",
            static_url_path=app.static_url_path + "/reloaded"
        )
        
        @reloaded.route("/")
        def should_reload():
            with file(".reloaded", 'a+'):
                mtime = os.stat(".reloaded").st_mtime
            
            return jsonify({"mtime": mtime})
            
        app.register_blueprint(reloaded, url_prefix='/reloaded')
        
        _old_run = app.run
        
        def _hacked_run(*args, **kwargs):
            def rp(*path):
                return os.path.join(app.root_path, *path)
        
            extra_files = kwargs.get("extra_files", [])
            
            extra_dirs = [
                rp(app.template_folder),
                app.static_folder
            ]
            extra_files += extra_dirs[:]
            
            for extra_dir in extra_dirs:
                for dirname, dirs, files in os.walk(extra_dir):
                    for filename in files:
                        filename = os.path.join(dirname, filename)
                        if os.path.isfile(filename):
                            extra_files.append(filename)
            
            kwargs["extra_files"] = extra_files
            
            _old_run(*args, **kwargs)
        
        # patch the app
        app.run = _hacked_run