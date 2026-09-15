import toolkit


class Mixin:

    def update_settings_view(self):
        self.frequency_option_menu.set(toolkit.settings.dict["frequency"])
        self.top_blocks_count_optionmenu.set(toolkit.settings.dict["top_blocks_count"])
        self.image_quality_optionmenu.set(toolkit.settings.dict["image_quality"])


    def save_settings_cammand(self):
        toolkit.settings.update({
            'frequency': self.frequency_option_menu.get(),
            'top_blocks_count': self.top_blocks_count_optionmenu.get(),
            'image_quality': self.image_quality_optionmenu.get()
        })

