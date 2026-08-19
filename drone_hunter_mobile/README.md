# 📱 Drone Hunter (Mobile Edition)

Mobile version tailored for Android touch devices and simulators, featuring on-screen virtual joystick controls, touch action buttons, responsive touch HUD, and Buildozer APK packaging.

---

## 🎮 How to Run (Desktop Simulation)

```bash
python drone_hunter_mobile/main.py
```

---

## 📦 Building Android APK

Using Buildozer on Linux/WSL:
```bash
cd drone_hunter_mobile
buildozer android debug
```
The resulting `.apk` will be generated in the `bin/` directory.
