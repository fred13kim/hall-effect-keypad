import sys
from pathlib import Path

PARENT_DIR = Path(__file__).resolve().parent.parent

if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

from profile_manager import ProfileManager
config_path = PARENT_DIR / "configs" / "profiles.json"
pm = ProfileManager(config_path)

for adc in [270, 320, 400, 500]:
    button_id = pm.get_button_for_channel("0")
    output, level = pm.get_output_from_adc(button_id, adc)
    print(adc, "level:", round(level, 2), "button:", button_id, "output:", output)