import json
import os
import subprocess
from paramiko import SSHClient, AutoAddPolicy


def list_servers_to_choose(options):
    for idx, option in enumerate(options, start=1):
        # Check if the option is a group or a server
        if isinstance(option, dict):  # It's a server
            if "nickname" in option:
                display_name = f"{option['nickname']} ({option['ip']})"
            else:
                display_name = option["ip"]
        else:  # It's a group
            display_name = f"Group: {option}"

        print(f"{idx}. {display_name}")


def get_selected_servers(servers):
    for idx, server in enumerate(servers, start=1):
        if "nickname" in server:
            display_name = f"{server['nickname']} ({server['ip']})"
        else:
            display_name = server["ip"]
        print(f"{idx}. {display_name}")

    selected_indices = input(
        "Select servers by typing their numbers separated by spaces: "
    ).split()
    return [
        servers[int(idx) - 1]
        for idx in selected_indices
        if idx.isdigit() and 1 <= int(idx) <= len(servers)
    ]


def execute_commands(ssh, commands):
    for command in commands:
        stdin, stdout, stderr = ssh.exec_command(command)
        print(stdout.read().decode())
        stdin.close()
        stdout.close()
        stderr.close()


def updateFluxNode(server):
    with SSHClient() as ssh:
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(
            server["ip"], username=server["username"], password=server["password"]
        )
        commands = [
            "sudo apt-get update -y",
            "sudo apt-get --with-new-pkgs upgrade -y && sudo apt autoremove -y && cd && cd zelflux && git checkout . && git checkout master && git reset --hard origin/master && git pull",
            "sudo reboot",
        ]
        execute_commands(ssh, commands)


def restartNode(server):
    with SSHClient() as ssh:
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(
            server["ip"], username=server["username"], password=server["password"]
        )
        commands = ["sudo reboot"]
        execute_commands(ssh, commands)


def get_servers_from_groups(config, group_names):
    """Return servers based on selected group names."""
    selected_servers = []
    for group_name in group_names:
        for ip in config["groups"].get(group_name, []):
            server = next((s for s in config["servers"] if s["ip"] == ip), None)
            if server:
                selected_servers.append(server)
    return selected_servers


def get_selected_groups(groups):
    for idx, group_name in enumerate(groups, start=1):
        print(f"{idx}. Group: {group_name}")

    selected_indices = input(
        "Select groups by typing their numbers separated by spaces: "
    ).split()
    return [
        list(groups.keys())[int(idx) - 1]
        for idx in selected_indices
        if idx.isdigit() and 1 <= int(idx) <= len(groups)
    ]


def main():
    # Check if config.txt exists, if not, run config.py
    if not os.path.exists("config.txt"):
        subprocess.run(
            ["python", "config.py"]
        )  # Use "python3" if that's the appropriate command on your system

    # If config.txt still doesn't exist after config.py (e.g. user cancelled), exit
    if not os.path.exists("config.txt"):
        print("No server configurations found. Exiting.")
        exit()

    # Load the servers from config.txt
    with open("config.txt", "r") as infile:
        config = json.load(infile)

    if not config["servers"]:
        print("No server configurations found. Please run config.py first.")
        exit()

    # Let's assume you want to connect to the first server in the list
    # You can modify this part as per your requirement
    while True:
        print("What do you want to do?")
        print("1. Update node")
        print("2. Restart node")
        print("3. Update server list")
        print("4. Exit")
        choice = input("Enter your choice: ")

        if choice in ["1", "2"]:
            # Ask if they want to execute for a server or a group
            target_choice = input("Do you want to target a (1) Server or a (2) Group? ")

            if target_choice == "1":
                # Only servers are displayed for selection
                selected_options = get_selected_servers(config["servers"])
            elif target_choice == "2":
                # Only groups are displayed for selection
                selected_options = get_selected_groups(config["groups"])

            if target_choice == "1":
                for server in selected_options:
                    if choice == "1":
                        updateFluxNode(server)
                    elif choice == "2":
                        restartNode(server)
            elif target_choice == "2":
                for group_name in selected_options:
                    for server_ip in config["groups"][group_name]:
                        server = next(
                            (s for s in config["servers"] if s["ip"] == server_ip), None
                        )
                        if server:
                            if choice == "1":
                                updateFluxNode(server)
                            elif choice == "2":
                                restartNode(server)
        elif choice == "3":
            subprocess.run(["python", "config.py"])
        elif choice == "4":
            print("Exiting.")
            break


if __name__ == "__main__":
    main()
