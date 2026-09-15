import qrcode
import os
import bitstring
import toolkit
import json

def genarate_new_key_qr():

    new_aes_key = os.urandom(32).hex()

    save_new_key_in_settings(new_aes_key)

    save_qr_code_png(new_aes_key)


def save_qr_code_png(aes_key):
    qrcode.make(aes_key).save(os.path.join(toolkit.root_path, toolkit.aes_qr_code_file_name))


def save_new_key_in_settings(aes_key):
    if (os.path.isfile(os.path.join(toolkit.root_path, toolkit.settings_file_name))):
        with open(os.path.join(toolkit.root_path, toolkit.settings_file_name), 'r') as f:
            settings = json.load(f)
    else:
        settings = {}

    settings['aes_key'] = aes_key

    with open(os.path.join(toolkit.root_path, toolkit.settings_file_name), 'w') as f:
        f.write(json.dumps(settings))



if __name__ == '__main__':
    genarate_new_key_qr()