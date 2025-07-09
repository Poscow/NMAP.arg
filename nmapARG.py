import os
import sys
import time
import subprocess
import ipaddress
from colorama import Fore, Style, init
import webbrowser

init(autoreset=True)

current_ip = None
file_saving = True
auto_save = False
ip_log = True
scanned_ips = set()

script_folder = os.path.dirname(os.path.realpath(__file__))
config_dir = os.path.join(script_folder, "config")
logs_dir = os.path.join(script_folder, "logs")

#make sure directories exist
os.makedirs(config_dir, exist_ok=True)
os.makedirs(logs_dir, exist_ok=True)
custom_settings_file = os.path.join(config_dir, "nmap_custom_settings.txt")
ip_log_file = os.path.join(logs_dir, "ip_log.txt")

def print_banner():
    os.system('cls' if os.name == 'nt' else 'clear')  #clear screen

    banner = [
        "███╗   ██╗███╗   ███╗ █████╗ ██████╗ ",
        "████╗  ██║████╗ ████║██╔══██╗██╔══██╗",
        "██╔██╗ ██║██╔████╔██║███████║██████╔╝",
        "██║╚██╗██║██║╚██╔╝██║██╔══██║██╔═══╝ ",
        "██║ ╚████║██║ ╚═╝ ██║██║  ██║██║     ",
        "╚═╝  ╚═══╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝     "
    ]
    
    for line in banner:
        for c in line:
            print(Fore.CYAN + c, end="")
            sys.stdout.flush()
            time.sleep(0.0015)
        print()

    print(Fore.WHITE + "\nNMAP.ARG created by: " + Fore.GREEN + "p0scow" + Fore.WHITE + "\n")

def save_setting(setting):
    settings = {}
    if os.path.exists(custom_settings_file):
        with open(custom_settings_file, "r") as f:
            for line in f:
                if line.strip():
                    key = line.split()[0]
                    settings[key] = line.strip()

    key = setting.split()[0]
    settings[key] = setting

    with open(custom_settings_file, "w") as f:
        for val in settings.values():
            f.write(val + "\n")

def load_settings():
    global file_saving, auto_save, ip_log

    #Default settings
    default_settings = [
        "autosave false",
        "filesaving true",
        "iplog true"
    ]

    if not os.path.exists(custom_settings_file):
        with open(custom_settings_file, "w") as f:
            f.write("\n".join(default_settings) + "\n")

    with open(custom_settings_file, "r") as f:
        for line in f:
            line = line.strip().lower()
            if line == "autosave false":
                auto_save = False
            elif line == "autosave true":
                auto_save = True
            elif line == "filesaving false":
                file_saving = False
            elif line == "filesaving true":
                file_saving = True
            elif line == "iplog false":
                ip_log = False
            elif line == "iplog true":
                ip_log = True

def spinner_process(proc):
    spinner = ['|', '/', '-', '\\']
    idx = 0
    while proc.poll() is None:
        print(Fore.YELLOW + spinner[idx % len(spinner)], end='\r')
        idx += 1
        time.sleep(0.1)

