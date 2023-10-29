import subprocess
import os
import getpass


def generate_ssh_key():
    # Check if ./keys/ directory exists, if not, create it
    if not os.path.exists("./keys"):
        os.mkdir("./keys")

    # Ask the user for a passphrase
    passphrase = getpass.getpass("Enter a passphrase (leave empty for no passphrase): ")

    # Generate the ssh key
    keygen_command = [
        "ssh-keygen",
        "-t",
        "rsa",
        "-f",
        "./keys/id_rsa",
        "-N",
        passphrase,
    ]

    subprocess.run(keygen_command)

    print("SSH key generated and saved in ./keys/ directory.")


if __name__ == "__main__":
    generate_ssh_key()
