# Helper functions for building backup file paths.

import sublime
import os
import re
import datetime

from .settings import get_settings

if sublime.platform() == 'windows':
    from .win32helpers import get_my_documents

def get_base_dir():
    """Returns the base dir for where we should store backups.
    If not configured in .sublime-settings, we'll take a best guess
    based on the user's OS."""

    # Configured setting
    backup_dir = get_settings().get('backup_dir', '')
    if backup_dir != '':
        return os.path.expanduser(backup_dir)

    # Windows: <user folder>/My Documents/Sublime Text Backups
    if sublime.platform() == 'windows':
        return os.path.join(get_my_documents(), 'Sublime Text Backups')

    # Linux/OSX/other: ~/sublime_backups
    return os.path.expanduser('~/.sublime/backups')


def timestamp_file(filename):
    """Puts a datestamp in filename, just before the extension."""

    now = datetime.datetime.today()
    (filepart, extensionpart) = os.path.splitext(filename)
    return '%s-%04d-%02d-%02d_%02d-%02d-%02d%s' % (
        filepart,
        now.year,
        now.month,
        now.day,
        now.hour,
        now.minute,
        now.second,
        extensionpart,
        )


def get_backup_path(filepath):
    """Returns a path where we want to backup filepath."""
    path = os.path.expanduser(os.path.split(filepath)[0])
    backup_base = get_base_dir()

    if sublime.platform() != 'windows':
        # remove any leading / before combining with backup_base
        path = re.sub(r'^/', '', path)
        return os.path.join(backup_base, path)

    # windows only: transform C: into just C
    path = re.sub(r'^(\w):', r'\1', path)

    # windows only: transform \\remotebox\share into network\remotebox\share
    path = re.sub(r'^\\\\([\w\-]{2,})', r'network\\\1', path)

    return os.path.join(backup_base, path)


def get_backup_filepath(filepath):
    """Returns a full file path for where we want to store a backup copy
    for filepath. Filename in file path returned will be timestamped."""
    filename = os.path.split(filepath)[1]
    return os.path.join(get_backup_path(filepath), timestamp_file(filename))
