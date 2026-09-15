import serial
import serial.tools.list_ports as port_list
import toolkit as tk


class Goober():
    def __init__(self, port):
        self.port = port
        self.usb_device_serial = None

        self.hash_bytes = bytes.fromhex(tk.settings.hash)

        self.print_prefix = "Goober Class --> "

        self.role = 'receiver'

    def set_up(self):
        print(self.print_prefix + f'looking for port {self.port}...')

        ports = list(port_list.comports())

        self.usb_device = None

        if self.usb_device_serial is not None:
            self.usb_device_serial.close()

        for p in ports:
            if self.port == p.name:
                self.usb_device = p
                print(self.print_prefix + f'usb device found on port {self.usb_device}')

        if self.usb_device is None:
            print(self.print_prefix + "Error: can not find the gadget over USB. Please reconnect it and try again.")
            return
        else:
            self.usb_device_serial = serial.Serial(self.usb_device.device, 115200, timeout=0, parity=serial.PARITY_NONE,
                                                   rtscts=1)
            self.setup_already = True
            print(self.print_prefix + f'Goober is set up.')
            return True

    def save_settings(self):
        assert self.usb_device_serial.write(tk.settings.get_buffer()[:tk.usb_data_buffer_len]) == tk.usb_data_buffer_len
        print(self.print_prefix + "Settings sent to Goober.")
        return True

    def tell_goober_we_are_senders(self):

        body = bytearray(tk.rf_tx_body_length * [0])

        buffer = tk.get_formatted_payload(sender_ip=0, receiver_ip=0, payload_type=tk.payload_type_we_are_senders,
                                          hash_bytes=self.hash_bytes, body=body, zero_body=True)

        assert self.usb_device_serial.write(buffer[:tk.usb_data_buffer_len]) == tk.usb_data_buffer_len
        print()
        print(self.print_prefix + "Told Goober that we are the Sender Unit.")

        self.role = 'sender'

        return True

    def tell_goober_we_are_receiver(self):

        body = bytearray(tk.rf_tx_body_length * [0])

        buffer = tk.get_formatted_payload(sender_ip=0, receiver_ip=0, payload_type=tk.payload_type_we_are_receiver,
                                          hash_bytes=self.hash_bytes, body=body, zero_body=True)

        assert self.usb_device_serial.write(buffer[:tk.usb_data_buffer_len]) == tk.usb_data_buffer_len
        print()
        print(self.print_prefix + "Told Goober that we are the Receiver Unit.")

        self.role = 'receiver'

        return True

    def release_usb(self):
        self.usb_device_serial.close()
        self.usb_device = None

        return True
