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

# Ensure directories exist
os.makedirs(config_dir, exist_ok=True)
os.makedirs(logs_dir, exist_ok=True)
custom_settings_file = os.path.join(config_dir, "nmap_custom_settings.txt")
ip_log_file = os.path.join(logs_dir, "ip_log.txt")

def print_banner():
    os.system('cls' if os.name == 'nt' else 'clear')  # Clear screen

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

    print(Fore.WHITE + "\nNMAP.ARG created by " + Fore.GREEN + "p0scow" + Fore.WHITE + "\n")

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

    # Default settings
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
    global scanned_ips
    if os.path.exists(ip_log_file):
        with open(ip_log_file, "r") as f:
            for line in f:
                scanned_ips.add(line.strip())
    if ip not in scanned_ips:
        with open(ip_log_file, "a") as f:
            f.write(ip + "\n")
        scanned_ips.add(ip)

def display_menu():
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
    print("6. Ultra Aggressive Scan")
    print("7. Scan for Services")
    print("8. TERM - Custom Settings Terminal")
    print("9. Exit")

def execute_nmap(choice):
    global current_ip
    if choice == '1':
        user_int()
    elif choice == '8':
        term_mode()
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
            '5': ['-A'],
            '6': ['-AA'],
            '7': ['-sV']
        }

        if choice in commands:
            run_scan(commands[choice] + [current_ip])
        else:
            print(Fore.RED + "Invalid option.")

