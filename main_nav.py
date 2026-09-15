import webbrowser


class Mixin:


    def select_frame_by_name(self, name):
        # set button color for selected button

        # self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.key_sync_button.configure(fg_color=("gray75", "gray25") if name == "key_sync" else "transparent")
        self.receiver_button.configure(fg_color=("gray75", "gray25") if name == "receiver" else "transparent")
        self.settings_button.configure(fg_color=("gray75", "gray25") if name == "settings" else "transparent")
        self.sender_button.configure(fg_color=("gray75", "gray25") if name == "sender" else "transparent")

        # show selected frame
        # if name == "home":
        #     self.home_frame.grid(row=0, column=1, sticky="nsew")
        # else:
        #     self.home_frame.grid_forget()


        if name == "key_sync":
            self.key_sync_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.key_sync_frame.grid_forget()

        if name == "receiver":
            self.receiver_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.receiver_frame.grid_forget()

        if name == "settings":
            self.settings_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.settings_frame.grid_forget()

        if name == "sender":
            self.sender_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.sender_frame.grid_forget()



    def home_button_event(self):
        self.select_frame_by_name("home")

    def settings_button_event(self):
        self.select_frame_by_name("settings")

    def key_sync_button_event(self):
        self.select_frame_by_name("key_sync")


    def receiver_frame_button_event(self):
        self.select_frame_by_name("receiver")
        self.refresh_receiver_goobers_list()

    def sender_frame_button_event(self):
        self.select_frame_by_name("sender")
        self.refresh_sender_goobers_list()


    def goto_parniatech(self):
        webbrowser.open("https://www.parniatech.com", new=0, autoraise=True)

    def goto_docs(self):
        webbrowser.open("https://elora-vision-docs.readthedocs.io/en/latest/", new=0, autoraise=True)
