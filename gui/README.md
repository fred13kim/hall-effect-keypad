# Instructions

Make sure that `conda` is availabe on machine

Run `conda env create -f environment.yml`

Run `conda activate snr-proj`


# Profile Customizer App

A modularized PySide6 profile customization skeleton.

## Run

```bash
python3 layout.py
```

## Layout

```text
profile_customizer_app/
├── layout.py
├── README.md
└── profile_customizer/
    ├── __init__.py
    ├── defaults.py
    ├── dialog.py
    ├── mapping.py
    ├── models.py
    ├── paths.py
    └── persistence.py
```

## Files

- `models.py`: pure profile/config dataclasses.
- `mapping.py`: validation and normalized-voltage mapping logic.
- `defaults.py`: default presets for profiles/buttons.
- `persistence.py`: JSON load/save and schema migration.
- `dialog.py`: PySide6 UI only.
- `paths.py`: config file paths.
- `layout.py`: application entry point.
