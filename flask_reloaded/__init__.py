"""
Flask-Reloaded

A kinda-ghetto browser autoreloader for Flask
"""
import os
import sys
import time
from itertools import chain

from werkzeug import serving
from werkzeug.serving import (
    _iter_module_files,
    _log,
)

from flask import (
    Blueprint,
    jsonify
)


class Reloaded(object):
    """
    The main class, in the style of http://flask.pocoo.org/docs/extensiondev/
    """
    def __init__(self, app=None):
        """
        Should somehow support a factory... but probably won't
        """
        if app is not None:
            self.app = app
            self.init_app(self.app)
        else:
            self.app = None

    def init_app(self, app):
        """
        Should somehow support a factory... but probably won't
        """
        app.config.setdefault('RELOADED_TEMP_FILE', '.reloaded')
        app.config.setdefault('RELOADED_URL_PREFIX', '/_reloaded')
        app.config.setdefault('RELOADED_EXTENSIONS', self.default_extensions)

        blueprint = Blueprint(
            'reloaded',
            __name__,
            static_folder='static',
            template_folder='templates',
            static_url_path=app.static_url_path + self.url_prefix
        )

        @blueprint.route('/')
        def should_reload():
            """
            The main view the gives back the mtime of the most recently
            modified file (stored in RELOADED_TEMP_FILE)
            """
            with file(self.tmp_file, 'a+'):
                mtime = os.stat(self.tmp_file).st_mtime

            return jsonify({'mtime': mtime})

        self._patch_reloader()
        self._patch_run()

        self.app.register_blueprint(blueprint, url_prefix=self.url_prefix)

    @property
    def default_extensions(self):
        """
        A nice list of modern extensions that would trigger a refresh
        """
        exts = 'coffee css html jpg js less md png svg swf ttf sass woff'
        return exts.split(' ')

    @property
    def default_paths(self):
        """
        Returns the static and template directories for the app and all its
        Blueprints
        """
        def rooted(path, obj=None):
            """
            Weird path munging on PackageBoundObject
            """
            if obj is None:
                obj = self.app

            return os.path.abspath(
               os.path.join(obj.root_path, *(path,))
            )

        yield rooted(self.app.template_folder)
        yield rooted(self.app.static_folder)

        for bpr in self.app.blueprints.values():
            if bpr.static_folder:
                yield rooted(bpr.static_folder, bpr)

            if bpr.template_folder:
                yield rooted(bpr.template_folder, bpr)

    @property
    def url_prefix(self):
        """
        Where should this live? _reloaded
        """
        return self.app.config['RELOADED_URL_PREFIX']

    @property
    def tmp_file(self):
        """
        What is this called? .reloaded
        """
        return self.app.config['RELOADED_TEMP_FILE']

    @property
    def extensions(self):
        """
        What extensions do you care about?
        """
        return self.app.config['RELOADED_EXTENSIONS']

    def _patch_reloader(self):
        """
        lifted from werkzeug.serving
        """
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
                """
                emulate bash `touch`
                """
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
        """
        Add the reloaded files
        """
        _old_run = self.app.run

        def _hacked_run(*args, **kwargs):
            """
            replaces `app.run`, passing through all args
            """
            paths = kwargs.get('reloaded_paths', list(self.default_paths))
            files = []
            dirs = []
            exts = self.extensions

            def _find_paths(path, files, dirs):
                """
                recursively add all found matching files (and their parent dirs)
                to files and dirs, respectively. not bullet-proof
                """
                for dirname, dir_dirs, dir_files in os.walk(path):
                    for filename in dir_files:
                        filename = os.path.join(dirname, filename)
                        ext = filename.split('.')[-1].lower()
                        if os.path.isfile(filename) and ext in exts:
                            files.append(filename)
                            if dirname not in dirs:
                                dirs.append(dirname)
                    for dir_path in dir_dirs:
                        _find_paths(dir_path, files, dirs)

            for path in paths:
                _find_paths(path, files, dirs)

            files.extend(kwargs.get('extra_files', []))

            if files or dirs:
                print(' ** Will suggest browser reload for:')
                print('    %s types: %s ' % (len(exts), ' '.join(exts)))
                print('    %s folders' % (
                    len(dirs)))
                print('    %s known files' % len(files))

            files.extend(dirs)

            # patch up the old extra_files
            kwargs['extra_files'] = files

            _old_run(*args, **kwargs)

        # patch the app
        self.app.run = _hacked_run
