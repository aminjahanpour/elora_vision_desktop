import base64

from Cryptodome.Cipher import AES




IV_LENGTH = 16


# iv_hex_string = "603deb1015ca71be2b73aef0857d7781"
iv_hex_string = "d437708cd695e430eae418e3a4c47071"
key_hex_string = "7d54ba990f3d69a068d437708cd695e430eae418e3a4c4707139edb2f0955594"

key = bytearray.fromhex(key_hex_string)
iv = bytearray.fromhex(iv_hex_string)


def pad_str(s):
    pad_count = (IV_LENGTH - len(s) % IV_LENGTH)
    pad_char = chr(IV_LENGTH - len(s) % IV_LENGTH)
    padded = s + pad_count * pad_char
    return padded


def unpad_str(s):
    pad_char = s[-1:]
    pad_count = ord(pad_char)
    return s[0 : -pad_count]



def pad_byte(s):
    pad_count = (IV_LENGTH - len(s) % IV_LENGTH)
    pad_byte = (IV_LENGTH - len(s) % IV_LENGTH).to_bytes(1,'big')
    padded = s + pad_count * pad_byte
    return padded



def bytearray_to_string(input):
    cipher_string_b = base64.b64encode(input)
    return bytes.decode(cipher_string_b)

def encrypt_string(message_string, key, iv):
    message_padded = pad_str(message_string)

    cipher = AES.new(key, AES.MODE_CBC, iv)
    message_padded_encode = message_padded.encode("utf8")

    message_padded_encode_encrypted = cipher.encrypt(message_padded_encode)

    cipher_bytes = iv + message_padded_encode_encrypted
    return cipher_bytes


def encrypt_bytes(message_bytes, key, iv):
    message_padded = pad_byte(message_bytes)

    cipher = AES.new(key, AES.MODE_CBC, iv)
    # message_padded_encode = message_padded.encode("utf8")

    message_padded_encode_encrypted = cipher.encrypt(message_padded)

    cipher_bytes = iv + message_padded_encode_encrypted
    return cipher_bytes


def decrypt(iv_plus_cipher_bytes, key):
    iv = iv_plus_cipher_bytes[:IV_LENGTH]
    cipher_bytes = iv_plus_cipher_bytes[IV_LENGTH:]

    cipher = AES.new(key, AES.MODE_CBC, iv)

    padded_decrpted_string_b = cipher.decrypt(cipher_bytes)
    return padded_decrpted_string_b
    # unpadded_decrpted_string_b = unpad(padded_decrpted_string_b)
    # decrypted_string = bytes.decode(unpadded_decrpted_string_b)

    # return decrypted_string


def test():

    with open("./received_frame.jpg", "rb") as f:
        plain_bytes = f.read()

    ecrypted = encrypt_bytes(plain_bytes, key, iv)


    with open("./test_decrypted.jpg", "wb") as f:
        f.write(decrypt(ecrypted, key))

    exit()



    plain_text = "M0993000353"

    cipher_bytes = encrypt_string(plain_text, key, iv)
    # print("CipherText: " + cipher_string)

    decrypted_bytes = decrypt(cipher_bytes, key)
    # print("DecryptedMessage: " + decrypted_string)
    assert unpad_str(bytes.decode(decrypted_bytes)) == plain_text


def main():
    with open("./received_encrypted_payload.txt", 'rb') as f:
        cipher_bytes = f.read()
        cipher_bytes_hex = cipher_bytes.hex()
        cipher_bytes_count = len(cipher_bytes)
        sdf=4


    with open("./received_frame_dec.jpg", 'wb') as f:
        decrypted_bytes = decrypt(cipher_bytes, key)
        f.write(decrypted_bytes[30:])


if __name__ == '__main__':
    test()
    # main()