from netmiko import ConnectHandler
from getpass import getpass
import subprocess
import threading
import concurrent.futures
import logging
from datetime import datetime


def Username():
    Result = subprocess.getoutput("whoami")
    return Result


def host_list():
    ipaddrs = []
    with open("text_files/host_list.txt", "r", encoding="utf-8") as f:
        for line in f:
            if not line.isspace():
                ipaddrs.append(line.strip())
    return ipaddrs


def ssh_connection(device, commands):
    print_output = []
    number_of_open_ports = 0
    try:
        print_output.append(f"Connecting to the device: {device['host']}\n")
        #connecting to the device here
        with ConnectHandler(**device) as net_connect:  # Using Context Manager
            try:
                for command in commands:
                    # sending show command and sorting the data into a dict
                    output_dict = net_connect.send_command(command, use_textfsm=True)

                    # going through all the return dicts and searches for status down and enabled yes
                    for interface in output_dict:
                        if interface["status"] == "Down" and interface["enabled"] == "Yes":

                            # if condition matches then disable the port
                            print_output.append(f"interface {interface['port']} shutdown")
                            #net_connect.send_config_set(f"interface {interface['port']} disable")
                            number_of_open_ports += 1

                # optinal to save the config
                # print_output.append(f"\n\n{net_connect.save_config()}")

            except:
                # if the command is mistyped then this error message will show.
                print_output.append(f"\nFailed to send command to {device['host']}\n")
                print_output.append(f"Command:\n{command}\n")
    except Exception as e:
        print_output.append(e)
        print_output.append(f"Failed to authenticate to {device['host']}" + "\n\n")
        with open("text_files/authfailed_hosts.txt", "a+", encoding="utf-8") as f:
            f.writelines(str(device["host"]) + "\n")
        # facts = net_connect.send_command("show version")  # Inside the connection
        # Notice here I didn't call the `net_connect.disconnect()`
        # because the `with` statement automatically disconnects the session.
    # On this indentation level (4 spaces), the connection is terminated

    finally:
        if number_of_open_ports > 0:
            print_output.append(f"number of ports closed: {number_of_open_ports}")
        print_output.append(f"closing connection to: {device['host']}")

        # print all the status messages together
        print("\n")
        for cli_output in print_output:
            print(cli_output, sep="\n")
        print("\n\n"+"#"*92)


def main():

    host_list()

    commands = ["show interfaces brief"]

    ssh_username = Username()
    password = getpass()

    # A list comprehension
    devices = [
        {
            "device_type": "hp_procurve",
            "host": ip,
            "username": ssh_username,
            "password": password,
        }
        for ip in host_list()
    ]
    MAX_THREADS = 200
    nof_switches = len(devices)

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        for device in devices:
            executor.submit(ssh_connection, device, commands)
            nof_switches = nof_switches - 1
            #print(f"Threading active count: {threading.active_count()}")
            print(f"Executor max workers count: {executor._max_workers}")
            print(f"nof_switches: {nof_switches}")
            logging.debug(
                f"Processing {device} [{nof_switches}] t:({threading.active_count()}/{MAX_THREADS - 1})")
    print(f"Number of devices: {len(devices)}")


if __name__ == "__main__":
    start_time = datetime.now()
    main()
    print("\nElapsed time: " + str(datetime.now() - start_time))
