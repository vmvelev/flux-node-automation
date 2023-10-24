import json
import os
import subprocess
from paramiko import SSHClient, AutoAddPolicy
from prompt_toolkit.shortcuts import checkboxlist_dialog


def list_servers_to_choose(servers):
    for idx, server in enumerate(servers, start=1):
        if "nickname" in server:
            display_name = f"{server['nickname']} ({server['ip']})"
        else:
            display_name = server["ip"]
        print(f"{idx}. {display_name}")


def get_selected_servers(servers):
    choices = [
        (
            server,
            server.get("nickname", server["ip"])
            if "nickname" in server
            else server["ip"],
        )
        for server in servers
    ]

    selected_servers = checkboxlist_dialog(
        title="Select servers",
        text="Use arrow keys to navigate and spacebar to select:",
        values=choices,
    ).run()

    return selected_servers


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
        servers = json.load(infile)

    if not servers:
        print("No server configurations found. Please run config.py first.")
        exit()

    # Let's assume you want to connect to the first server in the list
    # You can modify this part as per your requirement
    while True:
        print("What do you want to do?")
        print("1. Update node")
        print("2. Restart node")
        print("3. Cancel")
        choice = input("Enter your choice: ")

        if choice in ["1", "2"]:
            selected_servers = get_selected_servers(servers)
            for server in selected_servers:
                if choice == "1":
                    updateFluxNode(server)
                elif choice == "2":
                    restartNode(server)
        elif choice == "3":
            print("Exiting.")
            break


if __name__ == "__main__":
    main()
