#!/usr/bin/env python3

import sys
import struct
import time
from pathlib import Path

import hid
from pynput.keyboard import Controller
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QCheckBox, QPushButton)

GUI_DIR = Path(__file__).resolve().parent.parent
PROFILE_PATH = GUI_DIR / "configs" / "profiles.json"

sys.path.insert(0, str(GUI_DIR))

from profile_manager import ProfileManager

VID = 0xCAFE
PID = 0x4004
NUM_CHANNELS = 4

'''
Lower = faster response, but more susceptible to jitter.
'''
DEBOUNCE_MS = 15

'''
How often Qt reads HID
'''
TIMER_MS = 3


class HIDReader:
    def __init__(self, vid, pid):
        self.device = hid.Device(vid, pid)
        self.device.nonblocking = True

    def read_adc_all_channels(self):
        adc_values = None

        while True:
            data = self.device.read(64)

            if not data:
                break

            if len(data) >= 8:
                adc_values = struct.unpack_from("<4H", bytes(data), 0)

        return adc_values

    def close(self):
        self.device.close()


class ProfileTypingMapper:
    def __init__(self, profile_manager, debounce_ms=20):
        self.profile_manager = profile_manager
        self.debounce_s = debounce_ms / 1000.0
        self.keyboard = Controller()

        self.last_raw_output = {}
        self.last_change_time = {}
        self.stable_output = {}
        self.has_fired = {}

        for ch in range(NUM_CHANNELS):
            self.last_raw_output[ch] = ""
            self.last_change_time[ch] = time.monotonic()
            self.stable_output[ch] = ""
            self.has_fired[ch] = False

    def get_channel_output_and_level(self, channel_id, adc_value):

        button_id = self.profile_manager.get_button_for_channel(channel_id)
        output, level = self.profile_manager.get_output_from_adc(button_id, adc_value)

        if output is None:
            output = ""

        return str(output), level, button_id

    def update(self, adc_values, typing_enabled=True):
        if adc_values is None:
            return []

        now = time.monotonic()
        typed_chars = []

        for ch in range(NUM_CHANNELS):
            if ch >= len(adc_values):
                continue

            adc = adc_values[ch]
            raw_output, level, button_id = self.get_channel_output_and_level(ch, adc)

            # Treat empty string as rest/no press.
            is_pressed = raw_output != ""

            # Raw interpreted output changed, so restart debounce timer.
            if raw_output != self.last_raw_output[ch]:
                self.last_raw_output[ch] = raw_output
                self.last_change_time[ch] = now
                continue

            # Wait until output is stable.
            if now - self.last_change_time[ch] < self.debounce_s:
                continue

            old_stable_output = self.stable_output[ch]
            self.stable_output[ch] = raw_output

            # Reset when released / no output.
            if not is_pressed:
                self.has_fired[ch] = False
                continue

            # Fire once per press.
            if not self.has_fired[ch] and self.stable_output[ch] != "":
                typed_chars.append(self.stable_output[ch])

                if typing_enabled:
                    self.keyboard.type(self.stable_output[ch])

                self.has_fired[ch] = True

        return typed_chars

    def get_debug_info(self, adc_values):
        """
        Returns per-channel debug strings for the GUI.
        """
        lines = []

        if adc_values is None:
            return ["No ADC data"]

        for ch in range(NUM_CHANNELS):
            if ch >= len(adc_values):
                continue

            adc = adc_values[ch]
            output, level, button_id = self.get_channel_output_and_level(ch, adc)

            display_output = output if output != "" else "none"

            lines.append(
                f"Channel {ch} -> Button {button_id}: "
                f"ADC={adc:4d} | level={level:.3f} | "
                f"output={display_output}"
            )

        return lines

    def reload_profile(self):
        self.profile_manager.reload()
        now = time.monotonic()

        for ch in range(NUM_CHANNELS):
            self.last_raw_output[ch] = ""
            self.last_change_time[ch] = now
            self.stable_output[ch] = ""
            self.has_fired[ch] = False


class TypingDemo(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Hall Effect Keypad Typing Demo")

        # Smaller demo window
        self.setFixedSize(430, 230)

        self.reader = HIDReader(VID, PID)
        self.profile_manager = ProfileManager(PROFILE_PATH)

        self.key_mapper = ProfileTypingMapper(
            profile_manager=self.profile_manager,
            debounce_ms=DEBOUNCE_MS,
        )

        self.title_label = QLabel("Hall Effect Keypad Typing Demo")
        self.title_label.setStyleSheet(
            "font-size: 22px; "
            "font-weight: bold;"
        )

        self.instructions_label = QLabel(
            "Demo Instructions:\n"
            "Press a Hall-effect key to type the mapped output."
        )
        self.instructions_label.setWordWrap(True)
        self.instructions_label.setStyleSheet("font-size: 13px;")

        self.typing_checkbox = QCheckBox("Enable typing")
        self.typing_checkbox.setChecked(True)

        self.reload_button = QPushButton("Reload Profile")
        self.reload_button.clicked.connect(self.reload_profile)

        self.reload_button.setFixedWidth(90)
        self.reload_button.setFixedHeight(28)

        self.profile_label = QLabel()
        self.profile_label.setStyleSheet(
            "font-size: 14px; "
            "font-weight: bold;"
        )

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.typing_checkbox)
        controls_layout.addStretch()
        controls_layout.addWidget(self.reload_button)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        layout.addWidget(self.title_label)
        layout.addWidget(self.instructions_label)
        layout.addLayout(controls_layout)
        layout.addWidget(self.profile_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.update_profile_label()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_demo)
        self.timer.start(TIMER_MS)

    def update_profile_label(self):
        active_id = self.profile_manager.get_active_profile_id()
        self.profile_label.setText(f"Active profile: {active_id}")

    def reload_profile(self):
        try:
            self.key_mapper.reload_profile()
            self.update_profile_label()
        except Exception as e:
            print(f"Reload failed: {e}")

    def update_demo(self):
        adc_values = self.reader.read_adc_all_channels()

        if adc_values is None:
            return

        self.key_mapper.update(
            adc_values,
            typing_enabled=self.typing_checkbox.isChecked(),
        )

    def closeEvent(self, event):
        self.reader.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    try:
        window = TypingDemo()
    except Exception as e:
        sys.exit(1)

    window.show()

    sys.exit(app.exec())
