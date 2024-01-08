LIRC to Home-assistant

Losely based on https://github.com/akkana/scripts/blob/master/rpi/pyirw.py
Moved to Asyncio and added REST calls to Homoe-assistant

## Install Lirc
sudo apt update && apt upgrade
sudo apt install lirc

## Confirm your USB IR receiver
lsusb

## Correct lirc_options file
sudo nano /etc/lirc/lirc_options.conf
```
[lircd]
nodaemon        = False
driver          = default
device          = /dev/lirc0
``` 

## Copy project files
/home/pi/lirc2hass.py
/home/pi/lirc2hass.conf

## List valid key names
irrecord --list-namespace

## Stop lircd service
sudo systemctl stop lircd.socket
sudo systemctl stop lircd.service

## Backup current lircd.config
sudo mv /etc/lirc/lircd.conf /etc/lirc/lircd_original.conf

## Record commands to a new lircd.config
sudo irrecord -d /dev/lirc0 ~/lircd.conf
Follow instructions and enter valid names from the namespace and record each key from your remote control

## Create a systemd service
sudo nano /etc/systemd/system/lirc2hass.service
```
[Unit]
Description=My test service
After=multi-user.target
[Service]
Type=simple
Restart=always
ExecStart=/usr/bin/python3 /home/pi/lirc2hass.py
[Install]
WantedBy=multi-user.target
```
sudo systemctl daemon-reload
sudo systemctl enable lirc2hass.service
sudo systemctl start lirc2hass.service
