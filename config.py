import json
import os
from paramiko import SSHClient, AutoAddPolicy
import subprocess


def ask_server_details():
    ip = input("Which is the IP you want to connect to? ")
    username = input("What is the username for that server? ")
    nickname = input("What is the nickname that you want to give to this server? ")

    auth_details = ask_authentication_details()

    if auth_details["type"] == "password":
        return {
            "ip": ip,
            "username": username,
            "password": auth_details["password"],
            "nickname": nickname,
        }
    elif auth_details["type"] == "key":
        return {
            "ip": ip,
            "username": username,
            "password": auth_details["password"],
            "use_key": True,
            "nickname": nickname,
        }


def list_servers(servers, start=0):
    end = start + 10
    for idx, server in enumerate(servers[start:end], start=start + 1):
        print(f"{idx}. {server['nickname']} ({server['ip']})")


def delete_server(servers):
    page = 0
    while True:
        os.system("cls" if os.name == "nt" else "clear")  # Clear the screen
        list_servers(servers, start=page * 10)
        print(
            "\nSelect a server to delete or type 'next' for the next page or 'prev' for the previous page."
        )
        choice = input("Enter server number or 'next', 'prev': ")
        if choice == "next" and (page + 1) * 10 < len(servers):
            page += 1
        elif choice == "prev" and page > 0:
            page -= 1
        elif choice.isdigit() and 1 <= int(choice) <= len(servers):
            index_to_delete = int(choice) - 1
            del servers[index_to_delete]
            return servers


def assign_server_to_group(config):
    if not config["servers"]:
        print("No servers available!")
        return
    for idx, server in enumerate(config["servers"], start=1):
        print(f"{idx}. {server['nickname']} ({server['ip']})")

    server_choice = int(input("Select a server to assign to a group: ")) - 1
    server_ip = config["servers"][server_choice]["ip"]

    for idx, group in enumerate(config["groups"].keys(), start=1):
        print(f"{idx}. {group}")

    group_choice = int(input("Select a group: ")) - 1
    group_name = list(config["groups"].keys())[group_choice]

    if server_ip in config["groups"][group_name]:
        print(f"Server with IP {server_ip} is already in {group_name}!")
        return

    config["groups"][group_name].append(server_ip)
    print(f"Server with IP {server_ip} added to {group_name}!")


def create_group(config):
    group_name = input("Enter the name for the new group: ")
    if group_name in config["groups"]:
        print("Group with this name already exists!")
        return
    config["groups"][group_name] = []
    print(f"Group '{group_name}' created!")


def install_key_to_server(server):
    public_key_path = "./keys/id_rsa.pub"

    # Read the local public key content
    with open(public_key_path, "r") as f:
        public_key_content = f.read().strip()

    if not server.get("password"):
        server["password"] = input(f"Enter the password for {server["ip"]}: ")

    # First, use SSH to check if the key is already in the authorized_keys file
    with SSHClient() as ssh:
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(
            server["ip"], username=server["username"], password=server["password"]
        )

        # Check if the key is already present
        stdin, stdout, stderr = ssh.exec_command("cat ~/.ssh/authorized_keys")
        existing_keys = stdout.read().decode().splitlines()
        if public_key_content in existing_keys:
            print(f"The key is already installed on {server['ip']}. Skipping.")
            return

        # If the key isn't present, continue with the installation
        sftp = ssh.open_sftp()
        sftp.put(public_key_path, "/tmp/id_rsa.pub")
        sftp.close()

        # Now, append this key to the authorized_keys on the remote server
        commands = [
            "mkdir -p ~/.ssh",
            "cat /tmp/id_rsa.pub >> ~/.ssh/authorized_keys",
            "chmod 600 ~/.ssh/authorized_keys",
            "rm /tmp/id_rsa.pub",
        ]
        for command in commands:
            stdin, stdout, stderr = ssh.exec_command(command)
            stdout.read().decode()  # Just reading to consume the output

    print(f"Public key installed to {server['ip']} successfully.")


def ask_authentication_details():
    choice = input("Do you want to authenticate via (1) Password or (2) Key? ")

    if choice == "1":
        password = input("Enter the password: ")
        return {"type": "password", "password": password}

    elif choice == "2":
        # Check for the existence of the key
        if not os.path.exists("./keys/id_rsa.pub"):
            print("No SSH key found in ./keys/ directory. Generating now...")
            subprocess.run(["python", "keys.py"])

        # Even if a key is used, the password might be needed for the initial setup
        password = input("Enter the password (needed to install the key initially): ")
        return {"type": "key", "password": password}


def ask_install_target_type():
    print("Do you want to install the key to a (1) Server or (2) Group?")
    choice = input("Enter your choice (1/2): ")
    return choice


def main():
    if os.path.exists("config.txt"):
        try:
            with open("config.txt", "r") as infile:
                config = json.load(infile)
        except Exception as e:
            print(f"Error reading config: {e}")
            config = {"servers": [], "groups": {}}
    else:
        config = {"servers": [], "groups": {}}

    while True:
        print("1. Delete a server")
        print("2. Add a server")
        print("3. Create a group")
        print("4. Assign server to a group")
        print("5. Install key to a server")
        print("6. Cancel")
        choice = input("Select an option: ")

        if choice == "1" and config["servers"]:
            config["servers"] = delete_server(config["servers"])
        elif choice == "1" and not config["servers"]:
            print("No servers available to delete.")
        elif choice == "2":
            server = ask_server_details()
            config["servers"].append(server)

            if server.get("key"):
                print("\nServers available to install the key:")
                list_servers(config["servers"])
                server_choice = int(input("Select a server to install the key: ")) - 1
                target_server = config["servers"][server_choice]
                install_key_to_server(target_server)
        elif choice == "3":
            create_group(config)
        elif choice == "4":
            assign_server_to_group(config)
        elif choice == "5":
            if not config["servers"]:
                print("No servers available!")
                continue

            target_type = ask_install_target_type()

            # Install key to a single server
            if target_type == "1":
                for idx, server in enumerate(config["servers"], start=1):
                    print(f"{idx}. {server['nickname']} ({server['ip']})")

                server_choice = int(input("Select a server to install the key: ")) - 1
                selected_server = config["servers"][server_choice]

                if "use_key" in selected_server:
                    try:
                        install_key_to_server(selected_server)
                        del selected_server["password"]
                    except Exception as e:
                        print(f"Error installing key: {e}")
                else:
                    print(
                        "The selected server is not configured for key authentication."
                    )

            # Install key to a group of servers
            elif target_type == "2":
                if not config["groups"]:
                    print("No groups available!")
                    continue

                for idx, group in enumerate(config["groups"].keys(), start=1):
                    print(f"{idx}. {group}")

                group_choice = (
                    int(input("Select a group to install the key to its servers: ")) - 1
                )
                group_name = list(config["groups"].keys())[group_choice]

                for server_ip in config["groups"][group_name]:
                    matched_server = next(
                        filter(lambda x: x["ip"] == server_ip, config["servers"]), None
                    )
                    if matched_server and "use_key" in matched_server:
                        try:
                            install_key_to_server(matched_server)
                            del matched_server["password"]
                        except Exception as e:
                            print(f"Error installing key to {server_ip}: {e}")
                    else:
                        print(
                            f"The server {server_ip} is not configured for key authentication or doesn't exist."
                        )
        elif choice == "6":
            break

        with open("config.txt", "w") as outfile:
            json.dump(config, outfile, indent=4)


if __name__ == "__main__":
    main()
