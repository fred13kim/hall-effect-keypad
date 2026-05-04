from profile_manager import ProfileManager

pm = ProfileManager("configs/profiles.json")

for adc in [550, 635, 690, 720]:
    button_id = pm.get_button_for_channel("0")
    output, level = pm.get_output_from_adc(button_id, adc)
    print(adc, "level:", round(level, 2), "button:", button_id, "output:", output)