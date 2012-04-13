import os
import re
import sublime
from subprocess import Popen

import backups


class BackupsNavigator:

    def __init__(self):
        self.reinit()

    def reinit(self):
        self.index = None
        self.just_reverted = False
        self.found_backup_files = None
        self.current_file = None

    def find_backups(self, view):
        fn = view.file_name()
        self.current_file = fn

        (f, ext) = os.path.splitext(os.path.split(fn)[1])
        self.backup_path = backups.backup_file_path(view, just_dir=True)

        dir_listing = os.listdir(self.backup_path)

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
        sublime.set_timeout(lambda: do_revert(view), 50)
        self.just_reverted = True
        sublime.status_message('Showing current version')

    def at_last_backup(self):
        return self.index == len(self.found_backup_files) - 1

    def buffer(self, view, edit):
        pos = view.viewport_position()

        with file(self.backup_full_path) as old_file:
            view.erase(edit, sublime.Region(0, view.size()))

            data = old_file.read()

            try:
                unicoded = unicode(data)
            except UnicodeDecodeError:
                unicoded = unicode(data, 'latin-1')  # should work

            view.insert(edit, 0, unicoded)

        sublime.status_message('%s [%s of %s]' % (self.backup,
                               self.index + 1,
                               len(self.found_backup_files) - 1))

        reposition_view(view, pos)

    def merge(self, view):
        settings = sublime.load_settings('AutomaticBackups.sublime-settings')
        merge_cmd = settings.get('backup_merge_command')

        if not merge_cmd:
            sublime.error_message(
                'Merge command is not set.\nSet one in Preferences->Package Settings->Automatic Backups.')
            return

        cmd = merge_cmd.format(
           oldfilename=self.backup,
           oldfilepath=self.backup_full_path,
           curfilename=os.path.split(self.current_file)[1],
           curfilepath=self.current_file)
        sublime.status_message('Launching external merge tool')
        Popen(cmd)
### TODO make this work for all OS's

def do_revert(view):
    pos = view.viewport_position()
    view.run_command('revert')
    sublime.set_timeout(lambda: reposition_view(view, pos), 50)  # must delay


def reposition_view(view, pos):
    # I don't know why this works, but it does:
    # Setting viewport to just pos makes it scroll to the top
    # of the buffer. Setting it to +1 then +0 position works.
    # Probably something to do with ST2 getting confused that the
    # buffer changed and giving it a different pos causes it to
    # resync things vs. just giving it the same pos again.
    view.set_viewport_position((pos[0], pos[1] + 1))
    view.set_viewport_position((pos[0], pos[1] + 0))
