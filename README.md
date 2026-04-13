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
- A usb keyboard for installation.  
- Micro USB adapter for usb keyboard.  

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
| !Turbo         | GPIO26 | Pin 37 |  
| 8TO6  | GPIO19 | Pin 35 |  
| !8TO6 | GPIO25 | Pin 22 |  
| DISC | GPIO20 | Pin 38 |  

Turbo is grounded directly to a spare ground on the Pacto board.  
Any Ground on the Rpi to Any Ground on the Pacto.  

## ⚙️ Features
- Touchscreen-based control interface  
- Designed for Pactotech integration  
- Compatible with multiple Raspberry Pi models  
- Works with XInput-based arcade controls
- Keyboard Mode - Disconnects and icons can not be pressed until re-enabled.  

## 🚀 Setup
Recommended Pi OS using the official imager: Raspberry Pi OS (Other) -> Raspberry Pi OS Lite (32-Bit)  
Edit config.txt and add lines for the resolution of your touchscreen, for example:  

```````````````````````
hdmi_force_hotplug=1  
hdmi_group=2  
hdmi_mode=87  
hdmi_cvt=800 480 60 6 0 0 0  
```````````````````````
  
Some touchscreens may also require this video driver in config.txt:  
```````````````````````
dtoverlay=vc4-kms-v3d  
```````````````````````
Auto Login:  
```````````````````````
sudo raspi-config  
```````````````````````
System Options-> Enable Auto Login  

Install Dependencies:  
```````````````````````
sudo apt update  
```````````````````````
```````````````````````
sudo apt install -y git python3-pygame python3-gpiozero python3-evdev libsdl2-2.0-0  
```````````````````````
```````````````````````
sudo apt install -y libegl1 libgles2 libgl1 libdrm2  
```````````````````````
```````````````````````
git clone https://github.com/dinodox/PactoTouchscreen.git  
```````````````````````
```````````````````````
cd PactoTouchscreen  
```````````````````````
```````````````````````
python3 pacto.py  
```````````````````````
*Some touchscreens may see a runtime warning but this can be ignored, everything will still work fine.  

🔧 Optional  
Disable Raspberry Pi boot text.    
```````````````````````
sudo nano /boot/cmdline.txt
```````````````````````
Find:      console=serial0,115200 console=tty1  
Change to: console=serial0,115200 console=tty3  
Add at the end of the same line: 
```````````````````````
quiet splash loglevel=0 vt.global_cursor_default=0
```````````````````````
**Do not copy and paste the example below, PARTUUID must remain the same.   
Example cmdline.txt: console=tty3 root=PARTUUID=xxxx rootfstype=ext4 fsck.repair=yes rootwait quiet splash loglevel=0 vt.global_cursor_default=0  
  
Auto-Start pacto.py.  
Run as a systemd service.  
```````````````````````
sudo nano /etc/systemd/system/pacto.service
```````````````````````
Paste below:  
```````````````````````
[Unit]
Description=Pacto UI
After=multi-user.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/PactoTouchscreen
ExecStart=/usr/bin/python3 /home/pi/PactoTouchscreen/pacto.py
Restart=always

# Pygame / framebuffer
Environment=SDL_VIDEODRIVER=KMSDRM
Environment=SDL_FBDEV=/dev/fb0

# Give display time to initialize (important for your screen)
ExecStartPre=/bin/sleep 2

[Install]
WantedBy=multi-user.target  
```````````````````````

Remove some unused rpi components to speed up boot time.  
```````````````````````
systemctl list-unit-files --type=service
```````````````````````
Some files that can be disabled that are not needed and can speed up boot time:  
```````````````````````
sudo systemctl disable bluetooth.service
sudo systemctl disable hciuart.service
sudo systemctl disable triggerhappy.service
sudo systemctl disable avahi-daemon.service
sudo systemctl disable dphys-swapfile.service
sudo systemctl disable keyboard-setup.service
sudo systemctl disable apt-daily.service
sudo systemctl disable apt-daily-upgrade.service
```````````````````````
Disable wifi will also speed up boot time if not needed:  
```````````````````````
sudo nano /boot/config.txt
```````````````````````
Add:  
`````````````````````
dtoverlay=disable-wifi
dtoverlay=disable-bt
`````````````````````

📝 Notes  
ESC on keyboard will end pacto.py.  
90° Right Angle HDMI & USB Adapters recommended for cleaner look.  
Blank button icon supplied for custom icons.  
Most HDMI touchscreens should work.  
Pactotech handles controller input natively.

📄 License  
MIT License  
Copyright (c) 2026 Dino Dox
