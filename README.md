# PactoTouchscreen
Use a touchscreen to control PactoTech control boards instead of physical switches/buttons.

## Pactotech Controller (RPi + Touchscreen)
A control system for Pactotech hardware built using a Raspberry Pi with a touchscreen interface.

## 🧰 Hardware Requirements
- Raspberry Pi Zero (any Raspberry Pi model with HDMI should work)
- Pactotech Control Interface Model 4000T (1000T & 2000T will also work but require code changes)  
  https://pactotech.com/en-us/products/copy-of-pacto-tech-4000t-4-player-control-interface-for-arcade-cabinets-supports-xinput-protocol  
- Adafruit 5" 800x480 HDMI Touchscreen (or similar)  
  https://www.adafruit.com/product/2260  
- 3D Printed Case  
  https://www.printables.com/model/899608-adafruit-5-hdmi-screen-case/related  
- HDMI + USB cables (varies by Pi model)
- 90° Right Angle Adapters for cleaner look  

## 🎮 About the Pactotech 4000T Interface
- Supports up to 4 players  
- Appears as Xbox 360 controllers (XInput)  
- Works with most emulators and PC games  
- Flexible input modes (digital, analog, twinstick)

## 🔌 GPIO Pinout (Pacto 4000T → Raspberry Pi)
All GPIOs are **active LOW** using `gpiozero.OutputDevice`.
### 🎮 Player Mode
| Mode        | GPIO   | Physical Pin |
|------------|--------|--------------|
| 2 Player   | GPIO17 | Pin 11 |
| 4 Player   | GPIO22 | Pin 15 |
| Twin Stick | GPIO27 | Pin 13 |
### 🕹️ Control Mode
| Mode        | GPIO   | Physical Pin |
|------------|--------|--------------|
| D-Pad      | GPIO13 | Pin 33 |
| Analog Fast| GPIO5  | Pin 29 |
| Analog Slow| GPIO6  | Pin 31 |
### ⚙️ Features
| Feature         | GPIO   | Physical Pin |  
|----------------|--------|--------------|  
| Turbo          | GPIO26 | Pin 37 |  
| 8-to-6 Enable  | GPIO19 | Pin 35 |  
| 8-to-6 Disable | GPIO25 | Pin 22 |  
| Keyboard Mode  | GPIO20 | Pin 38 |  

Any Ground on the Rpi to Any Ground on the Pacto.  
*Keyboard Mode - Disconnects and icons can not be pressed until re-enabled  .

## ⚙️ Features
- Touchscreen-based control interface  
- Designed for Pactotech integration  
- Compatible with multiple Raspberry Pi models  
- Works with XInput-based arcade controls  

## 🚀 Setup
sudo apt update  
sudo apt install -y git python3-pygame python3-gpiozero python3-evdev libsdl2-2.0-0  
git clone https://github.com/dinodox/PactoTouchscreen.git  
cd PactoTouchscreen  
python3 pacto.py  

🔧 Optional  
Disable Raspberry Pi boot text.  
Auto-login + auto-start pacto.py.  
Run as a systemd service.  
Remove some unused rpi components to speed up boot time.  
Blank button icon supplied for custom icons.  

📝 Notes  
Most HDMI touchscreens should work.  
May need to edit rpi config for resolution of touchscreen 800x480.  
Pactotech handles controller input natively.

📄 License  
MIT License  
Copyright (c) 2026 Dino Dox
