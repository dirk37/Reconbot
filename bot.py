#!/usr/bin/env python3
'''
This chat bot allows one to perform network recon through discord.
'''
import os
import sys
import asyncio
import json
import configparser
import ipaddress
import re
import discord
import aiodns
import aiohttp

if sys.platform == 'win32':
    asyncio.set_event_loop(asyncio.ProactorEventLoop())

DNS_RESOLVER = aiodns.DNSResolver()
HTTP_SESSION = aiohttp.ClientSession(skip_auto_headers=['User-Agent'])
CLIENT = discord.Client()
IPINFO_TOKEN = ''
WHOIS_TOKEN = ''

async def sendf(chn, fmt, *args, **kwargs):
    '''
    Helper method to send a formatted message to a the same channel as the
    previous channel
    '''
    await CLIENT.send_message(chn, fmt.format(*args, **kwargs))

async def ping(chn, host):
    '''
    Run the ping command against a host
    '''
    await sendf(chn, 'Pinging {}', host)
    pingargs = ['ping', '-c' if os.name == 'posix' else '-n', '3', host]

    proc = await asyncio.create_subprocess_exec(*pingargs, stdout=asyncio.subprocess.PIPE)
    (data, _) = await proc.communicate()

    if proc.returncode:
        await sendf(chn, 'Error: host not up')
    else:
        await sendf(chn, '```{}```', data.decode('utf-8'))

async def dnsquery(chn, name):
    '''
    Convert a hostname to an IP address
    '''
    try:
        ipaddress.ip_address(name)
        await sendf(chn, '`{}` is already a valid IP Address', name)
        return name
    except ValueError:
        pass

    try:
        hosts = await DNS_RESOLVER.query(name, 'A')
        await sendf(chn, 'IP Address for `{}` is `{}`', name, hosts[0].host)
        return hosts[0].host
    except aiodns.error.DNSError as err:
        await sendf(chn, 'Error: {}', err.args[1])

async def geolocate(chn, name):
    '''
    Get turn a name into an IP and then use ipinfo.io to get the geolocation
    '''
    real_ip = await dnsquery(chn, name)

    if real_ip:
        req = await HTTP_SESSION.get('https://ipinfo.io/{}?token={}'.format(
            real_ip, IPINFO_TOKEN))

        txt = await req.text()
        jdata = json.loads(txt)

        if 'loc' in jdata:
            await sendf(chn, 'https://maps.google.com?q={}', jdata['loc'])
        elif 'error' in jdata:
            err = jdata['error']
            await sendf(chn, 'Error: {}: {}', err['title'], err['message'])
        else:
            await sendf(chn, 'Error: Data unavailable')

CMDS = {
    '!ping': ping,
    '!ip': dnsquery,
    '!geo': geolocate
}

BAD_ARG_COUNT_RE = re.compile(r'takes (\d+) positional arguments but \d+ were given')
MISSING_ARG_RE = re.compile(r'missing (\d+) required positional arguments?: (.+)')

@CLIENT.event
async def on_message(msg):
    '''
    This is the event that gets called when the bots gets messaged
    '''
    chan = msg.channel
    data = msg.content.split(' ')

    if msg.author == CLIENT.user:
        return

    try:
        await CMDS[data[0]](chan, *(data[1:]))
    except KeyError:
        pass
    except TypeError as err:
        match = BAD_ARG_COUNT_RE.search(str(err))

        if match:
            await sendf(chan, 'Error: `{}` expects {} args but {} were given',
                        data[0], int(match[1]) - 1, len(data) - 1)
        else:
            match = MISSING_ARG_RE.search(str(err))

            if match:
                await sendf(chan, 'Error: `{}` expects {} args but {} were given',
                            data[0], int(match[1]), len(data) - 1)
                await sendf(chan, '`{} {}`', data[0], match[2])

@CLIENT.event
async def on_ready():
    '''
    This is the event that gets called when the bots connected to the network
    '''
    print('Logged in as {} ({})'.format(CLIENT.user.name, CLIENT.user.id))

if __name__ == '__main__':
    CONFIG_LOCATION = 'config.ini'

    if len(sys.argv) > 1:
        CONFIG_LOCATION = sys.argv[1]

    CONFIG_PARSER = configparser.ConfigParser()

    with open(CONFIG_LOCATION, 'r') as f:
        CONFIG_PARSER.read_file(f)

    CONFIG_TOKEN = CONFIG_PARSER['Tokens']['discord']
    IPINFO_TOKEN = CONFIG_PARSER['Tokens']['ipinfo']
    WHOIS_TOKEN = CONFIG_PARSER['Tokens']['whois']
    CLIENT.run(CONFIG_TOKEN)
