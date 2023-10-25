import json
import os


def ask_server_details():
    ip = input("Which is the IP you want to connect to? ")
    username = input("What is the username for that server? ")
    password = input("What is the password for that server? ")
    nickname = input("What is the nickname that you want to give to this server? ")
    return {"ip": ip, "username": username, "password": password, "nickname": nickname}


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


def main():
    if os.path.exists("config.txt"):
        with open("config.txt", "r") as infile:
            config = json.load(infile)
    else:
        config = {"servers": [], "groups": {}}

    while True:
        print("1. Delete a server")
        print("2. Add a server")
        print("3. Create a group")
        print("4. Assign server to a group")
        print("5. Cancel")
        choice = input("Select an option: ")

        if choice == "1" and config["servers"]:
            config["servers"] = delete_server(config["servers"])
        elif choice == "1" and not config["servers"]:
            print("No servers available to delete.")
        elif choice == "2":
            server = ask_server_details()
            config["servers"].append(server)
        elif choice == "3":
            create_group(config)
        elif choice == "4":
            assign_server_to_group(config)
        elif choice == "5":
            break

        with open("config.txt", "w") as outfile:
            json.dump(config, outfile, indent=4)


if __name__ == "__main__":
    main()
