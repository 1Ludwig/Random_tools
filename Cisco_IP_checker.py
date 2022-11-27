from netmiko import ConnectHandler
from getpass import getpass
import subprocess
import threading
import concurrent.futures
import logging
from datetime import datetime
import re


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
    # Regex string to matche which interfaces we want to look into
    # Vlans + Loopbacks + *Ethernet*
    interfaces_to_search_re = r"[Vv]lan.*|[Ll]oopback.*|.*[Ee]thernet.*"
    print_output = []
    general_counter = 0
    try:
        print_output.append(f"Connecting to the device: {device['host']}\n")
        # connecting to the device here
        with ConnectHandler(**device) as net_connect:  # Using Context Manager
            try:
                for command in commands:
                    # sending show command and sorting the data into a list of dicts
                    output_dict = net_connect.send_command(command, use_textfsm=True)

                    # output_dict contains all the interfaces sorted by text_fsm
                    # next step is to loop through all the interfaces
                    for interface in output_dict:
                        # We only want interfaces with an IP address, hence skip 'unassigned'
                        if not interface["ipaddr"] == "unassigned":
                            # Of all interfaces that have IP, lets only look at those specified in the regex filter
                            if re.search(interfaces_to_search_re, interface["intf"]):
                                # fetching interface name and use it to check for more addresses
                                print_output.append(f"{interface['intf']}")
                                ip_interface_output = net_connect.send_command(
                                    f"show ip interface {interface['intf']}",
                                    use_textfsm=True,
                                )
                                # fetching IP addresses and subnet mask from interface dict
                                for ip_numbers in ip_interface_output:
                                    # Merge IP and Submask to the same object
                                    ip_to_dict = dict(
                                        zip(ip_numbers["ipaddr"], ip_numbers["mask"])
                                    )
                                    # Fetching the first and primary IP + Submask on the interface
                                    # main IP is returned first in the dict
                                    print_output.append(
                                        f"{list(ip_to_dict.items())[0][0]}/{list(ip_to_dict.items())[0][1]}"
                                    )
                                    # Check if the interface have multiple IP's
                                    # if list have more than one entry log them as secondary IP's
                                    if len(list(ip_to_dict.items())) > 1:
                                        # skip first entry since we have already fetched that as primary IP
                                        for key, value in list(ip_to_dict.items())[1:]:
                                            print_output.append(
                                                f"{key}/{value} secondary"
                                            )

            except:
                # if the command is mistyped then this error message will show.
                print_output.append(f"\nFailed to send command to {device['host']}\n")
                print_output.append(f"Command:\n{command}\n")
    except Exception as e:
        print_output.append(e)
        print_output.append(f"Failed to authenticate to {device['host']}" + "\n\n")
        with open("text_files/authfailed_hosts.txt", "w+", encoding="utf-8") as f:
            f.writelines(str(device["host"]) + "\n")

    finally:
        if general_counter > 0:
            print_output.append(f"general_counter: {general_counter}")
        print_output.append(f"\nclosing connection to: {device['host']}")

        # print all the status messages together
        print("\n")
        for cli_output in print_output:
            print(cli_output, sep="\n")
        print("\n\n" + "#" * 92)


def main():

    host_list()

    commands = ["show ip interface brief"]

    ssh_username = Username()
    password = getpass()

    # A list comprehension
    devices = [
        {
            "device_type": "cisco_ios",
            # "device_type": "hp_procurve",
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
    print(f"\nElapsed time: {str(datetime.now() - start_time)}")
