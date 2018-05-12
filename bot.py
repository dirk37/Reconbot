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

def ping(url):
    '''
    Run the ping command against a host
    '''
    result = subprocess.run(['ping', '-c' if os.name == 'posix' else '-n', '3', url], stdout=subprocess.PIPE)
    return False if result.returncode else result.stdout.decode('utf-8')

def getip(url):
    '''
    Run the ping command to get the IP from a URL
    '''
    try:
        return socket.gethostbyname(url)
    except socket.gaierror:
        return False

async def sendf(msg, fmt, *args):
    '''
    Helper method to send a formatted message to a the same channel as the
    previous channel
    '''
    await CLIENT.send_message(msg.channel, fmt.format(*args))

async def dispatch(message):
    '''
    This is parses the arguments of the command and dispatches the command to
    the actual system commands that get run.
    '''
    data = message.content.split(' ')

    if data[0] == '!hello':
        await sendf(message, 'Hello {}', message.author.mention)
    elif data[0] == '!ping':
        if len(data) != 2:
            await sendf(message, 'Error: this command takes 1 argument')
        else:
            await sendf(message, 'Pinging {}', data[1])
            msg = ping(data[1])

            if not msg:
                msg = 'Host not found / up'

            await sendf(message, msg)
    elif data[0] == '!geo':
        if len(data) != 2:
            await sendf(message, 'Error: this command takes 1 argument')
        else:
            url = data[1]
            real_ip = getip(url)

            if real_ip:
                await sendf(message, 'Ip Address: {}', real_ip)
                req = requests.get('http://ipinfo.io/{}?token=cc8b1d0905b2cf'.format(real_ip))
                jdata = json.loads(req.text)
                await sendf(message, 'https://maps.google.com?q={}', jdata['loc'])
            else:
                await sendf(message, 'Host not found / up')

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

    CONFIG_TOKEN = CONFIG_PARSER['NetBot']['token']
    CLIENT.run(CONFIG_TOKEN)
