import paramiko
from YamlOp.YamlOperations import YamlOperations


class SshClass:
    local_netcfg_path = "./cfg/netcfg.yaml"

    def __init__(self, host, user, passwd, port=False):
        self.host = host
        self.user = user
        self.passwd = passwd
        if port:
            self.port = port
        else:
            self.port = 22
        self.connect()

    def connect(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh.connect(hostname=self.host, username=self.user,
                             password=self.passwd, port=self.port)
        except paramiko.AuthenticationException:
            print("Authentication exception")
        except paramiko.SSHException:
            print("SSH exception")
        except:
            print("Unknown exception")

    def execute_cmd(self, command, timeout=5):
        try:
            stdin, stdout, stderr = self.ssh.exec_command(command, timeout=timeout)
            if stdout.channel.recv_exit_status():
                print("Errors when executing command: \"{}\"".format(command))
                for line in stderr.readlines():
                    print(line)
        except paramiko.SSHException:
            print("Exception when trying to execute command: {}".format(command))
        else:
            for line in stdout.readlines():
                print(line)

    def verify_user(self):
        user=input("###  Verify user  ###\nuser: ")
        self.execute_cmd("id {}".format(user))

    def add_user(self):
        user=input("###  Add user  ###\nuser: ")
        self.execute_cmd("sudo useradd -m {}".format(user))
        self.execute_cmd("id {}".format(user))

    def delete_user(self):
        user=input("###  Delete user  ###\nuser: ")
        self.execute_cmd("sudo userdel {}".format(user))

    def perform_action(self, user_option):
        if user_option == "1":
            self.add_user()
        elif user_option == "2":
            self.delete_user()
        elif user_option == "3":
            self.verify_user()
        elif user_option == "4":
            self.get_network_config_file()
            YamlOperations(SshClass.local_netcfg_path, "network_config").listNetworkConfig()

    def get_network_config_file(self):
        self.sftp = self.ssh.open_sftp()
        remote_path="/etc/netplan/01-netcfg.yaml"
        try:
            self.sftp.get(remote_path, SshClass.local_netcfg_path)
        except Exception as e:
            print("Exception when trying to copy remote file: {}".format(remote_path), "\n", e)
        else:
            print("File remotely copied from: {}".format(remote_path))
        finally:
            self.sftp.close()