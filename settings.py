# Helper functions for accessing the plugin's configured settings.

import sublime

def get_settings():
    return sublime.load_settings('Automatic Backups.sublime-settings')

