from datetime import datetime
import os

import goober_class
import receiver_unit
import sender_unit
import settings_class
import serial.tools.list_ports as port_list
import copy
import json
import time


received_encrypted_payload_file_name = "received_encrypted_payload.dat"
received_redundant_file_name = "received_redundant.dat"
received_frame_file_name = "received_frame.jpg"
sent_frame_file_name = "sent_frame.jpg"
sent_payload_info_file_name = "sent_frame_info.json"
received_gps_file_name = "received_gps.json"
received_text_file_name = "received_text.txt"
received_audio_file_name = "received_audio.3gp"
received_signal_info_file_name = "received_signal_info.json"
settings_file_name = 'settings.json'
aes_qr_code_file_name = 'aes_qr_code.png'
db_file_name = "db.csv"


image_load_error_printed_already = False

root_path = os.path.dirname(os.path.realpath(__file__))

gallery_path = os.path.join(root_path, 'sessions')



header_payload_type_byte_idx                = 2

payload_type_greeting 						= 1
payload_type_data 							= 2
payload_type_we_are_senders 				= 3
payload_type_settings 						= 4
payload_type_stop_serving 					= 5
payload_tpye_intrupt_receiver_goober_usb	= 6
payload_type_knocking						= 7
payload_type_we_are_receiver                = 8



rf_tx_header_length                         = 6
rf_tx_body_length                           = 249

snr_byte_idx                                = 22
rssi_byte_idx                               = 23





usb_data_buffer_len = 64



usb_buffer_reset_receiver_frame = bytearray(usb_data_buffer_len * [11])

usb_buffer_confirmation = bytearray(usb_data_buffer_len * [1])





settings = settings_class.Settings()

sender_goober = None

receiver_goober = None

already_assigned_goobers = []


# Receiver Unit
receiver_thread = None


# Sender Unit
live_video_frame = None
allowed_to_stream = None
sender_main_thread = None










def api_get_a_preped_goober(port):
    goober = goober_class.Goober(port)

    goober.set_up()

    assert goober.save_settings()

    goober.release_usb()


    goober = goober_class.Goober(port)

    goober.set_up()

    return goober



def api_send(goober, value):

    if goober.role != 'sender':
        assert goober.tell_goober_we_are_senders()

    text_buffer = bytes(str(value), "utf8")

    sender_unit.send(goober=goober, text_buffer=text_buffer, jpeg_byte_array=None)


def api_start_listening(goober, log_content):

    if goober.role != 'receiver':
        assert goober.tell_goober_we_are_receiver()

    text_buffer = receiver_unit.receiver_task(goober, log=True, log_content=log_content)

    try:
        value = int(text_buffer.decode())
    except:
        print("Error in decoding. reset to 0")
        value = 0

    print(f"{text_buffer}\n")

    return value







def get_formatted_payload(sender_ip, receiver_ip, payload_type, hash_bytes, body, zero_body):

    header = bytearray(
        [sender_ip,
        receiver_ip,
        payload_type,
        hash_bytes[0],
        hash_bytes[1],
        hash_bytes[2]]
    )

    buffer = copy.deepcopy(header)

    if (zero_body):
        buffer += bytearray(64 * rf_tx_header_length * [0])
    else:
        buffer += body


    return buffer



def get_padded_buffer(payload, cte):

    if len(payload) % cte == 0:
        payload_padded = copy.deepcopy(payload)

    else:

        needed_padding = cte - (len(payload) % cte)
        payload_padded = payload + bytearray(needed_padding * [0])

    return payload_padded



def bundle_dict_and_data(input_dict, input_data):
    ret = serialize_reuqest_json(input_dict)
    if input_data is not None:
        ret.extend(input_data)
    return ret

def serialize_reuqest_json(input):
    load = bytes(json.dumps(input), "utf-8")
    load_size = len(load)
    load_size_to_three_bytes = to_three_bytes(load_size)
    ret = bytearray(3)
    ret[0] = load_size_to_three_bytes[0]
    ret[1] = load_size_to_three_bytes[1]
    ret[2] = load_size_to_three_bytes[2]

    ret.extend(load)

    return ret

def unbundle_dict_and_data(input):
    dict_size = three_bytes_to_integer(input[0], input[1], input[2])
    dict_encoded_json = input[3: 3+dict_size]
    data = input[3+dict_size:]
    dict_decoded_json = dict_encoded_json.decode('utf-8')
    dict = json.loads(dict_decoded_json)
    return dict, data


def to_three_bytes(v):
    return (v >> 16) & 0xff, (v >> 8) & 0xff, (v >> 0) & 0xff

def to_four_bytes(v):
    return (v >> 24) & 0xff, (v >> 16) & 0xff, (v >> 8) & 0xff, (v >> 0) & 0xff


def three_bytes_to_integer(v1, v2, v3):
    return ((v1 & 0xff) << 16) + ((v2 & 0xff) << 8) + (v3 & 0xff)


def four_bytes_to_long(v0, v1, v2, v3):
    return ((v0 & 0xff) << 24) + ((v1 & 0xff) << 16) + ((v2 & 0xff) << 8) + (v3 & 0xff)


def decsribe_lora_signal_quality(rssi):

    """
    -120 <=     RSSI    <= -30
    weakest             strongest
    """

    return int(100 * (rssi + 120.0) / (120.0))



def describePackaging(total_bytes, package_size):

    if (total_bytes % package_size == 0):
        total_number_of_packs = int(total_bytes / package_size)

    else:
        total_number_of_packs = int(total_bytes / package_size) + 1

    return total_number_of_packs



def chunks(input, n):
    return [input[i:i + n] for i in range(0, len(input), n)]


def get_goobers_list():

    ports = list(port_list.comports())

    ret = []

    for port in ports:

        if 'STMicroelectronics Virtual COM Port' in port.description:

            if port.name not in already_assigned_goobers:

                ret.append(port.name)

    return ret



def log_post_transaction(side, action):

    instance_datetime = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S:%f')

    with open("./post_log.txt", "a") as f:

        f.write(f"{instance_datetime}, {side}, {action}\n")


