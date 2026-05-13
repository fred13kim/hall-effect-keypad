#!/usr/bin/env python3
import sys
import random
import time
import struct

import hid

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget


VID = 0xCAFE
PID = 0x4004

NUM_CHANNELS = 4

PRESS_THRESHOLD = 465
RELEASE_THRESHOLD = 465


class HIDReader:
    def __init__(self, vid, pid):
        self.device = hid.Device(vid, pid)
        self.device.nonblocking = True

    def read_adc_all_channels(self):
        """Drain the HID queue and return the latest 4-channel reading."""
        adc_values = None

        while True:
            data = self.device.read(64)

            if not data:
                break

            if len(data) >= 8:  # 4 × uint16 = 8 bytes
                adc_values = struct.unpack_from("<4H", bytes(data), 0)

        return adc_values

    def close(self):
        self.device.close()


class ReactionTest(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Hall Effect Reaction Test")
        self.resize(800, 500)

        self.hid_reader = HIDReader(VID, PID)

        self.state = "waiting_to_start"
        self.green_time = None

        # Track pressed/released state separately for each Hall sensor.
        self.key_pressed = [False] * NUM_CHANNELS

        self.label = QLabel("Press any Hall effect key to start")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setStyleSheet("font-size: 38px; font-weight: bold; color: white;")

        central = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        central.setLayout(layout)
        self.setCentralWidget(central)

        self.set_red_screen("Press any Hall effect key to start")

        self.poll_timer = QTimer()
        self.poll_timer.timeout.connect(self.poll_keypad)
        self.poll_timer.start(5)

        self.reaction_timer = QTimer()
        self.reaction_timer.setSingleShot(True)
        self.reaction_timer.timeout.connect(self.turn_green)

    def set_red_screen(self, text):
        self.setStyleSheet("background-color: red;")
        self.label.setText(text)

    def set_green_screen(self, text):
        self.setStyleSheet("background-color: green;")
        self.label.setText(text)

    def start_round(self):
        self.state = "red_waiting"
        self.green_time = None

        self.set_red_screen("Wait for green...")

        delay_ms = random.randint(1500, 4000)
        self.reaction_timer.start(delay_ms)

    def turn_green(self):
        self.state = "green_ready"
        self.green_time = time.perf_counter()

        self.set_green_screen("PRESS NOW!")

    def finish_round(self):
        reaction_time = time.perf_counter() - self.green_time
        reaction_ms = reaction_time * 1000

        self.state = "result"

        self.set_red_screen(
            f"Reaction time: {reaction_ms:.1f} ms\n\n"
            "Release and press any key to restart"
        )

    def false_start(self):
        self.state = "result"
        self.reaction_timer.stop()

        self.set_red_screen("Too early!\n\n" "Release and press any key to restart")

    def update_key_states(self, adc_values):
        """
        Convert 4 analog ADC values into clean pressed/released states
        using hysteresis.

        Returns True only when at least one channel newly becomes pressed.
        """

        new_press_detected = False

        for channel, adc_value in enumerate(adc_values):
            previous_pressed = self.key_pressed[channel]

            if not self.key_pressed[channel] and adc_value >= PRESS_THRESHOLD:
                self.key_pressed[channel] = True

            elif self.key_pressed[channel] and adc_value <= RELEASE_THRESHOLD:
                self.key_pressed[channel] = False

            new_press = self.key_pressed[channel] and not previous_pressed

            if new_press:
                new_press_detected = True

        return new_press_detected

    def poll_keypad(self):
        adc_values = self.hid_reader.read_adc_all_channels()

        if adc_values is None:
            return

        new_press = self.update_key_states(adc_values)

        if not new_press:
            return

        if self.state == "waiting_to_start":
            self.start_round()

        elif self.state == "red_waiting":
            self.false_start()

        elif self.state == "green_ready":
            self.finish_round()

        elif self.state == "result":
            self.start_round()

    def closeEvent(self, event):
        self.hid_reader.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = ReactionTest()
    window.show()

    sys.exit(app.exec())
