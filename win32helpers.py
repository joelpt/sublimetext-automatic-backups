import os
import re
import sublime

try:
    import _winreg
except ImportError:
    if sublime.platform() == 'windows':
        sublime.error_message('There was an error importing the _winreg module required by the Automatic Backups plugin.')

def _substenv(m):
    return os.environ.get(m.group(1), m.group(0))


def get_shell_folder(name):
    """Returns the shell folder with the given name, eg "AppData", "Personal",
    "Programs". Environment variables in values of type REG_EXPAND_SZ are expanded
    if possible."""

    HKCU = _winreg.HKEY_CURRENT_USER
    USER_SHELL_FOLDERS = \
        r'Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders'
    key = _winreg.OpenKey(HKCU, USER_SHELL_FOLDERS)
    ret = _winreg.QueryValueEx(key, name)
    key.Close()
    if ret[1] == _winreg.REG_EXPAND_SZ and '%' in ret[0]:
        return re.compile(r'%([^|<>=^%]+)%').sub(_substenv, ret[0])
    else:
        return ret[0]
