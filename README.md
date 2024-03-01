# Discord bot

## How to use

* Build the package: `poetry build`
* Install the wheel to system: `sudo pip3 install dist/discord_bot-0.1.0-py3-none-any.whl`
* Copy bot configuration `discord-bot.conf` to `/etc/discord-bot.conf` on the server
* Install systemd unit `discord-bot.service` to `/etc/systemd/system/`
* Enable and start systemd service: `sudo systemctl enable discord-bot && sudo systemctl start discord-bot`
