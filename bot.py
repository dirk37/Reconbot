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
import aiohttp

from discord.ext import commands

if sys.platform == 'win32':
    import socket
    asyncio.set_event_loop(asyncio.ProactorEventLoop())
else:
    import aiodns
    DNS_RESOLVER = aiodns.DNSResolver()

CONFIG_LOCATION = 'config.ini'
CONFIG_PARSER = configparser.ConfigParser()
HTTP_SESSION = aiohttp.ClientSession(skip_auto_headers=['User-Agent'])
BOT = commands.Bot(command_prefix='%', description='Perform network recon operations')

if len(sys.argv) > 1:
    CONFIG_LOCATION = sys.argv[1]

with open(CONFIG_LOCATION, 'r') as f:
    CONFIG_PARSER.read_file(f)

@BOT.command()
async def ping(name: str, count: int = 3):
    '''
    Run the ping(1) command against a host
    '''
    await BOT.say('Pinging `{}`'.format(name))
    args = ['ping', '-c' if os.name == 'posix' else '-n', str(count), name]

    proc = await asyncio.create_subprocess_exec(*args, stdout=asyncio.subprocess.PIPE)
    (data, _) = await proc.communicate()

    if proc.returncode:
        await BOT.say('Error: Host not up')
    else:
        await BOT.say('```{}```'.format(data.decode('utf-8')))

@BOT.command()
async def traceroute(name: str):
    '''
    Run the traceroute(8) command against a host
    '''
    await BOT.say('Running traceroute on `{}`'.format(name))

    proc = await asyncio.create_subprocess_exec('traceroute', name,
                                                stdout=asyncio.subprocess.PIPE)
    (data, _) = await proc.communicate()

    if proc.returncode:
        await BOT.say('Error: Traceroute failed')
    else:
        await BOT.say('```{}```'.format(data.decode('utf-8')))

@BOT.command()
async def whois(name: str):
    '''
    Get whois data for specified domain from jsonwhois.io api
    '''
    await BOT.say('Running WHOIS against `{}`'.format(name))

    req = await HTTP_SESSION.get('https://api.jsonwhois.io/whois/domain?key={}&domain={}'.format(
        CONFIG_PARSER['Tokens']['whois'], name))
    txt = await req.text()
    jdata = json.loads(txt)

    await BOT.say('```{}```'.format(json.dumps(jdata, sort_keys=True, indent=4)))

async def dnsquery(name: str):
    '''
    Convert a hostname to an IP address
    '''
    if sys.platform == 'win32':
        try:
            host = socket.gethostbyname(name)

            if host == name:
                await BOT.say('`{}` is already a valid IP Address'.format(name))
            else:
                await BOT.say('IP Address for `{}` is `{}`'.format(name, host))

            return host
        except socket.gaierror as err:
            await BOT.say('Error: {}'.format(err))
    else:
        try:
            ipaddress.ip_address(name)
            await BOT.say('`{}` is already a valid IP Address'.format(name))
            return name
        except ValueError:
            pass

        try:
            hosts = await DNS_RESOLVER.query(name, 'A')
            await BOT.say('IP Address for `{}` is `{}`'.format(name, hosts[0].host))
            return hosts[0].host
        except aiodns.error.DNSError as err:
            await BOT.say('Error: {}'.format(err.args[1]))

@BOT.command()
async def hostresolve(name: str):
    '''
    Gets the raw IP address of a hostname
    '''
    await dnsquery(name)

@BOT.command()
async def geolocate(name: str):
    '''
    Gets the geolocation of a hostname
    '''
    real_ip = await dnsquery(name)

    if real_ip:
        req = await HTTP_SESSION.get('https://ipinfo.io/{}?token={}'.format(
            real_ip, CONFIG_PARSER['Tokens']['ipinfo']))

        txt = await req.text()
        jdata = json.loads(txt)

        if 'loc' in jdata:
            await BOT.say('https://maps.google.com?q={}'.format(jdata['loc']))
        elif 'error' in jdata:
            err = jdata['error']
            await BOT.say('Error: {}: {}'.format(err['title'], err['message']))
        else:
            await BOT.say('Error: Data unavailable')

@BOT.command()
async def nmap(name: str):
    '''
    Run the nmap(1) command against a domain name
    '''
    await BOT.say('Running NMAP against `{}`'.format(name))
    args = ['nmap', name]

    proc = await asyncio.create_subprocess_exec(*args, stdout=asyncio.subprocess.PIPE)
    (data, _) = await proc.communicate()

    if proc.returncode:
        await BOT.say('Error: Could not find host')
    else:
        await BOT.say('```{}```'.format(data.decode('utf-8')))

@BOT.event
async def on_ready():
    '''
    This is the event that gets called when the bot connects to the network
    '''
    print('Logged in as {} ({})'.format(BOT.user.name, BOT.user.id))

BOT.run(CONFIG_PARSER['Tokens']['discord'])
