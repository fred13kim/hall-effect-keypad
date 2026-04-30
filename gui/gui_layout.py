from __future__ import annotations

import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Any, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
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
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
)
from PySide6.QtCore import QSignalBlocker

CONFIG_DIR = Path(__file__).resolve().parent / "configs"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
PROFILES_PATH = CONFIG_DIR / "profiles.json"

'''
ARCHITECTURE NOTES (Future Modifications)

Current design:
  - Profile = pure config
  - Mapping = stateless interval logic
  - UI edits JSON directly
  - Persistence versioned

Planned upgrades:
  [ ] Per-key mappings (Profile: Dict[key_id, IntervalMapping])
  [ ] Calibration layer (raw ADC -> normalized)
  [ ] Hysteresis (stateful mapping object)
  [ ] Nonlinear curves
  [ ] Multi-layer profiles
'''

'''
============================================================
PROFILE DATA MODEL  (PRIMARY EXTENSION POINT)
------------------------------------------------------------
To add anything like:
  - per-key mappings
  - calibration (raw ADC -> normalized)
  - nonlinear curves
  - hysteresis with state
  - layers / macros

Modify this section first

IMPORTANT: Keep this section PURE CONFIG DATA.
'''
@dataclass
class IntervalMapping:
    """
    # IMPORTANT:
    # Voltage is assumed normalized to [0,1].
    # If using raw ADC, add normalization BEFORE calling mapping.

    Piecewise interval mapping for v in [0,1].

    breakpoints: strictly decreasing list, e.g. [0.75, 0.50]
    outputs: length = len(breakpoints)+1, e.g. ["A","B","C"]

    Intervals (top-down):
      (breakpoints[0], 1]                       -> outputs[0]
      (breakpoints[1], breakpoints[0]]          -> outputs[1]
      ...
      [0, breakpoints[-1]]                      -> outputs[-1]
    """
    breakpoints: List[float]
    outputs: List[str]
    hysteresis: float = 0.0  # reserved for later; not used in mapping below


@dataclass
class Profile:
    """
    A Profile is a full layout/config set.
    It contains 4 physical buttons, each with its own IntervalMapping JSON.
    """
    buttons: Dict[int, IntervalMapping]  # keys: 1..4


# ----------------------------
# Validation + core mapping
# ----------------------------
def validate_interval_mapping(m: IntervalMapping) -> None:
    bps = m.breakpoints
    outs = m.outputs

    if any((not isinstance(b, (int, float))) for b in bps):
        raise ValueError("All breakpoints must be numbers.")
    if any((not isinstance(o, str)) for o in outs):
        raise ValueError("All outputs must be strings.")

    if len(outs) != len(bps) + 1:
        raise ValueError("outputs must have exactly len(breakpoints)+1 items.")

    # Strictly decreasing and within [0,1]
    prev = None
    for b in bps:
        if not (0.0 <= float(b) <= 1.0):
            raise ValueError("All breakpoints must be within [0, 1].")
        if prev is not None and not (prev > b):
            raise ValueError("breakpoints must be strictly decreasing (e.g. [0.75, 0.5]).")
        prev = b

    if not (0.0 <= float(m.hysteresis) <= 0.5):
        raise ValueError("hysteresis must be within [0, 0.5].")


def map_voltage_to_output(v: float, m: IntervalMapping) -> str:
    """
    Stateless mapping (no hysteresis). Good skeleton.
    Later: swap this with a stateful hysteresis mapper without changing UI/profile schema much.

    This function defines how normalized voltage v in [0,1] maps to a symbolic output.
    
    To add anything along the lines of:
      - hysteresis (stateful transitions)
      - smoothing / filtering
      - nonlinear curves
      - time-dependent behavior
    
    Replace or wrap THIS function. (The UI and persistence should not need to change)
    """
    if not (0.0 <= v <= 1.0):
        raise ValueError("v must be in [0,1].")

    # assumes validated
    for i, b in enumerate(m.breakpoints):
        if v > b:
            return m.outputs[i]
    return m.outputs[-1]


