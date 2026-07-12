Setting my-wttr to systemd service in case i forget again

mkdir -p ~/.local/bin/my-wttr
cp weather_server.py ~/.local/bin/my-wttr/weather_server.py
mkdir -p ~/.config/systemd/user
nano ~/.config/systemd/user/my-wttr.service

paste in: 

[Unit]
Description=My WTTR Weather Server
After=network-online.target

[Service]
ExecStart=/usr/bin/python /home/Spring/.local/bin/my-wttr/weather_server.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target

systemctl --user daemon-reload
systemctl --user enable --now my-wttr.service



Fixing firefox trying to make my ears bleed cause i'll forget this too

install pipewire-alsa
go to about:config
add media.cubeb.backend
set as string, set value to alsa
enjoy having functional ears
