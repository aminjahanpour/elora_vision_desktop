import os
import time

import greeting_toolkit
import toolkit

import copy
import bin_toolkit
import json
import aes_cipher
import traceback
import goober_class
from tqdm import tqdm
import session_class

from playsound import playsound

receiver_verbose = 1





def main_receiver_loop(receiver_goober_port):

    try:

        goober = goober_class.Goober(receiver_goober_port)
        goober.set_up()
        while True:
            receiver_task(goober)

    except Exception as exc:
        print(traceback.format_exc())


def receiver_task(goober, log=False, log_content=None):

    recv_prefix = f"**** Recv Class ({goober.role}): "

    if receiver_verbose>0: print(recv_prefix + "1- waiting for a greeting...")


    while True:
        usb_buffer_received = goober.usb_device_serial.read(toolkit.usb_data_buffer_len)

        if len(usb_buffer_received) == toolkit.usb_data_buffer_len:

            if greeting_toolkit.is_greeting(usb_buffer_received):

                if receiver_verbose>0: print(recv_prefix + "2- got a greeting ...")

                break
            else:
                pass

    if log:
        toolkit.log_post_transaction(log_content, "recv greeting")

    gt = greeting_toolkit.Greeting(usb_buffer_received)

    if receiver_verbose>0:
        print(f"\tpayload bytes: {gt.payload_bytes_count} ({gt.payload_bytes_count / 64} USB packets)")

        if gt.include_gps:
            print(f"\t\tgps size  : {gt.gps_buffer_size}")
        if gt.include_text:
            print(f"\t\ttext size : {gt.text_buffer_size}")
        if gt.include_image:
            print(f"\t\timage size: {gt.image_buffer_size}")
        if gt.include_voice:
            print(f"\t\tvoice size: {gt.voice_buffer_size}")



    signal_quality = toolkit.decsribe_lora_signal_quality(gt.rssi)

    signal_info = {"snr": gt.snr, 'rssi': gt.rssi, 'signal_quality':signal_quality, 'payload_size': gt.payload_bytes_count - 30}
    with open(os.path.join(toolkit.root_path, toolkit.received_signal_info_file_name), 'w') as f:
        f.write(json.dumps(signal_info))



    total_packets_count = toolkit.describePackaging(gt.payload_bytes_count, 64)


    payload_from_usb = bytearray((total_packets_count * 64) * [0])


    if receiver_verbose>0: print(recv_prefix + "confirm the greeting")
    bytes_written_count = goober.usb_device_serial.write(toolkit.usb_buffer_confirmation)

    assert bytes_written_count == toolkit.usb_data_buffer_len

    if receiver_verbose>0: print(recv_prefix + "3- starting to receiving frame data")




    if receiver_verbose>0: print(recv_prefix + "asking for full packet")

    for idx in tqdm(range(total_packets_count)):

        if receiver_verbose == 2: print(f'idx:{idx + 1} from {total_packets_count}', end=' ')



        usb_buffer_received_len = 0

        while usb_buffer_received_len != 64:

            usb_buffer_received = goober.usb_device_serial.readall()

            usb_buffer_received_len = len(usb_buffer_received)


            if receiver_verbose == 2:
                if usb_buffer_received_len > 0:
                    print(recv_prefix + f'{usb_buffer_received_len}', end=' ')




        payload_from_usb[idx * 64 : (idx+1) * 64] = usb_buffer_received

        if receiver_verbose>1: print(recv_prefix + " confirm the full packet")
        bytes_written_count = goober.usb_device_serial.write(toolkit.usb_buffer_confirmation)

        assert bytes_written_count == toolkit.usb_data_buffer_len

        time.sleep(1 / 1000)


    payload_from_usb = payload_from_usb[:gt.payload_bytes_count]





    if receiver_verbose>0: print(recv_prefix + "4- got all the data")


    if len(payload_from_usb) == 0:
        print(recv_prefix + "ERROR: len(payload_from_usb) is 0     !!!")
        return

    if len(payload_from_usb) % 16 != 0:
        print(recv_prefix + "Warning: len(payload_from_usb) % 16 not equal to 0     !!!")



    with open(toolkit.received_encrypted_payload_file_name, "wb") as binary_file:
        binary_file.write(payload_from_usb)


    if receiver_verbose>0: print(recv_prefix + "5- decrypting data...")

    # decrypting the payload
    toolkit.settings.reload()
    payload = aes_cipher.decrypt(payload_from_usb, bytearray.fromhex(toolkit.settings.dict['aes_key']))
    # payload = payload_from_usb

    """
    splitting the payload
    """
    gps_buffer = bytearray()
    text_buffer = bytearray()
    voice_buffer = bytearray()
    image_buffer = bytearray()

    payload_starting_index = 0

    if (gt.include_gps):
        gps_buffer = payload[payload_starting_index : payload_starting_index + gt.gps_buffer_size]
        payload_starting_index += gt.gps_buffer_size

    if (gt.include_text):
        text_buffer = payload[payload_starting_index: payload_starting_index + gt.text_buffer_size]
        payload_starting_index += gt.text_buffer_size


    if (gt.include_voice):
        voice_buffer = payload[payload_starting_index : payload_starting_index + gt.voice_buffer_size]
        payload_starting_index += gt.voice_buffer_size

    if (gt.include_image):
        image_buffer = payload[payload_starting_index : payload_starting_index + gt.image_buffer_size]
        payload_starting_index += gt.image_buffer_size

    assert payload_starting_index <= len(payload)

    if (gt.include_gps):
        try:
            if receiver_verbose > 0: print(recv_prefix + "6- extracting GPS data...")

            gps_data = get_gps_data(gps_buffer)

            # update the GPS data only if they are valid
            with open(os.path.join(toolkit.root_path, toolkit.received_gps_file_name), 'w') as f:
                f.write(json.dumps(gps_data))
        except Exception as exc:
            print(traceback.format_exc())


    if gt.include_text:
        try:
            with open(os.path.join(toolkit.root_path, toolkit.received_text_file_name), 'wb') as f:
                f.write(text_buffer)
        except Exception as exc:
            print(traceback.format_exc())






    if gt.include_image:
        try:
            if receiver_verbose>0: print(recv_prefix + "6- storing decrypted JPEG data...")
            with open(os.path.join(toolkit.root_path, toolkit.received_frame_file_name), 'wb') as f:
                f.write(image_buffer)

            toolkit.image_load_error_printed_already = False

        except Exception as exc:
            print(traceback.format_exc())


        # session.save_frame(len(payload_from_usb), gps_data)


    if gt.include_voice:
        try:
            with open(os.path.join(toolkit.root_path, toolkit.received_audio_file_name), 'wb') as f:
                f.write(voice_buffer)
            playsound(toolkit.received_audio_file_name)
        except Exception as exc:
            print(traceback.format_exc())


    if receiver_verbose>0: print(recv_prefix + "8- saving payload into the session...")

    if receiver_verbose>0: print(recv_prefix + "9- done with this payload")

    return text_buffer


