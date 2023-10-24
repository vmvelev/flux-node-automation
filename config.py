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


def main():
    if os.path.exists("config.txt"):
        with open("config.txt", "r") as infile:
            servers = json.load(infile)
    else:
        servers = []

    while True:
        print("1. Delete a server")
        print("2. Add another server")
        print("3. Cancel")
        choice = input("Select an option: ")

        if choice == "1" and servers:
            servers = delete_server(servers)
            with open("config.txt", "w") as outfile:
                json.dump(servers, outfile, indent=4)
        elif choice == "1" and not servers:
            print("No servers available to delete.")
        elif choice == "2":
            server = ask_server_details()
            servers.append(server)
            with open("config.txt", "w") as outfile:
                json.dump(servers, outfile, indent=4)
        elif choice == "3":
            break


if __name__ == "__main__":
    main()
