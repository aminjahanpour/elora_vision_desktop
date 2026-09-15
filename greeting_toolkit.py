import toolkit as tk

greeting_prefix = (211, 49, 143)


class Greeting:
    def __init__(self, usb_buffer_received):


        self.payload_bytes_count =0
    
        self.snr  = 0
        self.rssi  = 0
    
        self.include_gps = False
        self.include_image = False
        self.include_voice = False
        self.include_text = False
    
        self.gps_buffer_size = 0
        self.text_buffer_size = 0
        self.voice_buffer_size = 0
        self.image_buffer_size = 0


        self.usb_buffer_received = usb_buffer_received

        self.payload_bytes_count = tk.three_bytes_to_integer(
            usb_buffer_received[tk.rf_tx_header_length + 0],
            usb_buffer_received[tk.rf_tx_header_length + 1],
            usb_buffer_received[tk.rf_tx_header_length + 2]
        )


        self.include_gps           = usb_buffer_received[tk.rf_tx_header_length + 3] == 1
        self.include_text          = usb_buffer_received[tk.rf_tx_header_length + 4] == 1
        self.include_voice         = usb_buffer_received[tk.rf_tx_header_length + 5] == 1
        self.include_image         = usb_buffer_received[tk.rf_tx_header_length + 6] == 1


        if (self.include_gps):
            self.gps_buffer_size = 30


        self.text_buffer_size = tk.three_bytes_to_integer(
            usb_buffer_received[tk.rf_tx_header_length + 7],
            usb_buffer_received[tk.rf_tx_header_length + 8],
            usb_buffer_received[tk.rf_tx_header_length + 9]
        )

        self.voice_buffer_size = tk.three_bytes_to_integer(
            usb_buffer_received[tk.rf_tx_header_length + 10],
            usb_buffer_received[tk.rf_tx_header_length + 11],
            usb_buffer_received[tk.rf_tx_header_length + 12]
        )


        self.image_buffer_size = tk.three_bytes_to_integer(
            usb_buffer_received[tk.rf_tx_header_length + 13],
            usb_buffer_received[tk.rf_tx_header_length + 14],
            usb_buffer_received[tk.rf_tx_header_length + 15]
        )




        self.snr = usb_buffer_received[tk.snr_byte_idx]
        self.rssi = -(int(usb_buffer_received[tk.rssi_byte_idx]) - 256 + 157)

        if self.snr < 0:
            self.rssi = self.rssi + 0.25 * self.snr






def guess_byte(byte_1, byte_2, byte_3):
    ret = byte_1

    if byte_2 == byte_3:
        ret = byte_2

    return ret


def recover_greeting_payload(buffer):
    for i in range(21):
        buffer[i] = guess_byte(buffer[i], buffer[i + 21], buffer[i + 42])


def is_greeting(usb_buffer_received):
    return usb_buffer_received[tk.header_payload_type_byte_idx] == tk.payload_type_greeting


def build_greeting_payload(
        total_number_of_bytes_to_send,

        include_gps,
        include_text,
        include_voice,
        include_image,

        text_buffer_size,
        voice_buffer_size,
        camera_image_buffer_size

):

    buffer = bytearray((tk.usb_data_buffer_len - tk.rf_tx_header_length) * [0])

    buffer[0], buffer[1], buffer[2] = tk.to_three_bytes(total_number_of_bytes_to_send)

    buffer[3] = 1 if (include_gps)   else 0
    buffer[4] = 1 if (include_text)  else 0
    buffer[5] = 1 if (include_voice) else 0
    buffer[6] = 1 if (include_image) else 0

    if include_text:
        buffer[7], buffer[8], buffer[9]     = tk.to_three_bytes(text_buffer_size)

    if (include_voice):
        buffer[10], buffer[11], buffer[12]  = tk.to_three_bytes(voice_buffer_size)

    if (include_image):
        buffer[13], buffer[14], buffer[15]  = tk.to_three_bytes(camera_image_buffer_size)

    return buffer
