#!/usr/bin/python3

from gi.repository import Gtk
import os
import re
import shutil  # copy files
import sys

import gi


gi.require_version('Gtk', '3.0')


"""
----------------------------------------------
Originaly created by : Nityananda Gohain
School of Engineering, Tezpur University
On: 27/10/17
----------------------------------------------
Modified by: @dennohpeter
School of Computing, Maseno University
On: 31/10/19
----------------------------------------------

"""
"""
Run it as sudo
Three files will be modified
1) /etc/apt/apt.conf
2) /etc/environment
3) /etc/bash.bashrc
"""

# backup_dir = "{}/{}".format(current_dir, ".backup_proxy")
# apt_backup_file = "{}/apt_initial.txt".format(backup_dir)
# env_backup_file = "{}/env_initial.txt".format(backup_dir)
# bashrc_backup_file = "{}/bashrc_initial.txt".format(backup_dir)

# apt_prev_file = "{}/apt_prev.txt".format(backup_dir)
# env_prev_file = "{}/env_prev.txt".format(backup_dir)
# bashrc_prev_file = "{}/bashrc_prev.txt".format(backup_dir)


# def create_proxy_backup(previous=False):
#     if previous:
#         if os.path.isfile(apt_file_path):
#             shutil.copyfile(apt_file_path, apt_prev_file)
#         if os.path.isfile(env_file_path):
#             shutil.copyfile(env_file_path, env_prev_file)
#         if os.path.isfile(bashrc_file_path):
#             shutil.copyfile(bashrc_file_path, bashrc_prev_file)
#     else:
#         if not os.path.isdir(backup_dir):
#             os.mkdir(backup_dir)
#             if os.path.isfile(apt_file_path):
#                 shutil.copyfile(apt_file_path, apt_backup_file)
#             if os.path.isfile(env_file_path):
#                 shutil.copyfile(env_file_path, env_backup_file)
#             if os.path.isfile(bashrc_file_path):
#                 shutil.copyfile(bashrc_file_path, bashrc_backup_file)


# def restore_prev_proxy():
#     restore_proxy(previous=True)


def default():
    print("Invalid option, please try again.")
    sys.exit()


