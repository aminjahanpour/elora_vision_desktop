import os
import toolkit
import key_sync
import customtkinter
from PIL import Image


class Mixin:


    def display_aes_key_qr_code_image(self):
        try:
            self.aes_key_qr_code_image = customtkinter.CTkImage(Image.open(os.path.join(toolkit.root_path, toolkit.aes_qr_code_file_name)), size=(300, 300))
            self.key_sync_large_image_label = customtkinter.CTkLabel(self.key_sync_frame, text="", image=self.aes_key_qr_code_image)
            self.key_sync_large_image_label.grid(row=0, column=0, padx=20, pady=10)
        except:
            pass


    def generate_new_key_button_event(self):
        key_sync.genarate_new_key_qr()
        self.display_aes_key_qr_code_image()
        self.display_current_key_button_event()


    def display_current_key_button_event(self):
        try:
            toolkit.settings.reload()
            self.key_sync_display_current_key_label.configure(text=toolkit.settings.dict['aes_key'])
        except:
            pass