def run_scan(args):
    global file_saving, auto_save, logs_dir, script_folder
    try:
        proc = subprocess.Popen(["nmap"] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        spinner_process(proc)
        output, err = proc.communicate()

        if err:
            print(Fore.RED + err)
        print(Fore.WHITE + output)

        if file_saving:
            if auto_save:
                filename = f"nmap_scan_{int(time.time())}.txt"
                out_path = os.path.join(logs_dir, filename)
                with open(out_path, "w", encoding='utf-8') as f:
                    f.write(output)
                print(Fore.GREEN + f"Output auto-saved to {out_path}.")
            else:
                save = input(Fore.CYAN + "\nDo you want to save this output to a text file in the logs folder? (y/n): ").strip().lower()
                if save == 'y':
                    filename = f"nmap_scan_{int(time.time())}.txt"
                    out_path = os.path.join(logs_dir, filename)
                    with open(out_path, "w", encoding='utf-8') as f:
                        f.write(output)
                    print(Fore.GREEN + f"Output saved to {out_path}.")

    except FileNotFoundError:
        print(Fore.RED + "Nmap is not installed or not in system PATH.")
        print(Fore.YELLOW + "Please download Nmap from: https://nmap.org/download.html")

def user_int():
    global current_ip
    while True:
        user_IP4V = input(Fore.WHITE + "Enter IPv4 Address: ").strip()
        try:
            ipaddress.IPv4Address(user_IP4V)
            current_ip = user_IP4V
            print(Fore.GREEN + f"Selected IP: {current_ip}")
            if ip_log:
                log_ip(current_ip)
            break
        except ipaddress.AddressValueError:
            print(Fore.RED + "Invalid IP (x.x.x.x)")

def log_ip(ip):
    global scanned_ips, ip_log

    #Check write permissions
    try:
        if os.path.exists(ip_log_file):
            if not os.access(ip_log_file, os.W_OK):
                print(Fore.RED + f"Error: No write permissions for {ip_log_file}. IP logging disabled.")
                print(Fore.YELLOW + f"Please ensure you have write permissions for {ip_log_file} or run the program with elevated privileges.")
                ip_log = False
                return
        else:
            #Check if the file is in the directory
            log_dir = os.path.dirname(ip_log_file)
            if not os.access(log_dir, os.W_OK):
                print(Fore.RED + f"Error: No write permissions for directory {log_dir}. IP logging disabled.")
                print(Fore.YELLOW + f"Please ensure you have write permissions for {log_dir} or run the program with elevated privileges.")
                ip_log = False
                return

        #Read existing IPs
        if os.path.exists(ip_log_file):
            with open(ip_log_file, "r") as f:
                for line in f:
                    scanned_ips.add(line.strip())
        
        #Write new IP if not already logged
        if ip not in scanned_ips:
            with open(ip_log_file, "a") as f:
                f.write(ip + "\n")
            scanned_ips.add(ip)

    except PermissionError:
        print(Fore.RED + f"PermissionError: Unable to write to {ip_log_file}. IP logging disabled.")
        print(Fore.YELLOW + f"Please ensure you have write permissions for {ip_log_file} or run the program with elevated privileges.")
        ip_log = False


def displaymenu():
    ip_display = current_ip if current_ip else "None Selected"
    print(Fore.CYAN + "\nSelect Nmap Option:")
    print(Fore.LIGHTBLUE_EX + f"Current IP: {ip_display}\n")

    if current_ip:
        print(Fore.YELLOW + "1. Change IP Address")
    else:
        print(Fore.YELLOW + "1. Select IP Address")

    print("2. Basic Scan")
    print("3. Scan with OS detection")
    print("4. Scan with version detection")
    print("5. Aggressive Scan")
    print("6. Sneaky Scan")
    print("7. Fast Scan")
    print("8. TERM - Custom Settings Terminal")
    print("9. Exit")

def NMAPexecute(choice):
    global current_ip
    if choice == '1':
        user_int()
    elif choice == '8':
        TermMode().run()
    elif choice == '9':
        print(Fore.WHITE + "Exiting...")
        sys.exit()
    else:
        if not current_ip:
            print(Fore.RED + "Please set an IP first (option 1).")
            return

        commands = {
            '2': [],
            '3': ['-O'],
            '4': ['-sV'], 
            '5': ['-A'], #I cant get this to work with more commands
            '6': ['-Pn'],
            '7': ['-T5'] 
        }

        if choice in commands:
            run_scan(commands[choice] + [current_ip])
        else:
            print(Fore.RED + "Invalid option.")


#class because why not
class TermMode:
    def __init__(self):
        self.commands = {
            "exit": self.exit,
            "version": self.version,
            "help": self.help,
            "list settings": self.list_settings,
            "list iplog": self.list_iplog,
            "clear": self.clear,
            "clear settings": self.clear,
            "autosave": self.autosave,
            "filesave": self.filesave,
            "iplog": self.iplog,
            "ipselect": self.ipselect,
            "ip": self.ip,
            "nmap": self.nmap
        }

    def run(self):
        global current_ip, file_saving, auto_save, ip_log, scanned_ips
        print(Fore.CYAN + "\nTERM Mode Type 'exit' to go back to the main menu.\n")
        while True:
            command = input(Fore.YELLOW + Style.BRIGHT + "TERM> " + Style.RESET_ALL).strip()
            if not command:
                continue
            cmd_lower = command.lower()
            parts = command.split()
            cmd_key = parts[0].lower() if parts else ""
            if cmd_key == "list" and len(parts) > 1:
                cmd_key = " ".join(parts[:2]).lower()
            elif cmd_key == "clear" and len(parts) > 1:
                cmd_key = " ".join(parts[:2]).lower()
            handler = self.commands.get(cmd_key, self.handle_unknown)
            if handler(parts):
                break

    def exit(self, parts):
        print(Fore.GREEN + "Returning to main menu")
        return True

    def version(self, parts):
        if len(parts) == 1 and parts[0].lower() == "version":
            print(Fore.MAGENTA + "NMAP.ARG\nVersion: 1.0.1\nCreated by p0scow")
        else:
            print(Fore.RED + "Unknown TERM command. Type 'help' for options")

    def help(self, parts):
        print(Fore.WHITE + Style.BRIGHT + " TERM commands:")
        print(Fore.GREEN + "  version")
        print(Fore.BLUE + "  list settings, list iplog")
        print(Fore.RED + "  clear, clear iplog, clear settings")
        print(Fore.YELLOW + "  autosave true/false/status")
        print(Fore.YELLOW + "  filesave true/false/status")
        print(Fore.WHITE + "  iplog true/false/status")
        print(Fore.WHITE + "  ipselect iplog [line_number]")
        print(Fore.WHITE + "  ip")
        print(Fore.MAGENTA + "  nmap")
        print(Fore.GREEN + "  help - Show this message")
        print(Fore.GREEN + "  exit - Exit TERM mode")

    def list_settings(self, parts):
        print(Fore.LIGHTBLUE_EX + f"\nFile Saving: {'On' if file_saving else 'Off'}")
        print(Fore.LIGHTBLUE_EX + f"Auto Save: {'On' if auto_save else 'Off'}")
        print(Fore.LIGHTBLUE_EX + f"IP Logging: {'On' if ip_log else 'Off'}")

    def list_iplog(self, parts):
        if os.path.exists(ip_log_file):
            try:
                with open(ip_log_file, "r") as f:
                    lines = [line.strip() for line in f if line.strip()]
                if lines:
                    print(Fore.BLUE + "\nLogged IPs:")
                    for idx, ip in enumerate(lines, 1):
                        print(Fore.BLUE + f" {idx}. {ip}")
                else:
                    print(Fore.YELLOW + "IP log is empty.")
            except IOError:
                print(Fore.RED + f"Error reading {ip_log_file}.")
        else:
            print(Fore.RED + "No IP log file found.")

    def clear(self, parts):
        if len(parts) == 1 and parts[0].lower() == "clear":
            os.system('cls' if os.name == 'nt' else 'clear')
            print(Fore.YELLOW + "TERM>")
        elif len(parts) == 2 and parts[0].lower() == "clear" and parts[1].lower() == "settings":
            try:
                with open(custom_settings_file, "w") as f:
                    f.write("autosave false\nfilesaving true\niplog true\n")
                load_settings()
                print(Fore.GREEN + "Settings reset to default.")
            except IOError:
                print(Fore.RED + f"Error resetting {custom_settings_file}")
        elif len(parts) == 2 and parts[1].lower() == "iplog":
            try:
                if os.path.exists(ip_log_file):
                    with open(ip_log_file, "w") as f:
                        pass
                    scanned_ips.clear()
                    print(Fore.GREEN + "iplog.txt has been cleared.")
                else:
                    print(Fore.RED + "iplog.txt not found.")
            except IOError:
                print(Fore.RED + f"Error clearing {ip_log_file}")
        else:
            print(Fore.RED + "Invalid clear syntax")

    def autosave(self, parts):
        self.setting(parts, "autosave")

    def filesave(self, parts):
        self.setting(parts, "filesave")

    def iplog(self, parts):
        self.setting(parts, "iplog")

    def setting(self, parts, setting_type):
        if len(parts) != 2:
            print(Fore.RED + f"Invalid {setting_type} syntax")
            return
        action = parts[1].lower()
        if action in ["true", "false"]:
            if setting_type == "autosave" and action == "true" and not file_saving:
                print(Fore.RED + "Cannot enable autosave while file saving is disabled.")
            elif setting_type == "filesave" and action == "false" and auto_save:
                print(Fore.RED + "Disable auto-save first before disabling file saving.")
            else:
                try:
                    save_setting(f"{setting_type} {action}")
                    load_settings()
                    status = "On" if action == "true" else "Off"
                    print(Fore.LIGHTBLUE_EX + f"{setting_type.capitalize()} set to: {status}")
                except IOError:
                    print(Fore.RED + f"Error saving to {custom_settings_file}.")
        elif action == "status":
            status = {"autosave": auto_save, "filesave": file_saving, "iplog": ip_log}[setting_type]
            print(Fore.LIGHTBLUE_EX + f"{setting_type.capitalize()} is {'enabled' if status else 'disabled'}.")
        else:
            print(Fore.RED + "Invalid syntax")

    def ipselect(self, parts):
        if len(parts) != 3 or not parts[2].isdigit():
            print(Fore.RED + "Invalid syntax" if len(parts) != 3 else "Use an integer.")
            return
        line_num = int(parts[2])
        if not os.path.exists(ip_log_file):
            print(Fore.RED + "ip_log.txt file not found.")
            return
        try:
            with open(ip_log_file, "r") as f:
                lines = [line.strip() for line in f if line.strip()]
            if line_num < 1 or line_num > len(lines):
                print(Fore.RED + f"Invalid entry. ip_log.txt has {len(lines)} entries.")
            else:
                global current_ip
                current_ip = lines[line_num - 1]
                print(Fore.GREEN + f"Selected IP set to: {current_ip}")
        except IOError:
            print(Fore.RED + f"Error reading {ip_log_file}.")

    def ip(self, parts):
        print(Fore.BLUE + f"Current selected IP: {current_ip}" if current_ip else Fore.YELLOW + "No IP selected.")

    def nmap(self, parts):
        if current_ip:
            run_scan(parts[1:] + [current_ip])
        else:
            print(Fore.RED + "Select an IP first.")

    def handle_unknown(self, parts):
        print(Fore.RED + "Unknown TERM command. Type 'help' for options")

if __name__ == "__main__":
    load_settings()
    print_banner()

    while True:
        displaymenu()
        user_choice = input(Fore.WHITE + "\nEnter your choice (1-9): ").strip()
        NMAPexecute(user_choice)