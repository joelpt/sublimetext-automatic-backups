# Manages backup history navigation state and operations.

import os
import re
import sublime
from subprocess import Popen

import backup_paths

settings = sublime.load_settings('Automatic Backups.sublime-settings')


class BackupsNavigator:

    """Stateful manager for navigating through a view's backup history."""

    index = None
    just_reverted = False
    found_backup_files = None
    current_file = None

    def __init__(self):
        self.reinit()

    def reinit(self):
        self.index = None
        self.just_reverted = False
        self.found_backup_files = None
        self.current_file = None

    def find_backups(self, view):
        """Look in the backup folder for all backups of view's file."""
        fn = view.file_name()
        self.current_file = fn

        (f, ext) = os.path.splitext(os.path.split(fn)[1])
        self.backup_path = backup_paths.get_backup_path(view.file_name())

        dir_listing = os.listdir(self.backup_path)
        dir_listing.sort()

        date = '-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}'
        pattern = '%s%s%s' % (f, date, ext)
        matcher = re.compile(pattern)

        self.found_backup_files = filter(lambda x: matcher.match(x),
                dir_listing)

        self.index = len(self.found_backup_files) - 1

    def nav_forwards(self):
        self.index += 1
        self.index = min(len(self.found_backup_files) - 1, self.index)

    def nav_backwards(self):
        self.index -= 1
        self.index = max(0, self.index)
        self.just_reverted = False

    def nav_start(self):
        self.index = 0

    def nav_end(self):
        self.index = len(self.found_backup_files) - 1

    def revert(self, view):
        """Revert current view to current file (drop all unsaved changes)."""
        sublime.set_timeout(lambda: do_revert(view), 50)
        self.just_reverted = True
        sublime.status_message('Showing current version')

    def at_last_backup(self):
        return self.index == len(self.found_backup_files) - 1

    def load_backup_to_view(self, view, edit):
        """Replaces contents of view with navigator's current backup file."""
        pos = view.viewport_position()

        with file(self.backup_full_path) as old_file:
            view.erase(edit, sublime.Region(0, view.size()))

            data = old_file.read()

            current_encoding = view.encoding()
            if current_encoding == 'Western (Windows 1252)':
                current_encoding = 'windows-1252'
            elif current_encoding == 'Undefined':
                current_encoding = 'utf-8'

            try:
                unicoded = unicode(data, current_encoding)
            except UnicodeDecodeError:
                unicoded = unicode(data, 'latin-1')  # should always work

            view.insert(edit, 0, unicoded)

        sublime.status_message('%s [%s of %s]' % (self.backup,
                               self.index + 1,
                               len(self.found_backup_files) - 1))

        reposition_view(view, pos)

    def merge(self, view):
        """Perform a merge with an external tool defined in settings."""
        merge_cmd = settings.get('backup_merge_command')

        if not merge_cmd:
            sublime.error_message(
                'Merge command is not set.\n' +
                'Set one in Preferences->Package Settings->Automatic Backups.')
            return

        cmd = merge_cmd.format(
           oldfilename=self.backup,
           oldfilepath=self.backup_full_path,
           curfilename=os.path.split(self.current_file)[1],
           curfilepath=self.current_file)
        sublime.status_message('Launching external merge tool')

        try:
            Popen(cmd)
        except Exception as e:
            sublime.error_message(
                'There was an error running your external merge command.\n' +
                'Please check your backup_merge_command setting.\n\n' +
                'Error given was:\n' + e.strerror + '\n\n' +
                'Check View->Show Console to view the command line that failed.'
            )
            print 'Attempted to execute:\n' + cmd


def do_revert(view):
    """Perform a revert of the current view (drop all changes)."""
    pos = view.viewport_position()
    view.run_command('revert')
    sublime.set_timeout(lambda: reposition_view(view, pos), 50)  # must delay


def reposition_view(view, pos):
    """Set viewport's scroll position in view to pos."""
    # I don't know why this works, but it does: Setting viewport to just pos
    # makes it scroll to the top of the buffer. Setting it to +1 then +0
    # position works. Probably something to do with ST2 getting confused that
    # the buffer changed and giving it a different pos causes it to resync
    # things vs. just giving it the same pos again.
    view.set_viewport_position((pos[0], pos[1] + 1))
    view.set_viewport_position((pos[0], pos[1] + 0))
