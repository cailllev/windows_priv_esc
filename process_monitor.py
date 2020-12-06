import win32con
import win32api
import win32security

import wmi
import os

LOG_FILE = "process_monitor_log.csv"


def get_process_privileges(pid):
    priv_list = []
    try:
        # obtain a handle to the target process
        hproc = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, pid)

        # open the main process token
        htok = win32security.OpenProcessToken(hproc, win32con.TOKEN_QUERY)

        # retrieve the list of privileges enabled
        privs = win32security.GetTokenInformation(htok, win32security.TokenPrivileges)

        # iterate over privileges and output the ones that are enabled
        for priv_id, priv_flags in privs:
            # check if the privilege is enabled
            if priv_flags == 3:
                priv_list.append(win32security.LookupPrivilegeName(None, priv_id))

    except:
        priv_list.append("N/A")

    return "|".join(priv_list)


def log_to_file(message):
    fd = open(LOG_FILE, "ab")
    fd.write(f"{message}\r\n".encode())
    fd.close()


# create a log file header
if not os.path.isfile(LOG_FILE):
    log_to_file("Time,User,Description,Executable,CommandLine,PID,ParentPID,Privileges")

# instantiate the WMI interface
c = wmi.WMI()

# create the process monitor
process_watcher = c.Win32_Process.watch_for("creation")


while True:
    try:
        new_process = process_watcher()

        print(new_process.GetOwner())

        proc_owner = new_process.GetOwner()
        proc_owner = f"{proc_owner[0]}\\{proc_owner[1]}\\{proc_owner[2]}"
        create_date = new_process.CreationDate
        description = new_process.Description
        executable = new_process.ExecutablePath
        cmdline = new_process.CommandLine
        pid = new_process.ProcessId
        parent_pid = new_process.ParentProcessId

        privileges = get_process_privileges(pid)

        process_log_message = f"{create_date,proc_owner,description,executable,cmdline,pid,parent_pid,privileges}"

        print(f"{process_log_message}\r\n")

        log_to_file(process_log_message)

    except:
        pass
