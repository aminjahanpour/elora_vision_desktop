import os
import json

import main_receiver
import sender_unit
import toolkit
import key_sync
import webbrowser
import customtkinter
from PIL import Image
import receiver_unit
from threading import Thread
import multiprocessing
import webbrowser

import main_nav
import main_key_sync
import main_receiver
import main_settings
import main_sender



customtkinter.set_appearance_mode("Light")  # Modes: "System" (standard), "Dark", "Light"


class App(customtkinter.CTk,
          main_nav.Mixin,
          main_key_sync.Mixin,
          main_receiver.Mixin,
          main_settings.Mixin,
          main_sender.Mixin
          ):
    def __init__(self):
        super().__init__()


        self.title("Elora Vision")
        self.geometry("1000x740")
        self.resizable(width=False,height=False)

        self.receiver_view_is_refreshing = False

        self.root_path = os.path.dirname(os.path.realpath(__file__))
        self.google_map_link=""

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.image_path = os.path.join(os.path.join(os.getcwd(), "assets"), "image")

        self.home_image         = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "home.png")),     size=(20, 20))
        self.settings_image     = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "settings.png")), size=(20, 20))
        self.key_image          = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "key.png")),      size=(20, 20))
        self.logo_image         = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "logo.png")),     size=(140, 40))
        self.sender_image     = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "camera.png")),  size=(20, 20))
        self.receiver_image     = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "monitor.png")),  size=(20, 20))
        self.location_image     = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "location.png")), size=(20, 20))
        self.save_image     = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "save.png")), size=(20, 20))
        self.play_image     = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "play.png")), size=(20, 20))
        self.stop_image     = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "stop.png")), size=(20, 20))
        self.sync_image     = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "sync.png")), size=(20, 20))
        self.error_large_image     = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "error.png")), size=(640, 480))
        self.refresh_image     = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "refresh.png")), size=(20, 20))
        self.docs_image     = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "manual.png")), size=(20, 20))









        # Create navigation frame
        # -----------------------------------------------------------------------------------------------------------------

        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(7, weight=1)


        # logo
        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="", image=self.logo_image,
                                                             compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)



        # Home frame
        # self.home_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Home",
        #                                                fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
        #                                                image=self.home_image, anchor="w", command=self.home_button_event)
        # self.home_button.grid(row=1, column=0, sticky="ew")



        # Key Sync frame
        self.key_sync_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Key Sync",
                                                       fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                       image=self.key_image, anchor="w", command=self.key_sync_button_event)
        self.key_sync_button.grid(row=2, column=0, sticky="ew")



        # Settings frame
        self.settings_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Settings",
                                                       fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                       image=self.settings_image, anchor="w", command=self.settings_button_event)
        self.settings_button.grid(row=3, column=0, sticky="ew")




        # Sender Device frame
        self.sender_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Sender Unit",
                                                       fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                       image=self.sender_image, anchor="w", command=self.sender_frame_button_event)
        self.sender_button.grid(row=4, column=0, sticky="ew")



        # Receiver Device frame
        self.receiver_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Receiver Unit",
                                                       fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                       image=self.receiver_image, anchor="w", command=self.receiver_frame_button_event)
        self.receiver_button.grid(row=5, column=0, sticky="ew")




        # Docs Device frame
        self.docs_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Read the Docs",
                                                       fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                       image=self.docs_image, anchor="w", command=self.goto_docs)
        self.docs_button.grid(row=6, column=0, sticky="ew")
































        # Create Frames
        # -----------------------------------------------------------------------------------------------------------------



        # create home frame content
        # self.home_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        # self.home_frame.grid_columnconfigure(0, weight=1)
        #
        # self.home_welcome_label = customtkinter.CTkLabel(self.home_frame, text="Welcome to Elora Vision Project desktop app\nThis is an open software/open hardware project facilitating affordable remote vision for those how need it.\nDocumentations are avaiable at https://elora-vision-docs.readthedocs.io")
        # self.home_welcome_label.grid(row=0, column=0, padx=20, pady=10)
        #
        # self.home_welcome_label = customtkinter.CTkLabel(self.home_frame, text="Here is a quick review over how to start receiving and displaying data\n1- Make sure you have set up your keys. This step needs to be done only once. (click on Key Sync on the left)\n2-If you wish to adjust the settings, click on Settings on the left. You can only do this before starting to receive data frame.\n3-Connect the Goober via USB cable.\n4- Click on Receiver Unit and the click on Play.")
        # self.home_welcome_label.grid(row=1, column=0, padx=20, pady=10)




        # create key sync frame content

        self.key_sync_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.key_sync_frame.grid_columnconfigure(0, weight=1)

        self.display_aes_key_qr_code_image()


        self.key_sync_display_current_key_label = customtkinter.CTkLabel(self.key_sync_frame, text="")
        self.key_sync_display_current_key_label.grid(row=1, column=0, padx=20, pady=10)
        self.display_current_key_button_event()

        self.key_sync_frame_generate_new_key_button = customtkinter.CTkButton(self.key_sync_frame, text="Generate a New Key", image=self.key_image, command=self.generate_new_key_button_event)
        self.key_sync_frame_generate_new_key_button.grid(row=3, column=0, padx=20, pady=10)


























        # create settings frame content
        self.settings_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        settings_frame_rows = 10
        settings_frame_cols = 5
        self.settings_frame.grid_columnconfigure(5, weight=1)
        self.settings_frame.grid_rowconfigure(10, weight=1)

        for i in range(settings_frame_cols):
            self.settings_frame.grid_columnconfigure(i, weight=1)

        for i in range(settings_frame_rows - 1):
            self.settings_frame.grid_rowconfigure(i, weight=1)
        self.settings_frame.grid_rowconfigure(settings_frame_rows, weight=100)


        # frequency
        self.settings_frame_label = customtkinter.CTkLabel(self.settings_frame, text="Frequency (MHz):")
        self.settings_frame_label.grid(row=3, column=0, padx=20, pady=10, sticky="e")

        self.frequency_option_menu = customtkinter.CTkOptionMenu(self.settings_frame,
                                                                 values=list(toolkit.settings.frequency_options.keys()))
        self.frequency_option_menu.grid(row=3, column=1, padx=20, pady=10, sticky="w")


        # top blocks count

        self.settings_frame_label = customtkinter.CTkLabel(self.settings_frame, text="Number of Blocks in the Image:")
        self.settings_frame_label.grid(row=4, column=0, padx=20, pady=10, sticky="e")

        self.top_blocks_count_optionmenu = customtkinter.CTkOptionMenu(self.settings_frame,
                                                   values=list(toolkit.settings.top_blocks_count_options.keys()))
        self.top_blocks_count_optionmenu.grid(row=4, column=1, padx=20, pady=10, sticky="w")
        self.top_blocks_count_optionmenu.set("Dynamic (Default)")


        # image Quality
        self.settings_frame_label = customtkinter.CTkLabel(self.settings_frame, text="Image Quality:")
        self.settings_frame_label.grid(row=5, column=0, padx=20, pady=10, sticky="e")

        self.image_quality_optionmenu = customtkinter.CTkOptionMenu(self.settings_frame,
                                                   values=list(toolkit.settings.image_quality_options.keys()))
        self.image_quality_optionmenu.grid(row=5, column=1, padx=20, pady=10, sticky="w")
        self.image_quality_optionmenu.set("15 (Default)")





        # save button
        self.save_settings_button = customtkinter.CTkButton(self.settings_frame, text="Save Settings", image=self.save_image, command=self.save_settings_cammand)
        self.save_settings_button.grid(row=9, column=4, sticky="wens")


        self.update_settings_view()


































        # create sender frame contents
        self.sender_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.sender_frame.grid_columnconfigure(0, weight=1)
        self.sender_frame.grid_rowconfigure(3, weight=1)




        self.sender_frame_row_0 = customtkinter.CTkFrame(self.sender_frame, fg_color="transparent")
        self.sender_frame_row_0.grid(row=0, column=0, sticky="nwse", padx=5, pady=5)
        for i in range(1):
            self.sender_frame_row_0.grid_columnconfigure(i, weight=1)









        self.sender_frame_row_1 = customtkinter.CTkFrame(self.sender_frame, fg_color="transparent")
        self.sender_frame_row_1.grid(row=1, column=0, sticky="nwse", padx=5, pady=5)

        for i in range(4):
            self.sender_frame_row_1.grid_columnconfigure(i, weight=1)

        self.settings_frame_label = customtkinter.CTkLabel(self.sender_frame_row_1, text="Attached Goobers:")
        self.settings_frame_label.grid(row=0, column=0, pady=10, sticky="e")

        self.attached_sender_goobers = customtkinter.CTkOptionMenu(self.sender_frame_row_1, values=[])
        self.attached_sender_goobers.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        self.sender_frame_set_up_button = customtkinter.CTkButton(self.sender_frame_row_1, text="Refresh", width=40, command=self.refresh_sender_goobers_list)
        self.sender_frame_set_up_button.grid(row=0, column=2, sticky="w")

        self.sender_frame_set_up_button = customtkinter.CTkButton(self.sender_frame_row_1, text="Sync with Goober", image=self.refresh_image, command=self.set_up_sender_goober_button_event)
        self.sender_frame_set_up_button.grid(row=0, column=3)




        self.sender_frame_row_2 = customtkinter.CTkFrame(self.sender_frame, fg_color="transparent")
        self.sender_frame_row_2.grid(row=2, column=0, sticky="nwse", padx=5, pady=5)

        for i in range(2):
            self.sender_frame_row_2.grid_columnconfigure(i, weight=1)

        self.sender_frame_start_sending_button = customtkinter.CTkButton(self.sender_frame_row_2, text="Start Camera", image=self.play_image, command=self.start_sending_button_event)
        self.sender_frame_start_sending_button.grid(row=0, column=0,padx=5, sticky="e")

        self.sender_frame_stop_sending_button = customtkinter.CTkButton(self.sender_frame_row_2, text="Stop Camera", image=self.stop_image, command=self.stop_sending_button_event)
        self.sender_frame_stop_sending_button.grid(row=0, column=1,padx=5, sticky="w")








        self.sender_frame_row_3 = customtkinter.CTkFrame(self.sender_frame, fg_color="transparent")
        self.sender_frame_row_3.grid(row=3, column=0, sticky="nwse", padx=5, pady=5)

        for i in range(2):
            self.sender_frame_row_3.grid_columnconfigure(i, weight=1)


        self.label_001 = customtkinter.CTkLabel(self.sender_frame_row_3, text='Payload Size:')
        self.label_001.grid(row=0, column=0,padx=5, sticky="e")
        self.sender_payload_size_label = customtkinter.CTkLabel(self.sender_frame_row_3, text='(Kb)')
        self.sender_payload_size_label.grid(row=0, column=1,padx=5, sticky="w")






        self.setup_sender_frame_view()



































        # create receiver frame contents

        self.receiver_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.receiver_frame.grid_columnconfigure(0, weight=1)
        self.receiver_frame.grid_rowconfigure(5, weight=1)


        # receiver_frame_row_0
        self.receiver_frame_row_0 = customtkinter.CTkFrame(self.receiver_frame, fg_color="transparent")
        self.receiver_frame_row_0.grid(row=0, column=0, sticky="nwse", padx=5, pady=5)
        for i in range(3):
            self.receiver_frame_row_0.grid_columnconfigure(i, weight=1)

        self.update_received_frame_view()




        # receiver_frame_row_1
        self.receiver_frame_row_1 = customtkinter.CTkFrame(self.receiver_frame, fg_color="transparent")
        self.receiver_frame_row_1.grid(row=1, column=0, sticky="nwse", padx=5, pady=5)

        for i in range(4):
            self.receiver_frame_row_1.grid_columnconfigure(i, weight=1)

        self.settings_frame_label = customtkinter.CTkLabel(self.receiver_frame_row_1, text="Attached Goobers:")
        self.settings_frame_label.grid(row=0, column=0, pady=10, sticky="e")

        self.attached_receiver_goobers = customtkinter.CTkOptionMenu(self.receiver_frame_row_1, values=[])
        self.attached_receiver_goobers.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        self.receiver_frame_set_up_button = customtkinter.CTkButton(self.receiver_frame_row_1, text="Refresh", width=40, image=self.refresh_image, command=self.refresh_receiver_goobers_list)
        self.receiver_frame_set_up_button.grid(row=0, column=2, sticky="w")

        self.receiver_frame_set_up_button = customtkinter.CTkButton(self.receiver_frame_row_1, text="Sync with Goober", image=self.sync_image, command=self.set_up_receiver_goober_button_event)
        self.receiver_frame_set_up_button.grid(row=0, column=3)




        # receiver_frame_row_2
        self.receiver_frame_row_2 = customtkinter.CTkFrame(self.receiver_frame, fg_color="transparent")
        self.receiver_frame_row_2.grid(row=2, column=0, sticky="nwse", padx=5, pady=5)

        for i in range(3):
            self.receiver_frame_row_2.grid_columnconfigure(i, weight=1)

        self.receiver_frame_start_receiving_button = customtkinter.CTkButton(self.receiver_frame_row_2, text="Play", image=self.play_image, command=self.start_receiving_button_event)
        self.receiver_frame_start_receiving_button.grid(row=0, column=1, padx=5, sticky="e")

        self.receiver_frame_stop_receiving_button = customtkinter.CTkButton(self.receiver_frame_row_2, text="Stop", image=self.stop_image, command=self.stop_receiving_button_event)
        self.receiver_frame_stop_receiving_button.grid(row=0, column=2, padx=5, sticky="w")


        self.message_text_label = customtkinter.CTkLabel(self.receiver_frame_row_2, text='message text', font=customtkinter.CTkFont(weight="bold"))
        self.message_text_label.grid(row=0, column=3, sticky="e", padx=5)





        # receiver_frame_row_3
        self.receiver_frame_row_3 = customtkinter.CTkFrame(self.receiver_frame, fg_color="transparent")
        self.receiver_frame_row_3.grid(row=3, column=0, sticky="nwse", padx=5, pady=5)
        for i in range(6):
            self.receiver_frame_row_3.grid_rowconfigure(i, weight=1)

        for i in range(6):
            self.receiver_frame_row_3.grid_columnconfigure(i, weight=1)


        self.label_001 = customtkinter.CTkLabel(self.receiver_frame_row_3, text='Latitude:', font=customtkinter.CTkFont(weight="bold"))
        self.label_001.grid(row=0, column=0, sticky="e", padx=5)
        self.latitude_label = customtkinter.CTkLabel(self.receiver_frame_row_3, text='')
        self.latitude_label.grid(row=0, column=1, sticky="w")


        self.label_002 = customtkinter.CTkLabel(self.receiver_frame_row_3, text='Longitude:', font=customtkinter.CTkFont(weight="bold"))
        self.label_002.grid(row=0, column=2, sticky="e", padx=5)
        self.longitude_label = customtkinter.CTkLabel(self.receiver_frame_row_3, text='')
        self.longitude_label.grid(row=0, column=3, sticky="w")

        # self.label_0003 = customtkinter.CTkLabel(self.receiver_frame_row_3, text='open url:')
        # self.label_0003.grid(row=2, column=1)
        self.receiver_frame_google_map_button = customtkinter.CTkButton(self.receiver_frame_row_3,  text="Open in Google Map", image=self.location_image, command=self.open_in_google_map_button_event)
        self.receiver_frame_google_map_button.grid(row=0, column=5,padx=5, pady=5)


        self.label_003 = customtkinter.CTkLabel(self.receiver_frame_row_3, text='Altitude:', font=customtkinter.CTkFont(weight="bold"))
        self.label_003.grid(row=1, column=0, sticky="e", padx=5)
        self.altitude_label = customtkinter.CTkLabel(self.receiver_frame_row_3, text='')
        self.altitude_label.grid(row=1, column=1, sticky="w")


        self.label_004 = customtkinter.CTkLabel(self.receiver_frame_row_3, text='Accuracy:', font=customtkinter.CTkFont(weight="bold"))
        self.label_004.grid(row=1, column=2, sticky="e", padx=5)
        self.accuracy_label = customtkinter.CTkLabel(self.receiver_frame_row_3, text='')
        self.accuracy_label.grid(row=1, column=3, sticky="w")


        self.label_005 = customtkinter.CTkLabel(self.receiver_frame_row_3, text='Speed:', font=customtkinter.CTkFont(weight="bold"))
        self.label_005.grid(row=1, column=4, sticky="e", padx=5)
        self.speed_label = customtkinter.CTkLabel(self.receiver_frame_row_3, text='')
        self.speed_label.grid(row=1, column=5, sticky="w")


        self.label_009 = customtkinter.CTkLabel(self.receiver_frame_row_3, text='Payload Size:', font=customtkinter.CTkFont(weight="bold"))
        self.label_009.grid(row=2, column=0, sticky="e", padx=5)
        self.payload_size_label = customtkinter.CTkLabel(self.receiver_frame_row_3, text='')
        self.payload_size_label.grid(row=2, column=1, sticky="w")

        self.label_006 = customtkinter.CTkLabel(self.receiver_frame_row_3, text='SNR:', font=customtkinter.CTkFont(weight="bold"))
        self.label_006.grid(row=2, column=2, sticky="e", padx=5)
        self.snr_label = customtkinter.CTkLabel(self.receiver_frame_row_3, text='')
        self.snr_label.grid(row=2, column=3, sticky="w")

        self.label_007 = customtkinter.CTkLabel(self.receiver_frame_row_3, text='RSSI:', font=customtkinter.CTkFont(weight="bold"))
        self.label_007.grid(row=2, column=4, sticky="e", padx=5)
        self.rssi_label = customtkinter.CTkLabel(self.receiver_frame_row_3, text='')
        self.rssi_label.grid(row=2, column=5, sticky="w")





        self.receiver_frame_row_5 = customtkinter.CTkFrame(self.receiver_frame, fg_color="transparent")
        self.receiver_frame_row_5.grid(row=5, column=0, sticky="nwse", padx=5, pady=5)

        self.receiver_frame_row_5.grid_columnconfigure(0, weight=1)
        self.receiver_frame_row_5.grid_columnconfigure(1, weight=1)
        self.receiver_frame_row_5.grid_columnconfigure(2, weight=10)

        self.label_008 = customtkinter.CTkLabel(self.receiver_frame_row_5, text='Signal Strength:')
        self.label_008.grid(row=0, column=0, sticky="e", padx=5)

        self.signal_quality_label = customtkinter.CTkLabel(self.receiver_frame_row_5, text='')
        self.signal_quality_label.grid(row=0, column=1, sticky="w")

        self.progressbar_signal_quality = customtkinter.CTkProgressBar(self.receiver_frame_row_5, orientation='horizontal', mode='determinate')
        self.progressbar_signal_quality.grid(row=0, column=2, sticky="ew", padx=(20, 20), pady=(1, 1))
        self.progressbar_signal_quality.set(0)







        # select default frame

        self.receiver_frame_stop_receiving_button.configure(state="disabled")

        self.select_frame_by_name("key_sync")







if __name__ == "__main__":
    app = App()
    app.iconbitmap(os.path.join(os.path.join(os.path.join(os.getcwd(), "assets"), "image"), "icon.ico"))


    app.mainloop()

