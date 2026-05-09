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
gui/
├── layout.py
├── demos/
    ├── typing_demo.py
    ├── raw_adc_demo.py
    └── demo_reaction.py
├── tests/
    ├── adc_test_profile.py
    ├── adc_test_values.py
    └── test_hid_read.py
├── README.md
├── profile_manager.py
└── profile_customizer/
    ├── __init__.py
    ├── defaults.py
    ├── dialog.py
    ├── mapping.py
    ├── models.py
    ├── paths.py
    ├── persistence.py
    └── threshold_editor.py
```
