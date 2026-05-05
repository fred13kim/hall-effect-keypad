from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from profile_customizer.mapping import validate_interval_mapping
from profile_customizer.models import IntervalMapping


class ThresholdEditor(QWidget):
    def __init__(self, mapping: IntervalMapping, on_change: Optional[Callable[[], None]] = None, parent=None,) -> None:
        super().__init__(parent)

        self._mapping = mapping
        self._on_change = on_change

        self._main_layout = QVBoxLayout(self)

        self._outputs_title = QLabel("Outputs")
        self._main_layout.addWidget(self._outputs_title)

        self._outputs_layout = QGridLayout()
        self._main_layout.addLayout(self._outputs_layout)

        self._breakpoints_title = QLabel("Breakpoints")
        self._main_layout.addWidget(self._breakpoints_title)

        self._breakpoints_layout = QVBoxLayout()
        self._main_layout.addLayout(self._breakpoints_layout)

        button_row = QHBoxLayout()

        self._add_output_btn = QPushButton("Add Output")
        self._remove_output_btn = QPushButton("Remove Output")

        self._add_output_btn.clicked.connect(self._add_output)
        self._remove_output_btn.clicked.connect(self._remove_output)

        button_row.addWidget(self._add_output_btn)
        button_row.addWidget(self._remove_output_btn)
        button_row.addStretch(1)

        self._main_layout.addLayout(button_row)

        self._rebuild()

    def set_mapping(self, mapping: IntervalMapping) -> None:
        """
        Use this when the selected profile/button changes.
        """
        self._mapping = mapping
        self._rebuild()

    def mapping(self) -> IntervalMapping:
        """
        Return the currently edited mapping.
        """
        validate_interval_mapping(self._mapping)
        return self._mapping

    def _rebuild(self) -> None:
        self._clear_layout(self._outputs_layout)
        self._clear_layout(self._breakpoints_layout)

        self._remove_output_btn.setEnabled(len(self._mapping.outputs) > 1)

        for index, output in enumerate(self._mapping.outputs):
            grid_row = index // 3
            grid_col = (index % 3) * 2

            label = QLabel(f"{index + 1}:")
            edit = QLineEdit(output)
            edit.setFixedWidth(70)

            edit.textChanged.connect(
                lambda text, i=index: self._update_output(i, text)
            )

            self._outputs_layout.addWidget(label, grid_row, grid_col)
            self._outputs_layout.addWidget(edit, grid_row, grid_col + 1)

        for index, breakpoint in enumerate(self._mapping.breakpoints):
            row = QHBoxLayout()

            left_output = self._mapping.outputs[index]
            right_output = self._mapping.outputs[index + 1]

            name_label = QLabel(f"{left_output} / {right_output}")
            name_label.setMinimumWidth(90)

            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(100)
            slider.setValue(int(float(breakpoint) * 100))

            spinbox = QDoubleSpinBox()
            spinbox.setRange(0.0, 1.0)
            spinbox.setDecimals(2)
            spinbox.setSingleStep(0.01)
            spinbox.setValue(float(breakpoint))
            spinbox.setFixedWidth(80)

            slider.valueChanged.connect(
                lambda value, i=index, box=spinbox: self._update_breakpoint_from_slider(i, value, box)
            )

            spinbox.valueChanged.connect(
                lambda value, i=index, s=slider: self._update_breakpoint_from_spinbox(i, value, s)
            )

            row.addWidget(name_label)
            row.addWidget(slider)
            row.addWidget(spinbox)

            self._breakpoints_layout.addLayout(row)

    def _update_output(self, index: int, text: str) -> None:
        self._mapping.outputs[index] = text
        self._notify_changed()
        self._rebuild()

    def _update_breakpoint_from_slider(self, index: int, value: int, spinbox: QDoubleSpinBox) -> None:
        new_value = value / 100.0

        spinbox.blockSignals(True)
        spinbox.setValue(new_value)
        spinbox.blockSignals(False)

        self._set_breakpoint(index, new_value)

    def _update_breakpoint_from_spinbox(self, index: int, value: float, slider: QSlider,) -> None:
        slider.blockSignals(True)
        slider.setValue(int(value * 100))
        slider.blockSignals(False)

        self._set_breakpoint(index, value)

    def _set_breakpoint(self, index: int, value: float) -> None:
        self._mapping.breakpoints[index] = float(value)
        self._mapping.breakpoints.sort(reverse=True)
        self._notify_changed()

    def _add_output(self) -> None:
        if self._mapping.breakpoints and self._mapping.breakpoints[-1] <= 0.01:
            return

        self._mapping.outputs.append("")

        if not self._mapping.breakpoints:
            self._mapping.breakpoints.append(0.50)
        else:
            last_breakpoint = self._mapping.breakpoints[-1]
            self._mapping.breakpoints.append(round(max(0.01, last_breakpoint - 0.10), 2))

        self._mapping.breakpoints.sort(reverse=True)

        self._notify_changed()
        self._rebuild()

    def _remove_output(self) -> None:
        if len(self._mapping.outputs) <= 1:
            return

        self._mapping.outputs.pop()

        if self._mapping.breakpoints:
            self._mapping.breakpoints.pop()

        self._notify_changed()
        self._rebuild()

    def _notify_changed(self) -> None:
        if self._on_change is not None:
            self._on_change()

    def _clear_layout(self, layout) -> None:
        while layout.count():
            item = layout.takeAt(0)

            widget = item.widget()
            child_layout = item.layout()

            if widget is not None:
                widget.deleteLater()
            elif child_layout is not None:
                self._clear_layout(child_layout)