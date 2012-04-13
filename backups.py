import sublime
import os
import re
import datetime

import win32helpers


def base_dir(view):
    """Returns the base dir for where we should store backups.
    If not configured in .sublime-settings, we'll take a best guess
    based on the user's OS."""

    # Configured setting
    settings = sublime.load_settings('AutomaticBackups.sublime-settings')
    backup_dir = settings.get('backup_dir', '')
    if backup_dir != '':
        return backup_dir

    # Windows: <user folder>/My Documents/Sublime Text Backups
    if sublime.platform() == 'windows':
        return os.path.join(
            win32helpers.get_shell_folder('Personal'),
            'Sublime Text Backups')

    # Linux/OSX/other: ~/sublime_backups
    return os.path.expanduser('~/sublime_backups')


def timestamp_file(file_name):
    """Puts a datestamp in file_name, just before the extension."""

    now = datetime.datetime.today()
    (filepart, extensionpart) = os.path.splitext(file_name)
    return '%s-%04d-%02d-%02d-%02d-%02d-%02d%s' % (
        filepart,
        now.year,
        now.month,
        now.day,
        now.hour,
        now.minute,
        now.second,
        extensionpart,
        )


## TODO break this below into get_backup_path and get_backup_filepath
## then drop just_dir arg
def backup_file_path(view, just_dir=False):
    """Creates a new name for the file to back up,
    in the base directory, with a timestamp.
    E.g. c:/myfile.txt -> d:/backups/c-drive/myfile-2008-03-20-12-44-03.txt
    """

    buffer_file_name = view.file_name()
    backup_base = base_dir(view)

    if sublime.platform() != 'windows':
        # BUG not right
        return os.path.join(backup_base, buffer_file_name)

    unc_rx = re.compile('^\\\\\\\\')  # unc format, eg \\svr\share
    drive_rx = re.compile('^[A-Za-z]\:\\\\')  # drive-colon, eg c:\foo

    drive_match = drive_rx.match(buffer_file_name)
    unc_match = unc_rx.match(buffer_file_name)

    rewritten_path = None

    if just_dir:
        buffer_file_name = os.path.split(buffer_file_name)[0]

    if drive_match:
        rewritten_path = os.path.join(
            backup_base,
            buffer_file_name[0],
            buffer_file_name[3:])
    elif unc_match:
        rewritten_path = os.path.join(backup_base, 'network',
                buffer_file_name[2:])

    if rewritten_path:
        return (timestamp_file(rewritten_path) if not just_dir else rewritten_path)

    return None  # we can't save this kind of file -- what the hell is it?
