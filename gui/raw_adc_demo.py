import sys
from collections import deque
from profile_manager import ProfileManager

import hid
import pyqtgraph as pg
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget,)


VID = 0xCAFE
PID = 0x4004

class HIDReader:
    def __init__(self, vid, pid):
        self.device = hid.Device(vid, pid)
        self.device.nonblocking = True

    def read_adc(self):
        # Assumming its structured as data[0] = low byte and data[1] = high byte

        adc_value = None
        while True:
            data = self.device.read(64)

            if not data:
                break

            if len(data) >= 2:
                adc_value = data[0] | (data[1] << 8)
            
        return adc_value

    def close(self):
        self.device.close()

class RawADCDemo(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Hall Effect Keypad - Raw ADC Demo")
        self.resize(800, 500)

        self.reader = HIDReader(VID, PID)

        self.profile_manager = ProfileManager(
            profile_path="configs/profiles.json",
            active_profile_id="1"
        )

        self.adc_channel = "0"

        self.samples = deque(maxlen=200)

        self.value_label = QLabel("ADC Value: ---")
        self.value_label.setStyleSheet("font-size: 28px; font-weight: bold;")

        self.state_label = QLabel("State: ---")
        self.state_label.setStyleSheet("font-size: 22px;")

        self.plot = pg.PlotWidget()
        self.plot.setYRange(450, 800)
        self.plot.setXRange(0, 199, padding=0)
        self.plot.setLabel("left", "ADC Value")
        self.plot.setLabel("bottom", "Sample")
        self.plot.showGrid(x=True, y=True)

        self.curve = self.plot.plot([], [], pen=pg.mkPen(width=3))

        self.profile_manager = ProfileManager(
            profile_path="configs/profiles.json",
            active_profile_id="1"
        )

        layout = QVBoxLayout()
        layout.addWidget(self.value_label)
        layout.addWidget(self.state_label)
        layout.addWidget(self.plot)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_adc)
        self.timer.start(5)  # update every 5 ms

    def classify_value(self, value):
        output, level = self.profile_manager.get_output_from_adc(
            self.button_id,
            value
        )

        return output, level

    def update_adc(self):
        value = self.reader.read_adc()

        if value is None:
            return

        button_id = self.profile_manager.get_button_for_channel(self.adc_channel)

        output, level = self.profile_manager.get_output_from_adc(
            button_id,
            value
        )

        self.value_label.setText(f"ADC Value: {value}")
        self.state_label.setText(f"Output: {output} | Level: {level:.2f}")

        self.samples.append(value)
        y = list(self.samples)
        x = list(range(len(y)))
        self.curve.setData(x, y)

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