def get_gps_data(gps_bytearray):

    gps_bitstring = ''.join(f'{z:08b}' for z in gps_bytearray)

    gps_fp_bits = 24

    ret = {}

    gps_rec_counter = 0
    for b in toolkit.chunks(gps_bitstring, 48):
        if gps_rec_counter == 0: ret['accuracy_rec'] = bin_toolkit.bit_string_to_float(b, gps_fp_bits)
        if gps_rec_counter == 1: ret['altitude_rec'] = bin_toolkit.bit_string_to_float(b, gps_fp_bits)
        if gps_rec_counter == 2: ret['latitude_rec'] = bin_toolkit.bit_string_to_float(b, gps_fp_bits)
        if gps_rec_counter == 3: ret['longitude_rec'] = bin_toolkit.bit_string_to_float(b, gps_fp_bits)
        if gps_rec_counter == 4: ret['speed_rec'] = bin_toolkit.bit_string_to_float(b, gps_fp_bits)

        gps_rec_counter += 1


    if (ret['latitude_rec'] < -360.0) or (ret['latitude_rec'] > 360.0): ret['latitude_rec'] = 0

    if (ret['longitude_rec'] < -360.0) or (ret['longitude_rec'] > 360.0): ret['longitude_rec'] = 0

    if (ret['altitude_rec'] < 0.0) or (ret['altitude_rec'] > 10000.0): ret['altitude_rec'] = 0

    if (ret['accuracy_rec'] < 0.0): ret['accuracy_rec'] = 0

    if (ret['speed_rec'] < 0.0): ret['speed_rec'] = 0


    return ret




if __name__ == '__main__':
    main_receiver_loop()