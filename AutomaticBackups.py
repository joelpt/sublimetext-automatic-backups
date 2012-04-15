# Sublime Text 2 event listeners and commands interface for automatic backups.

import sublime
import sublime_plugin
import os
import shutil

import backup_paths
from backups_navigator import BackupsNavigator

nav = BackupsNavigator()  # our backup navigator state manager
settings = sublime.load_settings('Automatic Backups.sublime-settings')


class AutomaticBackupsEventListener(sublime_plugin.EventListener):

    """Creates an automatic backup of every file you save. This
    gives you a rudimentary mechanism for making sure you don't lose
    information while working."""

    def on_post_save(self, view):
        """When a file is saved, put a copy of the file into the
        backup directory."""

        # don't save files above configured size
        if view.size() > settings.get("max_backup_file_size_bytes"):
            print 'Backup not saved, file too large (%d bytes)' % view.size()
            return

        filename = view.file_name()
        newname = backup_paths.get_backup_filepath(filename)
        if newname == None:
            return

        (backup_dir, file_to_write) = os.path.split(newname)

        # make sure that we have a directory to write into
        if os.access(backup_dir, os.F_OK) == False:
            os.makedirs(backup_dir)

        shutil.copy(filename, newname)
        print 'Backup saved to:', newname

        nav.reinit()

    def on_activated(self, view):
        """Reinit backups navigator on view activation, just in case
        file was modified outside of ST2."""
        if view.file_name() != nav.current_file:
            nav.reinit()

    def on_load(self, view):
        nav.reinit()


class AutomaticBackupsCommand(sublime_plugin.TextCommand):

    """Wires up received commands from keybindings to our BackupsNavigator
    instance."""

    def is_enabled(self, **kwargs):
        return self.view.file_name() is not None

    def run(self, edit, **kwargs):
        command = kwargs['command']

        if command in ('jump', 'step'):
            forward = kwargs['forward']

        if nav.index is None:
            nav.find_backups(self.view)

        if command == 'step':  # move 1 step forward or backward in history
            if forward:
                nav.nav_forwards()
            else:
                nav.nav_backwards()
        elif command == 'jump':  # jump to beginning/end of history
            if forward:
                nav.nav_end()
            else:
                nav.nav_start()

        if not nav.found_backup_files:
            sublime.status_message('No automatic backups found of this file')
            return

        if nav.at_last_backup():
            if command == 'merge':
                sublime.error_message('You are viewing the current version of this file. Navigate to a backup version before merging.')
                return
            if nav.just_reverted:
                sublime.status_message('Showing current version')
            else:
                nav.revert(self.view)
            return

        nav.backup = nav.found_backup_files[nav.index]
        nav.backup_full_path = os.path.join(nav.backup_path,
                nav.backup)

        if command == 'merge':
            nav.merge(self.view)
        else:
            nav.load_backup_to_view(self.view, edit)
