import json
import os

import cv2

import aes_cipher
import color_ranger
import greeting_toolkit
import toolkit
import io
import traceback
import numpy as np
import copy
import goober_class
from tqdm import tqdm



video_handler = cv2.VideoCapture(0)


def main_sender_loop(sender_goober_port):
    try:
        goober = goober_class.Goober(sender_goober_port)
        goober.set_up()

        top_block_counter_idx = 0

        sender_task(goober, top_block_counter_idx)

    except Exception as exc:
        errors = io.StringIO()
        traceback.print_exc(file=errors)  # Instead of printing directly to stdout, the result can be further processed
        contents = str(errors.getvalue())
        print(contents)
        errors.close()


def sender_task(goober, top_block_counter_idx):
    ret, cv2_rgb_img = video_handler.read()

    if ret:

        cv2_rgb_img = cv2.resize(cv2_rgb_img, (320, 240), interpolation=cv2.INTER_NEAREST)


        top_blocks_count = copy.deepcopy(toolkit.settings.top_blocks_count)
        if top_blocks_count == 0:
            top_blocks_count = list(toolkit.settings.top_blocks_count_options.values())[top_block_counter_idx]



        if toolkit.settings.top_blocks_count < 64:
            mask_array = color_ranger.range_colors(
                cv2_rgb_img,
                hue_bins_to_remove_percentage=95,
                top_blocks_count=top_blocks_count,
            )
            masked_array = cv2.bitwise_and(cv2_rgb_img, cv2_rgb_img, mask=mask_array)
        else:
            masked_array = cv2_rgb_img


        toolkit.settings.reload()
        is_success, buffer = cv2.imencode(".jpg", masked_array, [cv2.IMWRITE_JPEG_QUALITY, toolkit.settings.image_quality])
        jpeg_byte_array = buffer.tobytes()

        with open(os.path.join(toolkit.root_path, toolkit.sent_frame_file_name), 'wb') as f:
            f.write(jpeg_byte_array)

        # send(goober, text_buffer=bytes("yellow", "utf8"), jpeg_byte_array=jpeg_byte_array)
        send(goober, text_buffer=bytes("yellow bones", "utf8"), jpeg_byte_array=None)


def send(goober, text_buffer, jpeg_byte_array):

    send_prefix = f"#### Send Class ({goober.role}): "


    include_gps = False
    include_text = not text_buffer is None
    include_voice = False
    include_image = not jpeg_byte_array is None

    unencrypted_payload = bytearray()


    if include_text:

        unencrypted_payload.extend(text_buffer)

    if include_image:
        unencrypted_payload.extend(jpeg_byte_array)



    toolkit.settings.reload()

    payload = aes_cipher.encrypt_bytes(unencrypted_payload, key = bytearray.fromhex(toolkit.settings.dict['aes_key']), iv = np.random.bytes(16))


    with open(os.path.join(toolkit.root_path, toolkit.sent_payload_info_file_name), 'w') as f:
        f.write(json.dumps({"payload_size": len(payload)}))

    text_buffer_size = len(text_buffer) if include_text else 0
    voice_buffer_size = 0
    camera_image_buffer_size = len(jpeg_byte_array) if include_image else 0


    usb_greeting_tx_body_buffer = greeting_toolkit.build_greeting_payload(
        total_number_of_bytes_to_send=len(payload),

        include_gps=False,
        include_text=include_text,
        include_voice=False,
        include_image=include_image,

        text_buffer_size=text_buffer_size,
        voice_buffer_size=voice_buffer_size,
        camera_image_buffer_size=camera_image_buffer_size
    )


    hash_value = bytes.fromhex(toolkit.settings.hash)

    usb_greeting_tx_buffer = toolkit.get_formatted_payload(
        sender_ip = 0,
        receiver_ip = 0,
        payload_type = toolkit.payload_type_greeting,
        hash_bytes = hash_value,
        body = usb_greeting_tx_body_buffer,
        zero_body = False
    )


    goober.usb_device_serial.write(usb_greeting_tx_buffer)


    total_number_of_bytes_to_send = len(payload)

    total_number_of_packets = toolkit.describePackaging(total_number_of_bytes_to_send, toolkit.usb_data_buffer_len)

    print(send_prefix + "uploading the payload to Goober..")

    """
        send the greeting and then
        wait only for a short time to see if the Goober responds
        to the greeting. otherwise skip the frame
    """


    payload_padded = toolkit.get_padded_buffer(payload, 64)


    for idx in tqdm(range(total_number_of_packets)):

        packet_bytes = payload_padded[idx * toolkit.usb_data_buffer_len: (idx + 1) * toolkit.usb_data_buffer_len]

        goober.usb_device_serial.write(packet_bytes)


    print(send_prefix + "Done")
    print(send_prefix + "waiting for TX finish report..")




    while True:

        usb_buffer_received = goober.usb_device_serial.readall()

        if len(usb_buffer_received) == 64:
            break


    print(send_prefix + "Tx finish report received. All done.")



