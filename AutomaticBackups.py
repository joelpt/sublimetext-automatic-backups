import sublime_plugin
import os
import shutil

import backups
from backups_navigator import BackupsNavigator

nav = BackupsNavigator()


class AutomaticBackupsEventListener(sublime_plugin.EventListener):

    """Creates an automatic backup of every file you save. This
    gives you a rudimentary mechanism for making sure you don't lose
    information while working."""

    def on_post_save(self, view):
        """When a file is saved, put a copy of the file into the
        backup directory"""

        buffer_file_name = view.file_name()
        newname = backups.backup_file_path(view)
        if newname == None:
            return

        (backup_dir, file_to_write) = os.path.split(newname)

        # make sure that we have a directory to write into
        if os.access(backup_dir, os.F_OK) == False:
            os.makedirs(backup_dir)

        print 'Backup saved to:', newname
        shutil.copy(buffer_file_name, newname)

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

        if nav.found_backup_files:
            if nav.at_last_backup():
                if command != 'merge' and not nav.just_reverted:
                    nav.revert(self.view)
            else:
                nav.backup = nav.found_backup_files[nav.index]
                nav.backup_full_path = os.path.join(nav.backup_path,
                        nav.backup)

                print nav.backup_full_path

                if command == 'merge':
                    nav.merge(self.view)
                else:
                    nav.buffer(self.view, edit)
