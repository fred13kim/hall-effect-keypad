import json


class ProfileManager:
    def __init__(self, profile_path, active_profile_id="1"):
        self.profile_path = profile_path
        self.active_profile_id = str(active_profile_id)
        self.profile_data = self.load_profile()

        # Temporary calibration values for now.
        # Later, these should also come from the profile or calibration UI.
        self.rest_adc = 550
        self.max_adc = 720

    def load_profile(self):
        with open(self.profile_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def reload(self):
        self.profile_data = self.load_profile()

    def set_active_profile(self, profile_id):
        self.active_profile_id = str(profile_id)

    def get_active_profile(self):
        active_profile_id = self.get_active_profile_id()
        return self.profile_data["profiles"][active_profile_id]

    def get_button_for_channel(self, channel_id):
        channel_id = str(channel_id)
        return self.profile_data["hardware"]["adc_channels"][channel_id]

    def get_active_profile_id(self):
        return self.profile_data.get("active_profile", self.active_profile_id)

    def get_button_config(self, button_id):
        button_id = str(button_id)
        return self.get_active_profile()["buttons"][button_id]

    def adc_to_level(self, adc_value):
        """
        Converts raw ADC value to a 0.0–1.0 press level.

        For now:
            550 -> 0.0
            720 -> 1.0

        Later, rest_adc and max_adc should come from calibration/profile settings.
        """
        if self.max_adc == self.rest_adc:
            return 0.0

        level = (adc_value - self.rest_adc) / (self.max_adc - self.rest_adc)
        return max(0.0, min(1.0, level))

    def get_output_from_level(self, button_id, level):
        """
        Example:
            breakpoints = [0.75, 0.5]
            outputs     = ["A", "B", "C"]

        Mapping:
            level >= 0.75              -> "A"
            0.5 <= level < 0.75        -> "B"
            level < 0.5                -> "C"
        """
        button_config = self.get_button_config(button_id)

        breakpoints = button_config["breakpoints"]
        outputs = button_config["outputs"]

        for index, breakpoint in enumerate(breakpoints):
            if level >= breakpoint:
                return outputs[index]

        return outputs[-1]

    def get_output_from_adc(self, button_id, adc_value):
        level = self.adc_to_level(adc_value)
        output = self.get_output_from_level(button_id, level)

        return output, level