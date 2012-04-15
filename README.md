Automatic Backups for Sublime Text 2
====================================

A Sublime Text 2 plugin to automatically save off a backup of your files each time you save.

When you edit text files (scripts, prose, whatever) you often find yourself wishing for an older version. Ever accidentally deleted a chunk from an important configuration file, or wished you could roll back a document a few hours? This plugin takes a copy of every file you save and copies it into a backup directory structure, ensuring that you never lose an old version of a file.


## Installation

 * Install [Package Manager][1].
 * Use `Cmd+Shift+P` or `Ctrl+Shift+P` then `Package Control: Install Package`.
 * Look for `Automatic Backups` and install it.

If you prefer to install manually, install git, then:

    git clone https://github.com/joelpt/sublimetext-automatic-backups "<Sublime Text 2 Packages folder>/Automatic Backups"

## Basic usage

Once installed, any file you save will be automatically copied into your backups folder (defaults to `My Documents\Sublime Text Backups` on Windows and `~/.sublime/backups` on Linux/OSX).

For example, if you change `C:\autoexec.bat` on Windows, you'll get a backup saved somewhere like:

    C:\Users\yourUserName\My Documents\Sublime Text Backups\C\autoexec-2012-03-22-22-22-46.bat

That end bit is the timestamp, so you can see when the file was edited.

To change where the backups are stored, access the plugin's settings in `Preferences->Package Settings->Automatic Backups`.

To see if it's working, open the console with the `View->Show Console` menu item. When you save a file, you should see a line like this, indicating that the file has been backed up:

    Backup saved to: /home/stanislav/.sublime/backups/etc/hosts-2012-03-22-22-22-46


## Backup history navigation

Automatic Backups supports easy navigation through the backup history for any file with stored backups. To use this feature:

 * Press `Ctrl+Alt+[` to navigate backwards one step through a file's backup history.
 * Press `Ctrl+Alt+]` to navigate forwards one step.
 * Press `Ctrl+Shift+Alt+[` to jump to the first copy in the history.
 * Press `Ctrl+Shift+Alt+]` to jump to the current version (that is, the actual file, not a backup).

These commands can also be accessed via `Ctrl+Shift+P` or `Cmd+Shift+P`.


## Merge from backup history

When viewing a backup file via backup history navigation, press `Ctrl+Alt+Shift+M` to merge the backup version you're currently viewing with the latest version of the file using an external merge tool of your choosing.

You'll need to specify the command line for this merge tool; for more information go to `Preferences->Package Settings->Automatic Backups->Settings - Default`.

This command can also be accessed via `Ctrl+Shift+P` or `Cmd+Shift+P`.


## Backup size considerations

Though this plugin currently has no facility for pruning old backups, this probably won't be a problem for you. I have been running some form of this plugin for 2.5 years, and have a total of 27000 individual backup files stored totalling just 400 MB uncompressed. And I can go back to the very first version of any file I've edited in Sublime Text.

To prevent your backup folder from growing too large, check out the `max_backup_file_size_bytes` setting in `Preferences->Package Settings->Automatic Backups`.


## Credits

This code is available on [Github][0]. Pull requests are welcome.

Created by [Joel Thornton][3].

Originally authored for Sublime Text 1 by [Steve Cooper][2].

 [0]: https://github.com/joelpt/sublimetext-automatic-backups
 [1]: http://wbond.net/sublime_packages/package_control
 [2]: http://stevecooper.org/
 [3]: mailto:sublime@joelpt.net


