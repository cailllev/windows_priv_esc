# BLACK HAT PYTHON
## file_monitor_injector.py
### Description
Monitors file creation in temp folders. Some (older) programs create files, that are later run with admin rights from those programs. Inject our bhpnet.py in those files and we have root reverse shell.

### TODO
- Check privileged of created files, check with process created them (use process_monitor maybe?)
- bhpnet.py has to be in TEMP_Folder, why not combine this with the bhp_trojan (download from git)
- check bhpnet.py start command in all shells (ps1, cmd, bash)

## process_monitor.py
### Description
Monitors running processes.

### TODO
- read up in Black Hat Python how this is used originally.