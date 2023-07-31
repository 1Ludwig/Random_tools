he-luni@stodc01netmgt01:~/scripts$ cat search_serial_cisco.py 
from netmiko import ConnectHandler
from getpass import getpass
import subprocess
import threading
import concurrent.futures
import logging
from datetime import datetime


def Username():
    Result = subprocess.getoutput("whoami")
    # Result = input("Enter Username: ")
    return Result


def host_list():
    ipaddrs = []
    with open("text_files/host_list.txt", "r", encoding="utf-8") as f:
        for line in f:
            if not line.isspace():
                ipaddrs.append(line.strip())
    return ipaddrs


def serial_list():
    serial_list = []
    with open("text_files/serial_list.txt", "r", encoding="utf-8") as f:
        for line in f:
            if not line.isspace():
                serial_list.append(line.strip())
    return serial_list


def ssh_connection(device, commands):
    print_output = []
    number_of_open_ports = 0
    try:
        print_output.append(f"Connecting to the device: {device['host']}\n")
        # connecting to the device here
        with ConnectHandler(**device) as net_connect:  # Using Context Manager
            try:
                for command in commands:
                    # sending show command and sorting the data into a list of dicts
                    output_dict = net_connect.send_command(command, use_textfsm=True)
                    # print(output_dict)

                    # going through all the return dicts and searches for status down and enabled yes
                    for inventory_value in output_dict:
                        # print(inventory_value)
                        # print(interface)
                        for serial in serial_list():
                            # print(serial)
                            if inventory_value["sn"] == serial:
                                print_output.append(
                                    f"Serial: {inventory_value['sn']} - {device['host']}"
                                )
                                with open(
                                    "text_files/findings.txt", "a+", encoding="utf-8"
                                ) as f:
                                    f.write(
                                        f"{inventory_value['sn']} - {device['host']}\n"
                                    )

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
        print_output.append(f"closing connection to: {device['host']}")

        # print all the status messages together
        print("\n")
        for cli_output in print_output:
            print(cli_output, sep="\n")
        print("\n\n" + "#" * 92)


def main():

    host_list()
    serial_list()

    commands = ["show inventory"]

    ssh_username = Username()
    password = getpass()

    # A list comprehension
    devices = [
        {
            "device_type": "cisco_ios",
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
            # print(f"Threading active count: {threading.active_count()}")
            print(f"Executor max workers count: {executor._max_workers}")
            print(f"nof_switches: {nof_switches}")
            logging.debug(
                f"Processing {device} [{nof_switches}] t:({threading.active_count()}/{MAX_THREADS - 1})"
            )
    print(f"Number of devices: {len(devices)}")


if __name__ == "__main__":
    start_time = datetime.now()
    main()
    print("\nElapsed time: " + str(datetime.now() - start_time))
