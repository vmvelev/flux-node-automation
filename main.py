from paramiko import SSHClient, AutoAddPolicy

ssh = SSHClient()
ssh.set_missing_host_key_policy(AutoAddPolicy())
ssh.connect("192.168.31.31", username="cumulus", password="980480")
stdin, stdout, stderr = ssh.exec_command("ls -l")
print(stdout.read().decode())
ssh.close()
