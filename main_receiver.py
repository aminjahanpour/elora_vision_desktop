import os
import json
import traceback

import goober_class
import toolkit
import webbrowser
import customtkinter
from PIL import Image
import receiver_unit
import multiprocessing


class Mixin:


    def start_receiving_button_event(self):


        if toolkit.receiver_goober.setup_already:
            toolkit.receiver_thread = multiprocessing.Process(target=receiver_unit.main_receiver_loop, args=(toolkit.receiver_goober.port,))
            toolkit.receiver_thread.start()

            # self.settings_button.configure(state="disabled")
            self.receiver_frame_start_receiving_button.configure(state="disabled")

            self.receiver_frame_stop_receiving_button.configure(state="enabled")


            # start a heart beat
            self.receiver_view_is_refreshing = True
            self.after(300, self.update_all_received_fields)

        else:
            print("Goober is not set up")


    def stop_receiving_button_event(self):
        if toolkit.receiver_thread is not None:
            toolkit.receiver_thread.terminate()
        assert toolkit.receiver_goober.release_usb()


        self.receiver_frame_start_receiving_button.configure(state="enabled")
        self.receiver_frame_stop_receiving_button.configure(state="disabled")

        # self.settings_button.configure(state="enabled")

        self.receiver_view_is_refreshing = False
        print("Stoped Receiving.")


    def update_all_received_fields(self):

        self.update_received_frame_view()
        self.update_received_gps_info()
        self.update_received_signal_info()
        self.update_received_text_message()

        if self.receiver_view_is_refreshing:
            self.after(500, self.update_all_received_fields)




    def update_received_frame_view(self):
        try:
            img = Image.open(os.path.join(toolkit.root_path, toolkit.received_frame_file_name))
            self.received_frame_image_view = customtkinter.CTkImage(img, size=( 2* img.width, 2 * img.height))
            self.bg_image_label = customtkinter.CTkLabel(self.receiver_frame, image=self.received_frame_image_view, text='')
            self.bg_image_label.grid(row=0, column=0, padx=5, pady=5)
            toolkit.image_load_error_printed_already = False

        except:
            self.received_frame_image_view = self.error_large_image
            self.bg_image_label = customtkinter.CTkLabel(self.receiver_frame, image=self.received_frame_image_view, text='')
            self.bg_image_label.grid(row=0, column=0)
            if not toolkit.image_load_error_printed_already:
                print(traceback.format_exc())
                toolkit.image_load_error_printed_already = True

    def update_received_gps_info(self):
        try:
            with open(os.path.join(toolkit.root_path, toolkit.received_gps_file_name), 'r') as f:
                gps_info_dict = json.load(f)
                self.latitude_label.configure(text= f"{round(gps_info_dict['latitude_rec'], 7)}")
                self.longitude_label.configure(text= f"{round(gps_info_dict['longitude_rec'], 7)}")
                self.accuracy_label.configure(text= f"{round(gps_info_dict['accuracy_rec'],2 )} (m)")
                self.altitude_label.configure(text= f"{round(gps_info_dict['altitude_rec'], 2)} (m)")
                self.speed_label.configure(text= f"{round(gps_info_dict['speed_rec'], 1)} (m/s)")

                self.google_map_link = f"http://www.google.com/maps/place/{gps_info_dict['latitude_rec']},{gps_info_dict['longitude_rec']}"

        except:
            # print("error update_received_gps_info")
            pass



    def update_received_signal_info(self):
        try:
            with open(os.path.join(toolkit.root_path, toolkit.received_signal_info_file_name), 'r') as f:
                gps_info_dict = json.load(f)
                self.snr_label.configure(text= f"{gps_info_dict['snr']}")
                self.rssi_label.configure(text= f"{gps_info_dict['rssi']} (dBm)")
                self.payload_size_label.configure(text= f"{round(gps_info_dict['payload_size']/1024,3)} (Kb)")
                self.signal_quality_label.configure(text= f"{gps_info_dict['signal_quality']} %")
                self.progressbar_signal_quality.start()
                self.progressbar_signal_quality.set(gps_info_dict['signal_quality']/100.0)
                self.progressbar_signal_quality.stop()

        except:
            # print("error update_received_signal_info")
            pass




    def update_received_text_message(self):

        with open(os.path.join(toolkit.root_path, toolkit.received_text_file_name), 'rb') as f:

            text_message_bytes = f.read()
        text_message_text=''

        try:

            text_message_text = text_message_bytes.decode()


        except:

            text_message_text = text_message_bytes


        finally:
            self.message_text_label.configure(text=text_message_text)

    def open_in_google_map_button_event(self):
        try:
            print("ASD")
            webbrowser.open_new(self.google_map_link)
        except:
            pass

    def set_up_receiver_goober_button_event(self):
        available_goobers = toolkit.get_goobers_list()

        chosen_receiver_goober = self.attached_receiver_goobers.get()

        if len(available_goobers) > 0 and chosen_receiver_goober in available_goobers:

            toolkit.receiver_goober = goober_class.Goober(chosen_receiver_goober)
            assert toolkit.receiver_goober.set_up()

            assert toolkit.receiver_goober.save_settings()

            assert toolkit.receiver_goober.release_usb()

        else:
            print("Error: Goober not reachable")


    def refresh_receiver_goobers_list(self):
        available_goobers = toolkit.get_goobers_list()

        self.attached_receiver_goobers.configure(values=available_goobers)

        if len(available_goobers) > 0:
            self.attached_receiver_goobers.set(available_goobers[0])

