<div align="center">
  <h1>InspectX</h1>
  <p><strong>Defect Detection Studio — by Shubham Sahu</strong></p>
  <p>
    <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python" />
    <img src="https://img.shields.io/badge/PyQt6-6.6+-green?logo=qt" />
    <img src="https://img.shields.io/badge/SQLite-3-lightgrey?logo=sqlite" />
    <img src="https://img.shields.io/badge/license-MIT-purple" />
  </p>
</div>

---

## ✨ What is InspectX?

InspectX is a **full-featured desktop application** for industrial visual inspection and AI-powered defect detection. It provides a complete end-to-end workflow:

| Stage | What you can do |
|-------|----------------|
| **Dataset** | Upload images, tag them, manage splits (Train / Val / Test) |
| **Annotate** | Draw bounding boxes and polygons with a canvas editor |
| **Versions** | Snapshot dataset versions with preprocessing & augmentation config |
| **Train** | Configure and launch model training (YOLOv8-style pipeline) |
| **Models** | Browse trained models, compare mAP / precision / recall / latency |
| **Test** | Run inference on new images and review results |
| **Settings** | Camera, PLC/communication protocol, and project config |

---

## 🚀 Quick Start (No Install Required)

> **Recruiters:** follow these 3 steps — no Python needed.

1. Go to the [**Releases**](../../releases) tab and download:
   - `InspectX-windows.zip` — Windows 10/11
   - `InspectX-macos.zip` — macOS 12+

2. Extract the ZIP and run:
   - **Windows:** double-click `InspectX.exe`
   - **macOS:** double-click `InspectX.app`  
     *(If macOS blocks it: right-click → Open → Open)*

3. Log in with the demo account:

   | Field    | Value                |
   |----------|----------------------|
   | Email    | `demo@inspectx.ai`   |
   | Password | `demo1234`           |

   A sample **PCB Defect Detection** project with images, annotations, a dataset version, and a trained model is pre-loaded for you to explore.

---

## 🛠 Run from Source

```bash
# 1. Clone
git clone https://github.com/your-username/inspectx-python.git
cd inspectx-python

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Seed demo data (first time only)
python seed_demo.py

# 5. Launch
python main.py
```

**Requirements:** Python 3.10+ · PyQt6 · SQLAlchemy · bcrypt · Pillow

---

## 📦 Build a Standalone Installer

```bash
pip install pyinstaller
python seed_demo.py          # bake demo data into the DB first
pyinstaller inspectx.spec    # output → dist/InspectX/
```

Or push a version tag to trigger the automated GitHub Actions build:

```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions will build Windows + macOS binaries and attach them to a Release automatically. See [`.github/workflows/build.yml`](.github/workflows/build.yml).

---

## 🏗 Project Structure

```
inspectx-python/
├── main.py                     # Entry point
├── requirements.txt
├── seed_demo.py                # Populate DB with demo user + project
├── inspectx.spec               # PyInstaller build spec
├── assets/
│   └── -logo.jpg
└── app/
    ├── database/
    │   ├── engine.py           # SQLite engine (dev + packaged path aware)
    │   ├── models.py           # SQLAlchemy ORM models
    │   └── inspectx.db         # SQLite database
    ├── services/
    │   ├── auth_service.py
    │   ├── project_service.py
    │   ├── image_service.py
    │   ├── annotation_service.py
    │   ├── version_service.py
    │   └── model_service.py
    └── ui/
        ├── main_window.py      # Root QMainWindow, navigation host
        ├── state.py            # Centralised app state
        ├── theme.py            # Colour tokens
        ├── pages/              # One file per screen
        └── widgets/            # Reusable components
```

---

## 🧑‍💻 Tech Stack

- **UI framework:** PyQt6 (Qt 6)
- **Database:** SQLite via SQLAlchemy 2.0 ORM
- **Auth:** bcrypt password hashing
- **Packaging:** PyInstaller
- **CI/CD:** GitHub Actions

---

## 📸 Screenshots

> Add screenshots here after first launch.  
> `File → Screenshot` or use OS screenshot tool, then drag images into this folder.

---

## 📄 License

MIT ©  Shubham
