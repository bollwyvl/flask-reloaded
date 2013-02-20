import os
import sys
import time
from itertools import chain

from flask import (
    Blueprint,
    jsonify
)


class Reloaded(object):
    def __init__(self,
        app=None,
        tmp_file='.reloaded',
        url_prefix='/reloaded',
        reloaded_files=None,
    ):
        self.app = app
        self.tmp_file = tmp_file
        self.url_prefix = url_prefix

        self.blueprint = Blueprint(
            'reloaded',
            __name__,
            static_folder='static',
            template_folder='templates',
            static_url_path=app.static_url_path + url_prefix
        )

        self._finish_init()

        self.app.register_blueprint(self.blueprint, url_prefix=url_prefix)

    def _finish_init(self):

        @self.blueprint.route('/')
        def should_reload():
            with file(self.tmp_file, 'a+'):
                mtime = os.stat(self.tmp_file).st_mtime

            return jsonify({'mtime': mtime})

        self._patch_reloader()
        self._patch_run()

    def _patch_reloader(self):
        from werkzeug import serving
        from werkzeug.serving import (
            _iter_module_files,
            _log,
        )

        # lifted from werkzeug.serving
        def _reloader_stat_loop(extra_files=None, interval=1):
            """
            When this function is run from the main thread, it will force other
            threads to exit when any modules currently loaded change.

            Copyright notice.  This function is based on the autoreload.py from
            the CherryPy trac which originated from WSGIKit which is now dead.

            :param extra_files: a list of additional files it should watch.
            """
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
                        _log('info', ' * Detected change in %r, reloading,' % (
                            filename
                        ))
                        touch(self.tmp_file)
                        sys.exit(3)
                time.sleep(interval)

        # patch the reloader
        serving.reloader_loop = _reloader_stat_loop

    def _patch_run(self):
        _old_run = self.app.run

        def _hacked_run(*args, **kwargs):
            def rp(*path):
                return os.path.join(self.app.root_path, *path)

            # pass None to not reload... but not sure what you're up to, then
            reloaded_files = kwargs.get('reloaded_files', [])
            reloaded_dirs = []

            if not reloaded_files and reloaded_files is not None:
                # guess that they mean the static folder and templates
                reloaded_dirs = [
                    rp(self.app.template_folder),
                    self.app.static_folder
                ]

            if reloaded_files or reloaded_dirs:
                reloaded_files += reloaded_dirs[:]

                for reloaded_dir in reloaded_dirs:
                    for dirname, dirs, files in os.walk(reloaded_dir):
                        for filename in files:
                            filename = os.path.join(dirname, filename)
                            if os.path.isfile(filename):
                                reloaded_files += [filename]

                reloaded_files.extend(kwargs.get('extra_files', []))

                # patch up the old extra_files
                kwargs['extra_files'] = reloaded_files

            _old_run(*args, **kwargs)

        # patch the app
        self.app.run = _hacked_run
