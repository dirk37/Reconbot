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
import discord
import aiodns
import aiohttp

if sys.platform == 'win32':
    LOOP = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(LOOP)

DNS_RESOLVER = aiodns.DNSResolver()
HTTP_SESSION = aiohttp.ClientSession(skip_auto_headers=['User-Agent'])
CLIENT = discord.Client()
IPINFO_TOKEN = ''
WHOIS_TOKEN = ''

CMD_ARGS = {
    '!hello': 0,
    '!ping': 1,
    '!ip': 1,
    '!geo': 1
}

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
    Run the ping command to get the IP from a URL
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

async def dispatch(message):
    '''
    This is parses the arguments of the command and dispatches the command to
    the actual system commands that get run.
    '''
    data = message.content.split(' ')
    chn = message.channel

    if data[0] not in CMD_ARGS:
        return

    if len(data) - 1 != CMD_ARGS[data[0]]:
        await sendf(chn, 'Error: `{}` takes {} argument(s)', data[0], CMD_ARGS[data[0]])
        return

    if data[0] == '!hello':
        await sendf(chn, 'Hello {}', message.author.mention)
    elif data[0] == '!ping':
        await ping(chn, data[1])
    elif data[0] == '!ip':
        await dnsquery(chn, data[1])
    elif data[0] == '!geo':
        await geolocate(chn, data[1])

@CLIENT.event
async def on_message(message):
    '''
    This is the event that gets called when the bots gets messaged
    '''
    if message.author != CLIENT.user:
        await dispatch(message)

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
