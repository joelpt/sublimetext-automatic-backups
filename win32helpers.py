import os
import re
import sublime

try:
    import ctypes.wintypes
except ImportError:
    if sublime.platform() == 'windows':
        sublime.error_message('There was an error importing the ctypes.wintypes module required by the Automatic Backups plugin.')

def _substenv(m):
    return os.environ.get(m.group(1), m.group(0))


def get_my_documents():
    """Returns the user's 'My Documents' folder on Windows."""

    # Credit: http://stackoverflow.com/a/3859336/313177
    CSIDL_PERSONAL= 5       # My Documents
    SHGFP_TYPE_CURRENT= 0   # Want current, not default value

    buf= ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(0, CSIDL_PERSONAL, 0, SHGFP_TYPE_CURRENT, buf)
    return buf.value
