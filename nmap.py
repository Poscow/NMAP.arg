import os
import sys
import time
import subprocess
import ipaddress
from colorama import Fore, Style, init

init(autoreset=True)

# Globals
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
    os.system('cls' if os.name == 'nt' else 'clear')  # Clear terminal screen

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
    global file_saving, ip_log, auto_save

    # Default settings
    default_settings = [
        "autosave false",
        "filesaving true",
        "iplog true"
    ]

    if not os.path.exists(custom_settings_file):
        with open(custom_settings_file, "w") as f:
            f.write("\n".join(default_settings) + "\n")

    # Load settings
    file_saving = True
    auto_save = False
    ip_log = True

    with open(custom_settings_file, "r") as f:
        for line in f:
            line = line.strip().lower()
            if line == "autosave true":
                auto_save = True
            elif line == "autosave false":
                auto_save = False
            elif line == "filesaving true":
                file_saving = True
            elif line == "filesaving false":
                file_saving = False
            elif line == "iplog true":
                ip_log = True
            elif line == "iplog false":
                ip_log = False

    # Make sure auto_save can't be true if file_saving is false
    if auto_save and not file_saving:
        auto_save = False
        save_setting("autosave false")

def spinner_process(proc):
    spinner = ['|', '/', '-', '\\']
    idx = 0
    while proc.poll() is None:
        print(Fore.YELLOW + spinner[idx % len(spinner)], end='\r')
        idx += 1
        time.sleep(0.1)

