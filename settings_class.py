import toolkit as tk
import os
import json
import hashlib

class Settings:
    def __init__(self):

        self.frequency_options = {}

        for i in range(902, 929):
            self.frequency_options[str(i)] = i

        self.top_blocks_count_options = {
            "Dynamic (Default)" :  0,
            "5 blocks":             5,
            "15 blocks":            15,
            "20 blocks":            20,
            "30 blocks":            30,
            "50 blocks":            50,
            "64 blocks (Full Frame)": 64,
        }

        self.image_quality_options = {
            "5 (Lowest Quality, Fastest)" : 5,
            "10":10,
            "15 (Default)": 15,
            "20": 20,
            "25": 25,
            "30": 30,
            "60": 60,
            "90 (Highest Quality, Slowest)": 90,
        }

        self.hash_bytes_starting_pos = 10

        self.reload()



    def reload(self):
        with open(os.path.join(tk.root_path, tk.settings_file_name), 'r') as f:
            self.dict = json.load(f)

        self.aes_key =  self.dict['aes_key']

        self.frequency = self.frequency_options[self.dict['frequency']]
        self.top_blocks_count = self.top_blocks_count_options[self.dict['top_blocks_count']]
        self.image_quality = self.image_quality_options[self.dict['image_quality']]

        m = hashlib.sha256()
        m.update(bytes.fromhex(self.aes_key))

        self.hash = m.digest().hex()
        self.dict['hash'] = self.hash

    def update(self, dict):
        self.reload()

        for key, value in dict.items():
            self.dict[key] = value

        with open(os.path.join(tk.root_path, tk.settings_file_name), 'w') as f:
            f.write(json.dumps(self.dict))




    def get_buffer(self):

        hash_value = bytes.fromhex(self.hash)

        body = bytearray(tk.rf_tx_body_length * [0])

        body[0] = int(self.frequency) - 902

        body[1] = 7
        body[2] = 9
        body[3] = 4
        body[4] = 8
        body[5] = 9
        body[6] = 100
        body[7] = 18

        body[self.hash_bytes_starting_pos + 0] = hash_value[0]
        body[self.hash_bytes_starting_pos + 1] = hash_value[1]
        body[self.hash_bytes_starting_pos + 2] = hash_value[2]


        return tk.get_formatted_payload(sender_ip = 0, receiver_ip = 0, payload_type = tk.payload_type_settings, hash_bytes = hash_value, body = body, zero_body = False)


