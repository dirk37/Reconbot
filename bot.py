#!/usr/bin/env python3
# https://github.com/Rapptz/discord.py/blob/async/examples/reply.py
import discord
import os
import requests
import json
import configparser
import sys

client = discord.Client()

def ping(url):
	result = os.popen('ping -4 ' + url).read()
	return result if 'Ping statistics' in result else False

def getip(url):
	result = os.popen('ping -4 -n 1 ' + url).read()
	return result[1 + result.find('[') : result.find(']')] if 'Ping statistics' in result else False

async def sendf(msg, fmt, *args):
	await client.send_message(msg.channel, fmt.format(*args))

async def dispatch(message):
	data = message.content.split(' ')

	if data[0] == '!hello':
		await sendf(message, 'Hello {}', message.author.mention)
	elif data[0] == '!ping':
		if len(data) != 2:
			await sendf(message, 'Error: this command takes 1 argument')
		else:
			await sendf(message, 'Pinging {}', data[1])
			msg = ping(url)
			msg = msg[msg.find('Ping stat'):] if msg else 'Host not found / up'
			await sendf(message, msg)
	elif data[0] == '!geo':
		if len(data) != 2:
			await sendf(message, 'Error: this command takes 1 argument')
		else:
			url = data[1]
			ip = getip(url)

			if ip:
				await sendf(message, 'Ip Address: {}', ip)
				r = requests.get('http://ipinfo.io/{}?token=cc8b1d0905b2cf'.format(ip))
				jdata = json.loads(r.text)
				await sendf(message, 'https://maps.google.com?q={}', jdata['loc'])
			else:
				await sendf(message, 'Host not found / up')

@client.event
async def on_message(message):
	if message.author != client.user:
		await dispatch(message)

@client.event
async def on_ready():
	print('Logged in as {} ({})'.format(client.user.name, client.user.id))

if __name__ == '__main__':
	config_location = 'config.ini'

	if len(sys.argv) > 1:
		config_location = sys.argv[1]

	config_parser = configparser.ConfigParser()

	with open(config_location, 'r') as f:
		config_parser.read_file(f)

	config_token = config_parser['NetBot']['token']
	client.run(config_token)
