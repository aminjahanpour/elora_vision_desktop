import time

from pprint import pprint

import serial.tools.list_ports as port_list


def main():

    ports = list(port_list.comports())

    print("")
    for port in ports:

        pprint(vars(port))
        print("-------------------------")


def get_all_ports():
    return [port.name for port in list(port_list.comports())]

if __name__ == '__main__':
    print(get_all_ports())
    # main()





"""
sender IP
receiver IP


"""