# ----------------------------
# Persistence (versioned)
# ----------------------------
def default_profiles(n: int = 4) -> Dict[int, Profile]:
    """
    Default: each profile contains 4 buttons, each button has an IntervalMapping.
    Change presets here later as needed.
    """
    # Default mappings for the 4 buttons (example)
    button_defaults: Dict[int, IntervalMapping] = {
        1: IntervalMapping([0.75, 0.50], ["A", "B", "C"]),
        2: IntervalMapping([0.75, 0.50], ["D", "E", "F"]),
        3: IntervalMapping([0.75, 0.50], ["G", "H", "I"]),
        4: IntervalMapping([0.75, 0.50], ["J", "K", "L"]),
    }

    profiles: Dict[int, Profile] = {}
    for pid in range(1, n + 1):
        # Fresh copies so profiles never share mutable lists
        buttons = {
            bid: IntervalMapping(
                breakpoints=list(cfg.breakpoints),
                outputs=list(cfg.outputs),
                hysteresis=float(cfg.hysteresis),
            )
            for bid, cfg in button_defaults.items()
        }
        profiles[pid] = Profile(buttons=buttons)

    return profiles


def load_profiles(n: int = 4) -> Dict[int, Profile]:
    profiles = default_profiles(n)
    if not PROFILES_PATH.exists():
        return profiles

    try:
        data = json.loads(PROFILES_PATH.read_text(encoding="utf-8"))
        version = int(data.get("version", 1))
        raw_profiles = data.get("profiles", {})

        # -------------------------
        # v1 -> migrate: profile had ONE mapping; apply it to all 4 buttons
        # -------------------------
        if version == 1:
            for k, v in raw_profiles.items():
                pid = int(k)
                if not (1 <= pid <= n):
                    continue

                mapping = v.get("mapping", {})
                m = IntervalMapping(
                    breakpoints=list(mapping.get("breakpoints", profiles[pid].buttons[1].breakpoints)),
                    outputs=list(mapping.get("outputs", profiles[pid].buttons[1].outputs)),
                    hysteresis=float(mapping.get("hysteresis", profiles[pid].buttons[1].hysteresis)),
                )
                validate_interval_mapping(m)

                for bid in range(1, 5):
                    profiles[pid].buttons[bid] = IntervalMapping(
                        breakpoints=list(m.breakpoints),
                        outputs=list(m.outputs),
                        hysteresis=float(m.hysteresis),
                    )
            return profiles

        # -------------------------
        # v2: per-button mappings
        # -------------------------
        if version == 2:
            for k, v in raw_profiles.items():
                pid = int(k)
                if not (1 <= pid <= n):
                    continue

                buttons = v.get("buttons", {})
                for bid in range(1, 5):
                    bcfg = buttons.get(str(bid), {})
                    m = IntervalMapping(
                        breakpoints=list(bcfg.get("breakpoints", profiles[pid].buttons[bid].breakpoints)),
                        outputs=list(bcfg.get("outputs", profiles[pid].buttons[bid].outputs)),
                        hysteresis=float(bcfg.get("hysteresis", profiles[pid].buttons[bid].hysteresis)),
                    )
                    validate_interval_mapping(m)
                    profiles[pid].buttons[bid] = m

            return profiles

        # unknown version => defaults
        return profiles

    except Exception:
        return default_profiles(n)


def save_profiles(profiles: Dict[int, Profile]) -> None:
    data: Dict[str, Any] = {"version": 2, "profiles": {}}
    for pid, prof in profiles.items():
        data["profiles"][str(pid)] = {
            "buttons": {str(bid): asdict(cfg) for bid, cfg in prof.buttons.items()}
        }
    PROFILES_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


