#!/usr/bin/env python3
'''
This chat bot allows one to perform network recon through discord.
'''
import os
import sys
import json
import socket
import subprocess
import configparser
import discord
import requests

CLIENT = discord.Client()
IPINFO_TOKEN = ''
WHOIS_TOKEN = ''

CMD_ARGS = {
    '!hello': 0,
    '!ping': 1,
    '!ip': 1,
    '!geo': 1
}

def ping(url):
    '''
    Run the ping command against a host
    '''
    pingargs = ['ping', '-c' if os.name == 'posix' else '-n', '3', url]
    result = subprocess.run(pingargs, stdout=subprocess.PIPE)
    return False if result.returncode else result.stdout.decode('utf-8')

def getip(url):
    '''
    Run the ping command to get the IP from a URL
    '''
    try:
        return socket.gethostbyname(url)
    except socket.gaierror:
        return False

async def sendf(chn, fmt, *args):
    '''
    Helper method to send a formatted message to a the same channel as the
    previous channel
    '''
    await CLIENT.send_message(chn, fmt.format(*args))

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
        await sendf(chn, 'Pinging {}', data[1])
        msg = ping(data[1])

        if not msg:
            msg = 'Host not found / up'

        await sendf(chn, msg)
    elif data[0] == '!ip':
        await sendf(chn, 'Ip Address: {}', getip(data[1]))
    elif data[0] == '!geo':
        real_ip = getip(data[1])

        if not real_ip:
            await sendf(chn, 'Host not found / up')
            return

        await sendf(chn, 'Ip Address: {}', real_ip)
        req = requests.get('http://ipinfo.io/{}?token={}'.format(real_ip, IPINFO_TOKEN))
        jdata = json.loads(req.text)
        await sendf(chn, 'https://maps.google.com?q={}', jdata['loc'])

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
