import serial

import serial.tools.list_ports as port_list


a = serial.Serial("COM3", 115200, timeout=0, parity=serial.PARITY_NONE, rtscts=1)

wer=4