# ----------------------------
# UI
# ----------------------------
class Dialog(QDialog):
    num_buttons = 4
    num_profiles = 4

    def __init__(self):
        super().__init__()

        # Model/state
        self._profiles: Dict[int, Profile] = load_profiles(self.num_profiles)
        self._current_profile_id: int = 1
        self._current_button_id: int = 1 
        self._loading_ui: bool = False

        self.create_menu()
        self.create_profile_group()

        # big_editor = QTextEdit()
        # big_editor.setPlainText(
        #     "Skeleton for per-profile interval mapping.\n\n"
        #     "Each profile stores breakpoints + outputs.\n"
        #     "Runtime mapping logic is centralized in map_voltage_to_output().\n"
        #     "Persistence is versioned (profiles.json)."
        # )

        button_box = QDialogButtonBox(
             QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.setMenuBar(self._menu_bar)
        main_layout.addWidget(self._profile_group)
        # main_layout.addWidget(big_editor)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

        self.setWindowTitle("Basic Layouts — Profile 1")
        self.load_profile_into_ui(1)

    # ----- Menu -----
    def create_menu(self):
        self._menu_bar = QMenuBar()

        self._file_menu = QMenu("&File", self)
        self._save_action = self._file_menu.addAction("&Save Profiles")
        self._exit_action = self._file_menu.addAction("E&xit")
        self._menu_bar.addMenu(self._file_menu)

        self._save_action.triggered.connect(self.on_save_profiles)
        self._exit_action.triggered.connect(self.accept)

    def on_save_profiles(self):
        self.commit_ui_to_profile(self._current_profile_id)
        try:
            save_profiles(self._profiles)
            QMessageBox.information(self, "Saved", f"Saved to {PROFILES_PATH.resolve()}")
        except Exception as e:
            QMessageBox.critical(self, "Save failed", f"Could not save profiles:\n{e}")

    def on_button_selected(self, button_id: int):
        # Commit current JSON (if valid) to the previously active button
        self.commit_ui_to_profile(self._current_profile_id)

        self._current_button_id = button_id
        self.load_profile_into_ui(self._current_profile_id)
        self.update_test_output()

    # ----- Profile group -----
    def create_profile_group(self):
        self._profile_group = QGroupBox("Character Profiles (Interval Mapping)")
        outer = QVBoxLayout()

        # Top: profile selector (row of exclusive buttons)
        top = QHBoxLayout()
        top.addWidget(QLabel("Active profile:"))

        self._profile_btn_group = QButtonGroup(self)
        self._profile_btn_group.setExclusive(True)
        self._profile_btn_group.idClicked.connect(self.on_profile_button_clicked)

        for pid in range(1, self.num_profiles + 1):
            btn = QPushButton(f"{pid}")
            btn.setCheckable(True)
            if pid == 1:
                btn.setChecked(True)
            self._profile_btn_group.addButton(btn, pid)
            top.addWidget(btn)

        top.addStretch(1)

        # Form: mapping editor + tester
        form = QFormLayout()

        self._mapping_json = QTextEdit()
        self._mapping_json.setPlaceholderText(
            '{\n  "breakpoints": [0.75, 0.5],\n  "outputs": ["A","B","C"],\n  "hysteresis": 0.0\n}'
        )
        form.addRow("Mapping config (JSON):", self._mapping_json)

        apply_row = QHBoxLayout()
        self._apply_btn = QPushButton("Apply JSON to this profile")
        self._apply_btn.clicked.connect(self.on_apply_mapping_json)
        apply_row.addWidget(self._apply_btn)

        self._reset_btn = QPushButton("Reset this profile")
        self._reset_btn.clicked.connect(self.on_reset_profile)
        apply_row.addWidget(self._reset_btn)

        apply_row.addStretch(1)
        outer.addLayout(top)
        # NEW: Button selector (4 physical buttons inside the active profile)
        btn_row = QHBoxLayout()

        self._button_group = QButtonGroup(self)
        self._button_group.setExclusive(True)
        self._button_group.idClicked.connect(self.on_button_selected)

        for bid in range(1, 5):
            b = QPushButton(f"Button {bid}")   # <-- renamed
            b.setCheckable(True)
            if bid == 1:
                b.setChecked(True)
            self._button_group.addButton(b, bid)
            btn_row.addWidget(b)

        btn_row.addStretch(1)
        outer.addLayout(btn_row)

        outer.addLayout(form)
        outer.addLayout(apply_row)

        # Tester row: input v + computed output
        tester = QHBoxLayout()
        tester.addWidget(QLabel("Test v ∈ [0,1]:"))
        self._test_v = QLineEdit()
        self._test_v.setPlaceholderText("e.g. 0.83")
        self._test_v.textChanged.connect(self.on_test_value_changed)
        tester.addWidget(self._test_v)

        self._test_out = QLabel("→ (output)")
        self._test_out.setTextInteractionFlags(Qt.TextSelectableByMouse)
        tester.addWidget(self._test_out)
        tester.addStretch(1)

        outer.addLayout(tester)

        self._profile_group.setLayout(outer)

    def on_profile_button_clicked(self, profile_id: int):
        # Commit current profile if valid JSON
        self.commit_ui_to_profile(self._current_profile_id)

        self._current_profile_id = profile_id
        self.load_profile_into_ui(profile_id)
        self.setWindowTitle(f"Basic Layouts — Profile {profile_id}")
        self.update_test_output()
    
    '''
    Right now reset doesn’t change selection, so fine, but profile is set programmatically need this!

    def set_active_profile_ui(self, profile_id: int):
        btn = self._profile_btn_group.button(profile_id)
        if btn:
            btn.setChecked(True)
    '''
    def load_profile_into_ui(self, profile_id: int):
        self._loading_ui = True
        try:
            prof = self._profiles[profile_id]
            m = prof.buttons[self._current_button_id]  # <-- per-button mapping now
            with QSignalBlocker(self._mapping_json):
                self._mapping_json.setPlainText(json.dumps(asdict(m), indent=2))
        finally:
            self._loading_ui = False

    def commit_ui_to_profile(self, profile_id: int):
        """
        Only commits if JSON is valid. Otherwise, keeps old mapping.
        Commits into the CURRENT BUTTON of the given profile.
        """
        if self._loading_ui:
            return
        text = self._mapping_json.toPlainText().strip()
        if not text:
            return

        try:
            obj = json.loads(text)
            m = IntervalMapping(
                breakpoints=list(obj.get("breakpoints", [])),
                outputs=list(obj.get("outputs", [])),
                hysteresis=float(obj.get("hysteresis", 0.0)),
            )
            validate_interval_mapping(m)
            self._profiles[profile_id].buttons[self._current_button_id] = m  # <-- key change
        except Exception:
            return

    def on_apply_mapping_json(self):
        if self._loading_ui:
            return
        before = self._profiles[self._current_profile_id].buttons[self._current_button_id]
        text = self._mapping_json.toPlainText().strip()

        try:
            obj = json.loads(text) if text else {}
            m = IntervalMapping(
                breakpoints=list(obj.get("breakpoints", [])),
                outputs=list(obj.get("outputs", [])),
                hysteresis=float(obj.get("hysteresis", 0.0)),
            )
            validate_interval_mapping(m)
            self._profiles[self._current_profile_id].buttons[self._current_button_id] = m
            QMessageBox.information(self, "Applied", "Mapping applied to this profile.")
            self.update_test_output()
        except Exception as e:
            # Restore view to last valid mapping (optional but nice)
            self._mapping_json.setPlainText(json.dumps(asdict(before), indent=2))
            QMessageBox.critical(self, "Invalid mapping", f"Could not apply mapping:\n{e}")

    def on_reset_profile(self):
        pid = self._current_profile_id
        self._profiles[pid] = default_profiles(self.num_profiles)[pid]
        self.load_profile_into_ui(pid)
        self.update_test_output()

    def on_test_value_changed(self, _txt: str):
        self.update_test_output()

    def update_test_output(self):
        """
        Uses the *currently saved* mapping for this profile.
        (i.e., whatever last successfully applied/validated)
        """
        m = self._profiles[self._current_profile_id].buttons[self._current_button_id]
        txt = self._test_v.text().strip()
        if not txt:
            self._test_out.setText("→ (output)")
            return
        try:
            v = float(txt)
            out = map_voltage_to_output(v, m)
            self._test_out.setText(f"→ {out}")
        except Exception as e:
            self._test_out.setText(f"→ error: {e}")

    # Save-on-OK
    def accept(self):
        self.commit_ui_to_profile(self._current_profile_id)
        try:
            save_profiles(self._profiles)
        except Exception:
            pass
        super().accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = Dialog()
    sys.exit(dialog.exec())