def run_scan(args):
    global auto_save, file_saving
    try:
        proc = subprocess.Popen(["nmap"] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        spinner_process(proc)
        output, _ = proc.communicate()
        print(Fore.WHITE + output)

        if file_saving:
            if auto_save:
                out_path = os.path.join(logs_dir, f"nmap_scan_{int(time.time())}.txt")
                with open(out_path, "w", encoding='utf-8') as f:
                    f.write(output)
                print(Fore.GREEN + f"Output auto-saved to {out_path}.")
            else:
                save = input(Fore.CYAN + "\nDo you want to save this output to a text file in the logs folder? (y/n): ").strip().lower()
                if save == 'y':
                    out_path = os.path.join(logs_dir, f"nmap_scan_{int(time.time())}.txt")
                    with open(out_path, "w", encoding='utf-8') as f:
                        f.write(output)
                    print(Fore.GREEN + f"Output saved to {out_path}.")
    except FileNotFoundError:
        print(Fore.RED + "Nmap is not installed or not in system PATH.")

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
    if os.path.exists(ip_log_file):
        with open(ip_log_file, "r") as f:
            for line in f:
                scanned_ips.add(line.strip())
    if ip not in scanned_ips:
        with open(ip_log_file, "a") as f:
            f.write(ip + "\n")
        scanned_ips.add(ip)

def select_ip_from_log(index):
    global current_ip
    if not os.path.exists(ip_log_file):
        print(Fore.RED + "ip_log.txt does not exist.")
        return
    with open(ip_log_file, "r") as f:
        lines = [line.strip() for line in f if line.strip()]
    if not lines:
        print(Fore.RED + "ip_log.txt is empty.")
        return
    if index < 1 or index > len(lines):
        print(Fore.RED + f"Index {index} out of range. There are {len(lines)} IPs logged.")
        return
    selected_ip = lines[index-1]
    try:
        ipaddress.IPv4Address(selected_ip)
        current_ip = selected_ip
        print(Fore.GREEN + f"Selected IP from log: {current_ip}")
    except ipaddress.AddressValueError:
        print(Fore.RED + "Invalid IP found in ip_log.txt")

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

def show_help(command=None):
    very_light_blue = Fore.LIGHTBLUE_EX
    blue = Fore.BLUE
    red = Fore.RED
    green = Fore.GREEN

    if command is None:
        print(green + "Available main TERM commands:")
        print(f"{blue}list settings{Style.RESET_ALL} - Show all current settings")
        print(f"{blue}list iplog{Style.RESET_ALL} - Show all logged IPs")
        print(f"{red}clear{Style.RESET_ALL} - Clears the terminal screen")
        print(f"{red}clear iplog{Style.RESET_ALL} - Clears the logged IPs in ip_log.txt")
        print(f"{red}clear settings{Style.RESET_ALL} - Resets custom settings to default")
        print(f"{blue}iplog true/false/status/help{Style.RESET_ALL} - Manage IP logging")
        print(f"{very_light_blue}autosave true/false/status/help{Style.RESET_ALL} - Manage auto-save setting")
        print(f"{very_light_blue}filesaving true/false/status/help{Style.RESET_ALL} - Manage file-saving prompts")
        print(f"{blue}ip select ip_log.txt <number>{Style.RESET_ALL} - Select IP from ip_log.txt by line number")
        print(f"{green}help{Style.RESET_ALL} - Show this help message")
        return

    cmd = command.lower()
    if cmd == "list settings":
        print(very_light_blue + "list settings commands:")
        print("  list settings           - Show current file saving and autosave status")
        print("  list settings help      - Show this help message")
    elif cmd == "list iplog":
        print(blue + "list iplog commands:")
        print("  list iplog              - Show all logged IPs")
        print("  list iplog help         - Show this help message")
    elif cmd == "clear":
        print(red + "clear commands:")
        print("  clear                   - Clears the terminal screen")
        print("  clear help              - Show this help message")
    elif cmd == "clear iplog":
        print(red + "clear iplog commands:")
        print("  clear iplog             - Clears the logged IPs in ip_log.txt")
        print("  clear iplog help        - Show this help message")
    elif cmd == "clear settings":
        print(red + "clear settings commands:")
        print("  clear settings          - Resets custom settings to default")
        print("  clear settings help     - Show this help message")
    elif cmd == "iplog":
        print(blue + "iplog commands:")
        print("  iplog true              - Enable IP logging")
        print("  iplog false             - Disable IP logging")
        print("  iplog status            - Show current IP logging status")
        print("  iplog help              - Show this help message")
    elif cmd == "autosave":
        print(very_light_blue + "autosave commands:")
        print("  autosave true           - Enable auto-save (requires filesaving true)")
        print("  autosave false          - Disable auto-save")
        print("  autosave status         - Show current auto-save status")
        print("  autosave help           - Show this help message")
    elif cmd == "filesaving":
        print(very_light_blue + "filesaving commands:")
        print("  filesaving true         - Enable file-saving prompts")
        print("  filesaving false        - Disable file-saving prompts")
        print("  filesaving status       - Show current file saving status")
        print("  filesaving help         - Show this help message")
    else:
        print(Fore.RED + f"No help available for '{command}'")

def term_mode():
    print(Fore.CYAN + "\nEntering TERM mode. Type 'exit' to return to main menu or 'help' to display a list of commands.\n")
    while True:
        command = input(Fore.YELLOW + "@TERM> " + Style.RESET_ALL).strip()
        cmd_lower = command.lower()

        if cmd_lower == "exit":
            break

        elif cmd_lower == "help":
            print(Fore.GREEN + "Available TERM commands:")
            print(Fore.BLUE + "  list settings/status/help  - Show current settings info")
            print(Fore.BLUE + "  list iplog/status/help     - Show logged IPs info")
            print(Fore.RED + "  clear                      - Clear the terminal")
            print(Fore.RED + "  clear iplog                - Clear logged IPs")
            print(Fore.RED + "  clear settings             - Reset settings to default")
            print(Fore.LIGHTBLUE_EX + "  autosave true/false/status/help - Manage auto-save")
            print(Fore.LIGHTBLUE_EX + "  iplog true/false/status/help    - Manage IP logging")
            print(Fore.BLUE + "  ip select ip_log.txt <num> - Select IP from ip_log.txt")
            print(Fore.BLUE + "  nmap <args>                - Run nmap with arguments\n")

        elif cmd_lower.startswith("autosave "):
            parts = cmd_lower.split()
            if len(parts) == 2:
                if parts[1] == "true":
                    if not file_saving:
                        print(Fore.RED + "Cannot enable autosave while file saving is disabled.")
                    else:
                        save_setting("autosave true")
                        load_settings()
                        print(Fore.LIGHTBLUE_EX + "Auto-save enabled.")
                elif parts[1] == "false":
                    save_setting("autosave false")
                    load_settings()
                    print(Fore.LIGHTBLUE_EX + "Auto-save disabled.")
                elif parts[1] == "status":
                    print(Fore.LIGHTBLUE_EX + f"Auto-save is {'enabled' if auto_save else 'disabled'}.")
                elif parts[1] == "help":
                    print(Fore.LIGHTBLUE_EX + "AUTOSAVE commands:")
                    print("  autosave true     - Enable auto-save (requires file saving on)")
                    print("  autosave false    - Disable auto-save")
                    print("  autosave status   - Show current auto-save status")
                    print("  autosave help     - Show this help message")
                else:
                    print(Fore.RED + "Unknown autosave command. Use 'autosave help' for info.")
            else:
                print(Fore.RED + "Invalid autosave syntax. Use 'autosave help' for info.")

        elif cmd_lower.startswith("iplog "):
            parts = cmd_lower.split()
            if len(parts) == 2:
                if parts[1] == "true":
                    save_setting("iplog true")
                    load_settings()
                    print(Fore.LIGHTBLUE_EX + "IP logging enabled.")
                elif parts[1] == "false":
                    save_setting("iplog false")
                    load_settings()
                    print(Fore.LIGHTBLUE_EX + "IP logging disabled.")
                elif parts[1] == "status":
                    print(Fore.LIGHTBLUE_EX + f"IP logging is {'enabled' if ip_log else 'disabled'}.")
                elif parts[1] == "help":
                    print(Fore.LIGHTBLUE_EX + "IPLOG commands:")
                    print("  iplog true     - Enable IP logging")
                    print("  iplog false    - Disable IP logging")
                    print("  iplog status   - Show current IP logging status")
                    print("  iplog help     - Show this help message")
                else:
                    print(Fore.RED + "Unknown iplog command. Use 'iplog help' for info.")
            else:
                print(Fore.RED + "Invalid iplog syntax. Use 'iplog help' for info.")

        elif cmd_lower == "list settings":
            print(Fore.BLUE + "\nCurrent Settings:")
            print(Fore.LIGHTBLUE_EX + f"  File Saving: {'On' if file_saving else 'Off'}")
            print(Fore.LIGHTBLUE_EX + f"  Auto Save: {'On' if auto_save else 'Off'}")
            print(Fore.LIGHTBLUE_EX + f"  IP Logging: {'On' if ip_log else 'Off'}")

        elif cmd_lower == "list iplog":
            if os.path.exists(ip_log_file):
                with open(ip_log_file, "r") as f:
                    lines = [line.strip() for line in f if line.strip()]
                if lines:
                    print(Fore.BLUE + "\nLogged IPs:")
                    for i, ip in enumerate(lines, 1):
                        print(Fore.LIGHTBLUE_EX + f"  {i}. {ip}")
                else:
                    print(Fore.YELLOW + "IP log is empty.")
            else:
                print(Fore.RED + "No IP log file found.")

        elif cmd_lower == "clear":
            os.system('cls' if os.name == 'nt' else 'clear')
            print(Fore.YELLOW + "TERM>")

        elif cmd_lower == "clear iplog":
            if os.path.exists(ip_log_file):
                with open(ip_log_file, "w") as f:
                    pass
                scanned_ips.clear()
                print(Fore.RED + "ip_log.txt has been cleared.")
            else:
                print(Fore.RED + "ip_log.txt not found.")

        elif cmd_lower == "clear settings":
            with open(custom_settings_file, "w") as f:
                f.write("autosave true\niplog true\n")
            load_settings()
            print(Fore.RED + "Settings reset to default.")

        elif cmd_lower.startswith("list "):
            if cmd_lower == "list settings help":
                print(Fore.BLUE + "list settings - Shows current file saving, autosave, and IP logging status.")
                print("list settings help - Shows this help message.")
            elif cmd_lower == "list iplog help":
                print(Fore.BLUE + "list iplog - Lists all logged IP addresses.")
                print("list iplog help - Shows this help message.")
            else:
                print(Fore.RED + "Unknown list command. Type 'help' for options.")

        elif cmd_lower.startswith("clear "):
            if cmd_lower == "clear help":
                print(Fore.RED + "Clear Commands:")
                print("  clear           - Clears the terminal screen.")
                print("  clear iplog     - Clears the IP log file.")
                print("  clear settings  - Resets settings to default.")
                print("  clear help      - Shows this help message.")
            elif cmd_lower == "clear iplog help":
                print(Fore.RED + "clear iplog - Clears all logged IPs from ip_log.txt.")
            elif cmd_lower == "clear settings help":
                print(Fore.RED + "clear settings - Resets nmap_custom_settings.txt to default.")
            else:
                print(Fore.RED + "Unknown clear command. Type 'help' for options.")

        elif cmd_lower.startswith("ip select ip_log.txt "):
            parts = command.split()
            if len(parts) == 4 and parts[2] == "ip_log.txt":
                try:
                    index = int(parts[3]) - 1
                    if not os.path.exists(ip_log_file):
                        print(Fore.RED + "ip_log.txt not found.")
                        continue
                    with open(ip_log_file, "r") as f:
                        lines = [line.strip() for line in f if line.strip()]
                    if 0 <= index < len(lines):
                        global current_ip
                        current_ip = lines[index]
                        print(Fore.GREEN + f"Selected IP: {current_ip}")
                        if ip_log:
                            log_ip(current_ip)
                    else:
                        print(Fore.RED + "Index out of range.")
                except ValueError:
                    print(Fore.RED + "Invalid index number.")
            else:
                print(Fore.RED + "Invalid command syntax. Use: ip select ip_log.txt <number>")

        elif cmd_lower.startswith("nmap "):
            # Run nmap command directly with args
            args = command.split()[1:]
            if not current_ip:
                print(Fore.RED + "No IP selected. Use option 1 or 'ip select ip_log.txt <number>' to select an IP.")
                continue
            # Append the current_ip if not already in args
            if current_ip not in args:
                args.append(current_ip)
            run_scan(args)

        elif cmd_lower == "":
            # Ignore empty input (just enter)
            continue

        else:
            print(Fore.RED + "Unknown TERM command. Type 'help' for options.")



if __name__ == "__main__":
    load_settings()
    print_banner()

    while True:
        display_menu()
        user_choice = input(Fore.WHITE + "\nEnter your choice (1-9): ").strip()
        execute_nmap(user_choice)
