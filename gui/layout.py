from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from profile_customizer.dialog import ProfileCustomizerDialog


def main() -> int:
    app = QApplication(sys.argv)
    dialog = ProfileCustomizerDialog()
    return dialog.exec()


if __name__ == "__main__":
    sys.exit(main())
