#!/usr/bin/env python3
import sys
import struct
from collections import deque
from pathlib import Path

import hid
import pyqtgraph as pg
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow, QVBoxLayout, QPushButton, QHBoxLayout, QGridLayout, QWidget, QGroupBox)

# Script Paths
PARENT_DIR = Path(__file__).resolve().parent.parent

if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

from profile_manager import ProfileManager

VID = 0xCAFE
PID = 0x4004
NUM_CHANNELS = 4
CHANNEL_COLORS = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12"]

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
                adc_values = struct.unpack_from('<4H', bytes(data), 0)
        return adc_values

    def close(self):
        self.device.close()


class RawADCDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hall Effect Keypad – Multi-Channel ADC")
        self.resize(1000, 700)

        self.reader = HIDReader(VID, PID)
        config_path = PARENT_DIR / "configs" / "profiles.json"
        
        self.profile_manager = ProfileManager(
            profile_path=str(config_path),
            active_profile_id="1",
        )
        self.active_profile_label = QLabel()
        self.active_profile_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.reload_profile_btn = QPushButton("Reload Profile")
        self.reload_profile_btn.clicked.connect(self.reload_profile)

        # Per-channel state
        self.samples = [deque(maxlen=200) for _ in range(NUM_CHANNELS)]
        self.value_labels = []
        self.state_labels = []
        self.curves = []

        # Layout 
        root = QWidget()
        root_layout = QVBoxLayout(root)
        top_control_row = QHBoxLayout()
        top_control_row.addWidget(self.active_profile_label)
        top_control_row.addWidget(self.reload_profile_btn)
        top_control_row.addStretch(1)
        root_layout.addLayout(top_control_row)

        self.update_active_profile_label()

        # Top row: per-channel readout tiles
        readout_row = QHBoxLayout()
        for ch in range(NUM_CHANNELS):
            box = QGroupBox(f"Channel {ch}")
            box_layout = QVBoxLayout(box)

            val_lbl = QLabel("ADC: ---")
            val_lbl.setStyleSheet("font-size: 22px; font-weight: bold;")
            state_lbl = QLabel("Output: --- | Level: ---")
            state_lbl.setStyleSheet("font-size: 14px;")

            box_layout.addWidget(val_lbl)
            box_layout.addWidget(state_lbl)
            self.value_labels.append(val_lbl)
            self.state_labels.append(state_lbl)
            readout_row.addWidget(box)

        root_layout.addLayout(readout_row)

        # Bottom: 2×2 grid of plots
        plot_grid = QGridLayout()
        for ch in range(NUM_CHANNELS):
            plot = pg.PlotWidget(title=f"Channel {ch}")
            plot.setYRange(200, 600)          # 12-bit ADC ceiling
            plot.setXRange(0, 199, padding=0)
            plot.setLabel("left", "ADC")
            plot.setLabel("bottom", "Sample")
            plot.showGrid(x=True, y=True)
            curve = plot.plot(
                [], [],
                pen=pg.mkPen(color=CHANNEL_COLORS[ch], width=2),
            )
            self.curves.append(curve)
            plot_grid.addWidget(plot, ch // 2, ch % 2)

        plot_widget = QWidget()
        plot_widget.setLayout(plot_grid)
        root_layout.addWidget(plot_widget)

        self.setCentralWidget(root)

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_adc)
        self.timer.start(5)  # 5 ms  ~200 Hz poll
    
    def update_active_profile_label(self):
        active_profile = self.profile_manager.get_active_profile_id()
        self.active_profile_label.setText(f"Active Profile: {active_profile}")


    def reload_profile(self):
        self.profile_manager.reload()
        self.update_active_profile_label()

        active_profile = self.profile_manager.get_active_profile_id()
        print(f"Reloaded active profile: {active_profile}")

        for ch in range(NUM_CHANNELS):
            button_id = self.profile_manager.get_button_for_channel(str(ch))
            button_config = self.profile_manager.get_button_config(button_id)
    # Slot 
    def update_adc(self):
        values = self.reader.read_adc_all_channels()
        if values is None:
            return

        active_profile = self.profile_manager.get_active_profile_id()

        for ch, value in enumerate(values):
            button_id = self.profile_manager.get_button_for_channel(str(ch))
            output, level = self.profile_manager.get_output_from_adc(button_id, value)

            self.value_labels[ch].setText(f"ADC: {value}")
            self.state_labels[ch].setText(
                f"Profile {active_profile} | "
                f"Output: {output} "
            )

            self.samples[ch].append(value)
            y = list(self.samples[ch])
            self.curves[ch].setData(list(range(len(y))), y)

    def closeEvent(self, event):
        self.reader.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        window = RawADCDemo()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
