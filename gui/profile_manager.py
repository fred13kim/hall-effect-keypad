import json


class ProfileManager:
    def __init__(self, profile_path, active_profile_id="1"):
        self.profile_path = profile_path
        self.active_profile_id = str(active_profile_id)
        self.profile_data = self.load_profile()

        self.min_adc = 270
        self.rest_adc = 490

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
        Convert ADC to normalized press level.

        Since pressing lowers ADC:
        adc = rest_adc -> level = 1.0
        adc = min_adc  -> level = 0.0
        """
        if self.min_adc == self.rest_adc:
            return 1.0

        level = (adc_value - self.min_adc) / (self.rest_adc - self.min_adc)
        return max(0.0, min(1.0, level))

    def get_output_from_level(self, button_id, level):

        button_config = self.get_button_config(button_id)

        breakpoints = button_config["breakpoints"]
        outputs = button_config["outputs"]

        if len(outputs) != len(breakpoints) + 1:
            raise ValueError(
                f"Button {button_id} has {len(breakpoints)} breakpoints "
                f"but {len(outputs)} outputs. Expected outputs = {len(breakpoints)+1}."
            )

        output_index = 0

        for breakpoint in breakpoints:
            if level < breakpoint:
                output_index += 1
            else:
                break

        return outputs[output_index]

    def get_output_from_adc(self, button_id, adc_value):
        level = self.adc_to_level(adc_value)
        output = self.get_output_from_level(button_id, level)

        return output, level