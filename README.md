# PactoTouchscreen
Use a touchscreen to control PactoTech control boards instead of physical switches/buttons.

Pactotech Controller (RPi + Touchscreen)
A control system for Pactotech hardware built using a Raspberry Pi with a touchscreen interface.

🧰 Hardware Requirements
Raspberry Pi Zero (any Raspberry Pi model should work)

Pactotech Control Interface Model 4000T (1000T & 2000T will also work but will require some modifications to the gpio's)
https://pactotech.com/en-us/products/copy-of-pacto-tech-4000t-4-player-control-interface-for-arcade-cabinets-supports-xinput-protocol

Adafruit 5" 800x480 HDMI Touchscreen (Or any HDMI touchscreen)
https://www.adafruit.com/product/2260

3D Printed Case for the screen
https://www.printables.com/model/899608-adafruit-5-hdmi-screen-case/related

🎮 About the Pactotech Interface
The Pactotech 4000T is a 4-player arcade control interface that presents inputs as standard XInput (Xbox-style) controllers when connected to a system. 
This allows broad compatibility with emulators and modern games without additional configuration.

Supports up to 4 players
Appears as Xbox 360 controllers (XInput)
Works with most emulators and PC games
Flexible input modes (digital, analog, twinstick, etc.)

🔌 GPIO Connections
Coming soon
(GPIO pin mappings and wiring details will be added later.)

⚙️ Features
Touchscreen-based control interface
Designed for Pactotech system integration
Compatible with multiple Raspberry Pi models
Works with XInput-based arcade controls

🚀 Setup
Install Raspberry Pi OS on your device
Connect the HDMI touchscreen
Connect the Pactotech 4000T via USB
Clone this repository:

git clone https://github.com/dinodox/PactoTouchscreen.git
Navigate into the project folder:

cd pactotech-controller
Run the main script:

python3 pacto.py
📝 Notes
Most HDMI touchscreens should work (not limited to Adafruit)

The Pactotech interface handles input as standard controllers

GPIO integration will be documented as the project evolves

📄 License
This project is licensed under the MIT License.

Copyright (c) 2026 Dino Dox
