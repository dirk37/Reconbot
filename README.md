# Reconbot

Reconbot is a Discord chat bot written in Python using [discord.py][dpy]. It hosts several utility
commands that allow users to ping IP addresses and perform DNS lookup and geolocation on hostnames.

## Installation

You'll need to have a working Python 3 environment, including pip.

[See the discord.py documentation for installation instructions on your platform.][dpy-install]

## Usage

Create a configuration file in the same working directory called `config.ini`. This will store your 
private tokens, which should not be revealed publicly.

Populate it with the following contents, replacing the placeholders with your actual tokens:

```ini
[Tokens]
discord=YOUR_DISCORD_TOKEN
ipinfo=IPINFO_TOKEN
whois=WHOIS_TOKEN
```

The [`discord` token is a Discord Bot User token][dapi], and the [`ipinfo` token is from IpInfo][ipinfo].

Run the bot with the optional first parameter pointing to the config file location:

```bash
python3 bot.py
# this is also valid
python3 bot.py /path/to/config.ini
```

[dpy]: https://github.com/Rapptz/discord.py
[dpy-install]: https://github.com/Rapptz/discord.py#installing
[ipinfo]: https://ipinfo.io/
[dapi]: https://discordapp.com/developers/docs/intro
