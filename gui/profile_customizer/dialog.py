from __future__ import annotations

import json
from dataclasses import asdict
from typing import Dict

from PySide6.QtCore import QSignalBlocker
from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from profile_customizer.threshold_editor import ThresholdEditor
from profile_customizer.defaults import default_profiles
from profile_customizer.mapping import validate_interval_mapping
from profile_customizer.models import IntervalMapping, Profile
from profile_customizer.paths import PROFILES_PATH
from profile_customizer.persistence import load_profiles, save_profiles


class ProfileCustomizerDialog(QDialog):
    num_buttons = 4
    num_profiles = 4

    def __init__(self) -> None:
        super().__init__()

        self._profiles: Dict[int, Profile] = load_profiles(self.num_profiles)
        self._current_profile_id = 1
        self._current_button_id = 1
        self._loading_ui = False

        self._create_menu()
        self._create_profile_group()
        self._create_main_layout()

        self.setWindowTitle("Profile Customizer — Profile 1")
        self._load_profile_into_ui(1)

    def _create_main_layout(self) -> None:
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.setMenuBar(self._menu_bar)
        main_layout.addWidget(self._profile_group)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

    def _create_menu(self) -> None:
        self._menu_bar = QMenuBar()

        self._file_menu = QMenu("&File", self)
        self._save_action = self._file_menu.addAction("&Save Profiles")
        self._exit_action = self._file_menu.addAction("E&xit")
        self._menu_bar.addMenu(self._file_menu)

        self._save_action.triggered.connect(self._on_save_profiles)
        self._exit_action.triggered.connect(self.accept)

    def _create_profile_group(self) -> None:
        self._profile_group = QGroupBox("")
        outer_layout = QVBoxLayout()

        outer_layout.addLayout(self._build_profile_selector_row())
        outer_layout.addLayout(self._build_button_selector_row())
        outer_layout.addLayout(self._build_mapping_form())
        outer_layout.addLayout(self._build_apply_reset_row())

        self._profile_group.setLayout(outer_layout)

    def _build_profile_selector_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.addWidget(QLabel("Active profile:"))

        self._profile_btn_group = QButtonGroup(self)
        self._profile_btn_group.setExclusive(True)
        self._profile_btn_group.idClicked.connect(self._on_profile_button_clicked)

        for profile_id in range(1, self.num_profiles + 1):
            button = QPushButton(str(profile_id))
            button.setCheckable(True)
            button.setChecked(profile_id == 1)
            self._profile_btn_group.addButton(button, profile_id)
            row.addWidget(button)

        row.addStretch(1)
        return row

    def _build_button_selector_row(self) -> QHBoxLayout:
        row = QHBoxLayout()

        self._button_group = QButtonGroup(self)
        self._button_group.setExclusive(True)
        self._button_group.idClicked.connect(self._on_button_selected)

        for button_id in range(1, self.num_buttons + 1):
            button = QPushButton(f"Key {button_id}")
            button.setCheckable(True)
            button.setChecked(button_id == 1)
            self._button_group.addButton(button, button_id)
            row.addWidget(button)

        row.addStretch(1)
        return row

    # def _build_mapping_form(self) -> QFormLayout:
    #     form = QFormLayout()

    #     self._mapping_json = QTextEdit()
    #     self._mapping_json.setPlaceholderText(
    #         '{\n  "breakpoints": [0.75, 0.5],\n'
    #         '  "outputs": ["A", "B", "C"]\n}'
    #     )
    #     form.addRow("Mapping config (JSON):", self._mapping_json)

    #     return form

    def _build_mapping_form(self) -> QFormLayout:
        form = QFormLayout()

        mapping = self._profiles[self._current_profile_id].buttons[self._current_button_id]
        self._threshold_editor = ThresholdEditor(mapping)

        form.addRow("Thresholds / outputs:", self._threshold_editor)

        return form
    
    def _build_apply_reset_row(self) -> QHBoxLayout:
        row = QHBoxLayout()

        self._apply_btn = QPushButton("Save mappings to this Key")
        self._apply_btn.clicked.connect(self._on_apply_mapping)
        row.addWidget(self._apply_btn)

        self._reset_btn = QPushButton("Reset this profile")
        self._reset_btn.clicked.connect(self._on_reset_profile)
        row.addWidget(self._reset_btn)

        row.addStretch(1)
        return row

    def _on_save_profiles(self) -> None:
        self._commit_ui_to_profile(self._current_profile_id)
        try:
            save_profiles(self._profiles, active_profile=self._current_profile_id)
            QMessageBox.information(self, "Saved", f"Saved to {PROFILES_PATH.resolve()}")
        except Exception as error:
            QMessageBox.critical(self, "Save failed", f"Could not save profiles:\n{error}")

    def _on_profile_button_clicked(self, profile_id: int) -> None:
        self._commit_ui_to_profile(self._current_profile_id)
        self._current_profile_id = profile_id
        self._load_profile_into_ui(profile_id)
        self.setWindowTitle(f"Profile Customizer — Profile {profile_id}")

    def _on_button_selected(self, button_id: int) -> None:
        self._commit_ui_to_profile(self._current_profile_id)
        self._current_button_id = button_id
        self._load_profile_into_ui(self._current_profile_id)

    def _load_profile_into_ui(self, profile_id: int) -> None:
        self._loading_ui = True
        try:
            mapping = self._profiles[profile_id].buttons[self._current_button_id]
            self._threshold_editor.set_mapping(mapping)
        finally:
            self._loading_ui = False

    def _commit_ui_to_profile(self, profile_id: int) -> None:
        """Commit threshold editor state only if valid."""

        if self._loading_ui:
            return

        try:
            mapping = self._threshold_editor.mapping()
            self._profiles[profile_id].buttons[self._current_button_id] = mapping
        except Exception:
            return

    def _on_apply_mapping(self) -> None:
        if self._loading_ui:
            return

        try:
            mapping = self._threshold_editor.mapping()
            self._profiles[self._current_profile_id].buttons[self._current_button_id] = mapping
            QMessageBox.information(self, "Applied", "Mapping applied to this Key.")
        except Exception as error:
            QMessageBox.critical(self, "Invalid mapping", f"Could not apply mapping:\n{error}")

    def _on_reset_profile(self) -> None:
        profile_id = self._current_profile_id
        self._profiles[profile_id] = default_profiles(self.num_profiles, self.num_buttons)[profile_id]
        self._load_profile_into_ui(profile_id)

    @staticmethod
    def _mapping_from_json_text(text: str) -> IntervalMapping:
        obj = json.loads(text) if text else {}
        mapping = IntervalMapping(
            breakpoints=list(obj.get("breakpoints", [])),
            outputs=list(obj.get("outputs", [])),
        )
        validate_interval_mapping(mapping)
        return mapping

    def accept(self) -> None:
        self._commit_ui_to_profile(self._current_profile_id)
        try:
            save_profiles(self._profiles, active_profile=self._current_profile_id)
        except Exception:
            pass
        super().accept()
