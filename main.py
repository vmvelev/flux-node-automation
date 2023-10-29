import json
import os
import subprocess
from paramiko import SSHClient, AutoAddPolicy
from paramiko.ssh_exception import SSHException
from paramiko.rsakey import RSAKey
import getpass


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
        try:
            commands = [
                "sudo apt-get update -y",
                "sudo apt-get --with-new-pkgs upgrade -y && sudo apt autoremove -y && cd && cd zelflux && git checkout . && git checkout master && git reset --hard origin/master && git pull",
                "sudo reboot",
            ]
            if server.get("use_key", False):
                try:
                    # Attempt to load the key without a passphrase
                    pkey = RSAKey(filename="./keys/id_rsa")
                except SSHException:
                    # If loading fails, it might be encrypted. Prompt for passphrase and try again.
                    passphrase = getpass.getpass(
                        "Enter the passphrase for the private key: "
                    )
                    pkey = RSAKey(filename="./keys/id_rsa", password=passphrase)

                ssh.connect(
                    server["ip"],
                    username=server["username"],
                    pkey=pkey,  # Use the unlocked private key
                )
                execute_commands(ssh, commands)
            else:
                ssh.connect(
                    server["ip"],
                    username=server["username"],
                    password=server["password"],
                )
                execute_commands(ssh, commands)
        except Exception as e:
            print(f"Failed to connect to {server['ip']}. Reason: {str(e)}")


def restartNode(server):
    with SSHClient() as ssh:
        try:
            ssh.set_missing_host_key_policy(AutoAddPolicy())
            commands = ["sudo reboot"]
            # Determine the method of authentication
            if server.get("use_key", False):
                try:
                    # Attempt to load the key without a passphrase
                    pkey = RSAKey(filename="./keys/id_rsa")
                except SSHException:
                    # If loading fails, it might be encrypted. Prompt for passphrase and try again.
                    passphrase = getpass.getpass(
                        "Enter the passphrase for the private key: "
                    )
                    pkey = RSAKey(filename="./keys/id_rsa", password=passphrase)

                ssh.connect(
                    server["ip"],
                    username=server["username"],
                    pkey=pkey,  # Use the unlocked private key
                )
                execute_commands(ssh, commands)
            else:
                ssh.connect(
                    server["ip"],
                    username=server["username"],
                    password=server["password"],
                )
                execute_commands(ssh, commands)
        except Exception as e:
            print(f"Failed to connect to {server['ip']}. Reason: {str(e)}")


def test_connection(server):
    """Test the connection to a given server."""
    with SSHClient() as ssh:
        try:
            ssh.set_missing_host_key_policy(AutoAddPolicy())

            # Determine the method of authentication
            if server.get("use_key", False):
                try:
                    # Attempt to load the key without a passphrase
                    pkey = RSAKey(filename="./keys/id_rsa")
                except SSHException:
                    # If loading fails, it might be encrypted. Prompt for passphrase and try again.
                    passphrase = getpass.getpass(
                        "Enter the passphrase for the private key: "
                    )
                    pkey = RSAKey(filename="./keys/id_rsa", password=passphrase)

                ssh.connect(
                    server["ip"],
                    username=server["username"],
                    pkey=pkey,  # Use the unlocked private key
                )
            else:
                ssh.connect(
                    server["ip"],
                    username=server["username"],
                    password=server["password"],
                )

            print(f"Successfully connected to {server['ip']}!")
        except Exception as e:
            print(f"Failed to connect to {server['ip']}. Reason: {str(e)}")


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
        print("4. Test connection")
        print("5. Exit")
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
            target_choice = input("Do you want to target a (1) Server or a (2) Group? ")

            if target_choice == "1":
                selected_options = get_selected_servers(config["servers"])
                for server in selected_options:
                    test_connection(server)
            elif target_choice == "2":
                selected_group_names = get_selected_groups(config["groups"])
                selected_servers = get_servers_from_groups(config, selected_group_names)
                for server in selected_servers:
                    test_connection(server)

        elif choice == "5":
            print("Exiting.")
            break


if __name__ == "__main__":
    main()