def term_mode(): #\\Not sure what to do with this because I made it so long now and it's getting too big//#
    global current_ip, file_saving, auto_save, ip_log, scanned_ips
    print(Fore.CYAN + "\nEntering TERM mode. Type 'exit' to return to main menu.\n")
    while True:
        command = input(Fore.YELLOW + "TERM> " + Style.RESET_ALL).strip()
        if command == "":
            continue

        cmd_lower = command.lower()

        # EXIT
        if cmd_lower == "exit":
            break

        # VERSION
        elif cmd_lower == "version":
            print(Fore.MAGENTA + "NMAP.ARG Terminal Emulator")
            print(Fore.MAGENTA + "Version: 1.0.0")
            print(Fore.MAGENTA + "Created by p0scow")
            print(Fore.MAGENTA + "Custom TERM command - shows version info")

        # HELP
        elif cmd_lower == "help":
            print(Fore.GREEN + "Available TERM commands:")
            print(Fore.BLUE + "  version")
            print(Fore.BLUE + "  list settings, list iplog, list settings help, list iplog help")
            print(Fore.RED + "  clear, clear iplog, clear settings, clear help, clear iplog help, clear settings help")
            print(Fore.LIGHTBLUE_EX + "  autosave true/false/status/help")
            print(Fore.LIGHTBLUE_EX + "  filesaving true/false/status/help")
            print(Fore.BLUE + "  iplog true/false/status/help")
            print(Fore.BLUE + "  ip select ip_log.txt [line_number]")
            print(Fore.BLUE + "  ip")
            print(Fore.BLUE + "  nmap [nmap options]")
            print(Fore.GREEN + "  help - Show this message")
            print(Fore.GREEN + "  exit - Exit TERM mode")

        # LIST SETTINGS
        elif cmd_lower.startswith("list settings"):
            if cmd_lower == "list settings":
                print(Fore.LIGHTBLUE_EX + f"\nFile Saving: {'On' if file_saving else 'Off'}")
                print(Fore.LIGHTBLUE_EX + f"Auto Save: {'On' if auto_save else 'Off'}")
                print(Fore.LIGHTBLUE_EX + f"IP Logging: {'On' if ip_log else 'Off'}")
            elif cmd_lower == "list settings help":
                print(Fore.LIGHTBLUE_EX + "list settings - Show current file saving, autosave, and ip logging status")
                print(Fore.LIGHTBLUE_EX + "list settings help - Show this help message")

        # LIST IPLOG
        elif cmd_lower.startswith("list iplog"):
            if cmd_lower == "list iplog":
                if os.path.exists(ip_log_file):
                    with open(ip_log_file, "r") as f:
                        lines = [line.strip() for line in f if line.strip()]
                    if lines:
                        print(Fore.BLUE + "\nLogged IPs:")
                        for idx, ip in enumerate(lines, 1):
                            print(Fore.BLUE + f" {idx}. {ip}")
                    else:
                        print(Fore.YELLOW + "IP log is empty.")
                else:
                    print(Fore.RED + "No IP log file found.")
            elif cmd_lower == "list iplog help":
                print(Fore.BLUE + "list iplog - Show all logged IPs")
                print(Fore.BLUE + "list iplog help - Show this help message")

        # CLEAR COMMANDS
        elif cmd_lower.startswith("clear"):
            if cmd_lower == "clear":
                os.system('cls' if os.name == 'nt' else 'clear')
                print(Fore.YELLOW + "TERM>")
            elif cmd_lower == "clear help":
                print(Fore.RED + "clear - Clears the terminal screen")
                print(Fore.RED + "clear iplog - Clears the ip_log.txt file")
                print(Fore.RED + "clear settings - Resets settings to default")
                print(Fore.RED + "clear help - Shows this message")
                print(Fore.RED + "clear iplog help - Shows iplog clear help")
                print(Fore.RED + "clear settings help - Shows settings clear help")
            elif cmd_lower == "clear iplog":
                if os.path.exists(ip_log_file):
                    with open(ip_log_file, "w") as f:
                        pass  # Clear file
                    scanned_ips.clear()
                    print(Fore.GREEN + "ip_log.txt has been cleared.")
                else:
                    print(Fore.RED + "ip_log.txt not found.")
            elif cmd_lower == "clear iplog help":
                print(Fore.RED + "clear iplog - Clears the ip_log.txt file")
                print(Fore.RED + "clear iplog help - Shows this message")
            elif cmd_lower == "clear settings":
                with open(custom_settings_file, "w") as f:
                    f.write("autosave false\nfilesaving true\niplog true\n")
                load_settings()
                print(Fore.GREEN + "Settings reset to default.")
            elif cmd_lower == "clear settings help":
                print(Fore.RED + "clear settings - Resets settings to default")
                print(Fore.RED + "clear settings help - Shows this message")
            else:
                print(Fore.RED + "Unknown clear command. Type 'clear help' for options.")

        # AUTOSAVE COMMANDS
        elif cmd_lower.startswith("autosave "):
            parts = cmd_lower.split()
            if len(parts) == 2:
                if parts[1] == "true":
                    if not file_saving:
                        print(Fore.RED + "Cannot enable autosave while file saving is disabled.")
                    else:
                        save_setting("autosave true")
                        load_settings()
                        print(Fore.LIGHTBLUE_EX + "Auto-save set to: On")
                elif parts[1] == "false":
                    save_setting("autosave false")
                    load_settings()
                    print(Fore.LIGHTBLUE_EX + "Auto-save set to: Off")
                elif parts[1] == "status":
                    print(Fore.LIGHTBLUE_EX + f"Auto-save is {'enabled' if auto_save else 'disabled'}.")
                elif parts[1] == "help":
                    print(Fore.LIGHTBLUE_EX + "autosave commands:")
                    print(Fore.LIGHTBLUE_EX + "  autosave true    - Enable auto-save (requires file saving ON)")
                    print(Fore.LIGHTBLUE_EX + "  autosave false   - Disable auto-save")
                    print(Fore.LIGHTBLUE_EX + "  autosave status  - Show auto-save status")
                    print(Fore.LIGHTBLUE_EX + "  autosave help    - Show this help message")
                else:
                    print(Fore.RED + "Unknown autosave command.")
            else:
                print(Fore.RED + "Invalid autosave syntax. Use 'autosave help'.")

        # FILE SAVING COMMANDS
        elif cmd_lower.startswith("filesaving "):
            parts = cmd_lower.split()
            if len(parts) == 2:
                if parts[1] == "true":
                    save_setting("filesaving true")
                    load_settings()
                    print(Fore.LIGHTBLUE_EX + "File saving set to: On")
                elif parts[1] == "false":
                    if auto_save:
                        print(Fore.RED + "Disable auto-save first before disabling file saving.")
                    else:
                        save_setting("filesaving false")
                        load_settings()
                        print(Fore.LIGHTBLUE_EX + "File saving set to: Off")
                elif parts[1] == "status":
                    print(Fore.LIGHTBLUE_EX + f"File saving is {'enabled' if file_saving else 'disabled'}.")
                elif parts[1] == "help":
                    print(Fore.LIGHTBLUE_EX + "filesaving commands:")
                    print(Fore.LIGHTBLUE_EX + "  filesaving true    - Enable file saving prompts")
                    print(Fore.LIGHTBLUE_EX + "  filesaving false   - Disable file saving prompts")
                    print(Fore.LIGHTBLUE_EX + "  filesaving status  - Show file saving status")
                    print(Fore.LIGHTBLUE_EX + "  filesaving help    - Show this help message")
                else:
                    print(Fore.RED + "Unknown filesaving command.")
            else:
                print(Fore.RED + "Invalid filesaving syntax. Use 'filesaving help'.")

        # IPLOG COMMANDS
        elif cmd_lower.startswith("iplog "):
            parts = cmd_lower.split()
            if len(parts) == 2:
                if parts[1] == "true":
                    save_setting("iplog true")
                    load_settings()
                    print(Fore.BLUE + "IP logging set to: On")
                elif parts[1] == "false":
                    save_setting("iplog false")
                    load_settings()
                    print(Fore.BLUE + "IP logging set to: Off")
                elif parts[1] == "status":
                    print(Fore.BLUE + f"IP logging is {'enabled' if ip_log else 'disabled'}.")
                elif parts[1] == "help":
                    print(Fore.BLUE + "iplog commands:")
                    print(Fore.BLUE + "  iplog true    - Enable IP logging")
                    print(Fore.BLUE + "  iplog false   - Disable IP logging")
                    print(Fore.BLUE + "  iplog status  - Show IP logging status")
                    print(Fore.BLUE + "  iplog help    - Show this help message")
                else:
                    print(Fore.RED + "Unknown iplog command.")
            else:
                print(Fore.RED + "Invalid iplog syntax. Use 'iplog help'.")

        # IP SELECT COMMAND
        elif cmd_lower.startswith("ip select ip_log.txt"):
            parts = command.split()
            if len(parts) == 4:
                line_num_str = parts[3]
                if not line_num_str.isdigit():
                    print(Fore.RED + "Invalid line number. Use an integer.")
                else:
                    line_num = int(line_num_str)
                    if not os.path.exists(ip_log_file):
                        print(Fore.RED + "ip_log.txt file not found.")
                    else:
                        with open(ip_log_file, "r") as f:
                            lines = [line.strip() for line in f if line.strip()]
                        if line_num < 1 or line_num > len(lines):
                            print(Fore.RED + f"Line number out of range. ip_log.txt has {len(lines)} entries.")
                        else:
                            current_ip = lines[line_num - 1]
                            print(Fore.GREEN + f"Selected IP set to: {current_ip}")
            else:
                print(Fore.RED + "Invalid syntax. Usage: ip select ip_log.txt [line_number]")

        # SHOW CURRENT IP
        elif cmd_lower == "ip":
            if current_ip:
                print(Fore.BLUE + f"Current selected IP: {current_ip}")
            else:
                print(Fore.YELLOW + "No IP selected.")

        # DIRECT NMAP COMMAND
        elif cmd_lower.startswith("nmap "):
            # Check if IP is selected
            args = command.split()[1:]
            if not current_ip:
                print(Fore.RED + "Please select an IP first (use 'ip' or option 1 from main menu).")
            else:
                run_scan(args + [current_ip])

        else:
            print(Fore.RED + "Unknown TERM command. Type 'help' for options.")

if __name__ == "__main__":
    load_settings()
    print_banner()

    while True:
        display_menu()
        user_choice = input(Fore.WHITE + "\nEnter your choice (1-9): ").strip()
        execute_nmap(user_choice)