class ProxyWindow(object):
    apt_file_path = "/etc/apt/apt.conf"
    env_file_path = "/etc/environment"
    bashrc_file_path = "/etc/bash.bashrc"
    current_dir = "."

    def __init__(self):
        gladeFile = 'proxy.glade'

        self.builder = Gtk.Builder()
        self.builder.add_from_file(gladeFile)
        self.builder.connect_signals(self)

        self.http_proxy_field = self.builder.get_object('http_proxy')
        self.http_port_field = self.builder.get_object('http_port')

        self.https_proxy_field = self.builder.get_object('https_proxy')
        self.https_port_field = self.builder.get_object('https_port')

        self.ftp_proxy_field = self.builder.get_object('ftp_proxy')
        self.ftp_port_field = self.builder.get_object('ftp_port')

        self.socks_host_field = self.builder.get_object('socks_host')
        self.socks_port_field = self.builder.get_object('socks_port')

        self.fields = [self.http_proxy_field, self.http_port_field, self.https_proxy_field, self.https_port_field,
                       self.ftp_proxy_field, self.ftp_port_field, self.socks_host_field, self.socks_port_field]

        window = self.builder.get_object('window')
        window.connect('delete-event', Gtk.main_quit)
        window.show()

    def on_set_manual_proxy_toggled(self, widget):
        self.activate_fields()
        username, password = None, None

    def on_save_proxy_btn_clicked(self, widget):
        # remove existing proxies if exist before setting new
        self.remove_proxy(False)
        # writing proxy to /etc/apt/apt.conf file
        self.write_proxy_to_apt()
        # writing proxy to /etc/environment file
        self.write_proxy_to_env()
        # writing proxy to /etc/bash.bashrc file
        self.write_proxy_to_bashrc()
        print("All Set!!!")

    # removes proxies from apt, env and bashrc
    def on_no_proxy_toggled(self, widget):
        self.deactivate_fields()
        # before removing proxy create a backup
        # create_proxy_backup(True)
        files = [self.apt_file_path, self.env_file_path, self.bashrc_file_path]
        for file in files:
            with open(file, 'r+') as open_file:
                lines = open_file.readlines()
                # moves the file pointer to the beginning of the stream
                open_file.seek(0)
                for line in lines:
                    if "http://" not in line and "https://" not in line and "ftp://" not in line and "socks://" not in line:
                        open_file.write(line)
                open_file.truncate()

    def on_fill_ftp_and_https_toggled(self, widget):
        https_and_ftp_box = self.builder.get_object('https_and_ftp')
        if widget.get_active():
            https_and_ftp_box.set_sensitive(False)
            self.https_proxy_field.set_text(self.http_proxy_field.get_text())
            self.https_port_field.set_text(self.http_port_field.get_text())

            self.ftp_proxy_field.set_text(self.http_proxy_field.get_text())
            self.ftp_port_field.set_text(self.http_port_field.get_text())
        else:
            https_and_ftp_box.set_sensitive(True)
            self.https_proxy_field.set_text('')
            self.https_port_field.set_text('0')

            self.ftp_proxy_field.set_text('')
            self.ftp_port_field.set_text('0')

    def activate_fields(self):
        self.builder.get_object('content').set_sensitive(True)

    def deactivate_fields(self):
        self.builder.get_object('content').set_sensitive(False)
    # Writes proxy to /etc/apt/apt.conf

    def write_proxy_to_apt(self):
        lines = ['Acquire::http::proxy "http://{}:{}/";\n',
                 'Acquire::ftp::proxy "http://{}:{}/";\n',
                 'Acquire::https::proxy "http://{}:{}/";\n']
        writer(apt_file_path, lines, proxy, port, username, password)

    # Writes proxy to /etc/env

    def write_proxy_to_env(self):
        lines = ['http_proxy=http://{}:{}/\n',
                 'https_proxy=https://{}:{}/\n',
                 'ftp_proxy=ftp://{}:{}/\n',
                 'socks_proxy=socks://{}:{}/\n']
        writer(env_file_path, lines, proxy, port, username, password)

    # Writes proxy to /etc/bash.bashrc

    def write_proxy_to_bashrc(self):
        lines = ['export http_proxy="http://{}:{}/"\n',
                 'export https_proxy="https://{}:{}/"\n',
                 'export ftp_proxy="ftp://{}:{}/"\n',
                 'export socks_proxy="socks://{}:{}/"\n']

        writer(bashrc_file_path, lines, proxy, port, username, password)

    def writer(self, file_path, lines):
        try:
            file = open(file_path, "a")
            if username and password:
                for line in lines:
                    proxy_with_username = "{user}:{passwd}@{proxy}".format(
                        user=username, passwd=password, proxy=proxy)
                    file.write(line.format(proxy_with_username, port))
            else:
                for line in lines:
                    file.write(line.format(proxy, port))
        except IOError as err:
            exit("%s:\nRun again as sudo" % err)
        file.close()
        print("Done setting: %s" % file_path)

    # gets user input and strips it

    def _get_input(label):
        option = ""
        try:
            option = input(label)
        except Exception as err:
            print(str(err))
            exit("Run with python3 $ python3 proxy.py")
        print("---------------")
        return str(option).strip()

    # enables you to view current proxies

    # def view_proxy():
    #     size = os.path.getsize(apt_file_path)
    #     if size:
    #         file = open(apt_file_path, "r")
    #         line_1 = file.readline()
    #         pattern_1 = re.compile(r"(\d+.*):(\d+)\/")
    #         pattern_2 = re.compile(r"(\w+):(\w+)@(\d+.*):(\d+)\/")
    #         if r"@" in line_1.strip():
    #             [(username, password, proxy, port)] = pattern_2.findall(line_1)
    #         else:
    #             [(proxy, port)] = pattern_1.findall(line_1)
    #             username, password = None, ""
    #         print("Current Proxy is now: ")
    #         print("=============================")
    #         print(' HTTP Proxy: %s' % proxy)
    #         print(' Port: %s' % port)
    #         print(' Username: %s' % username)
    #         print(' Password: %s' %
    #               ([None, '*' * len(password)][password != ""]))
    #         print("=============================")
    #     else:
    #         print("No Proxies Set!!")

    # restores default proxy from backup files

    # def restore_proxy(show_log=True, previous=False):
    #     if previous:
    #         shutil.copy(apt_prev_file, apt_file_path)
    #         shutil.copy(env_prev_file, env_file_path)
    #         shutil.copy(bashrc_prev_file, bashrc_file_path)
    #         print("Previous Proxy Restored")
    #     else:
    #         shutil.copy(apt_backup_file, apt_file_path)
    #         shutil.copy(env_backup_file, env_file_path)
    #         shutil.copy(bashrc_backup_file, bashrc_file_path)
    #         print("Default State Restored!")

    #     view_proxy()


if __name__ == "__main__":
    # create_proxy_backup()
    # home_message = "Select an option from the menu \
    #         \n  2. Remove Proxy \
    #         \n  3. View Current Proxy \
    #         \n  4. Restore Previous Proxy \
    #         \n  5. Restore Default State \
    #         \nEnter choice: "
    # try:
    #     option = _get_input(home_message)
    #     menu = {"1": set_proxy,
    #             "2": remove_proxy,
    #             "3": view_proxy,
    #             "4": restore_prev_proxy,
    #             "5": restore_proxy,
    #             }

    #     menu.get(option, default)()

    main = ProxyWindow()
    Gtk.main()
