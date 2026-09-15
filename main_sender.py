import json
import multiprocessing
import os
import threading

import customtkinter
from PIL import Image, ImageTk

import sender_unit
import toolkit
import time

import goober_class


class Mixin:

    def setup_sender_frame_view(self):

        # camera view
        self.camera_view = customtkinter.CTkLabel(self.sender_frame_row_0, text="", width=640, height=480)

        self.camera_view.grid(row=0, column=0)


        # sent image view
        self.update_sent_image_view()



        self.sender_frame_start_sending_button.configure(state="disabled")
        self.sender_frame_stop_sending_button.configure(state="disabled")



    def update_sender_view_labels(self):

        with open(os.path.join(toolkit.root_path, toolkit.sent_payload_info_file_name), 'r') as f:
            sender_frame_info_dict = json.load(f)
            self.sender_payload_size_label.configure(text=f"{round(sender_frame_info_dict['payload_size'] / 1024, 3)} (Kb)")


    def update_sent_image_view(self):
        # print("update_sent_image_view")
        try:
            self.sent_frame_image_view = customtkinter.CTkImage(Image.open(self.root_path + "/" + toolkit.sent_frame_file_name), size=(640, 480))

        except:
            self.sent_frame_image_view = self.error_large_image

        finally:
            self.sent_image_view_label = customtkinter.CTkLabel(self.sender_frame_row_0, image=self.sent_frame_image_view, text='')
            self.sent_image_view_label.grid(row=0, column=0)

            # update labels
            self.update_sender_view_labels()

            self.after(300, self.update_sent_image_view)



    def start_sending_button_event(self):

        toolkit.sender_main_thread = multiprocessing.Process(target=sender_unit.main_sender_loop, args=(toolkit.sender_goober.port,))

        toolkit.sender_main_thread.start()


    def set_up_sender_goober_button_event(self):

        available_goobers = toolkit.get_goobers_list()

        chosen_sender_goober = self.attached_sender_goobers.get()

        if len(available_goobers) > 0 and chosen_sender_goober in available_goobers:

            toolkit.sender_goober = goober_class.Goober(chosen_sender_goober)

            assert toolkit.sender_goober.set_up()

            assert toolkit.sender_goober.tell_goober_we_are_senders()
            time.sleep(2)
            assert toolkit.sender_goober.save_settings()
            assert toolkit.sender_goober.release_usb()

            self.sender_frame_start_sending_button.configure(state="enabled")
            self.sender_frame_stop_sending_button.configure(state="enabled")

            toolkit.already_assigned_goobers.append(chosen_sender_goober)

        else:
            print("Error: Goober not reachable")




    def stop_sending_button_event(self):
        toolkit.allowed_to_stream = False

        if toolkit.sender_main_thread is not None:
            toolkit.sender_main_thread.terminate()


    def refresh_sender_goobers_list(self):

        available_goobers = toolkit.get_goobers_list()

        self.attached_sender_goobers.configure(values=available_goobers)

        if len(available_goobers) > 0:
            self.attached_sender_goobers.set(available_goobers[0])

