from flask import (
    current_app,
    render_template,
)


from flask_debugtoolbar.panels import DebugPanel

# hello? looks like an il8n attempt?
_ = lambda x: x

class ReloadedDebugPanel(DebugPanel):
    """
    A panel to display HTTP headers.
    """
    name = 'Autoreload'
    has_content = True
    # List of headers we want to display

    def nav_title(self):
        return _('Autoreload')

    def nav_subtitle(self):
        return 'Initializing...'
    
    def title(self):
        return _('Autoreload')
        
    def url(self):
        return ''

    def content(self):
        context = {}
        return render_template('reloaded/panel.html', **context)