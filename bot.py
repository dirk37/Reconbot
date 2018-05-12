#!/usr/bin/env python
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

def dispatch(message):
	def sendf(fmt, *args):
		await client.send_message(message.channel, fmt.format(*args))

	data = message.content.split(' ')

	if message.content.startswith('!hello'):
		sendf('Hello {0.author.mention}', message)

	if message.content.startswith('!ping'):
		if len(data) != 2:
			sendf('Error: this command takes 1 argument')
		else:
			sendf('Pinging {}', data[1])
			msg = ping(url)
			msg = msg[msg.find('Ping stat'):] if msg else 'Host not found / up'
			sendf(msg)
			
	if message.content.startswith('!geo'):
		if len(data) != 2:
			sendf('Error: this command takes 1 argument')
		else:
			url = data[1]
			ip = getip(url)

			if ip:
				sendf('Ip Address: {}', ip)
				r = requests.get('http://ipinfo.io/{}?token=cc8b1d0905b2cf'.format(ip))
				jdata = json.loads(r.text)
				sendf('https://maps.google.com?q={}', jdata['loc'])
			else:
				sendf('Host not found / up')

@client.event
async def on_message(message):
	if message.author != client.user:
		dispatch(message)

@client.event
async def on_ready():
	print('Logged in as {} ({})'.format(client.user.name, client.user.id))

if __name__ == '__main__':
	config_location = 'config.ini'

	if len(sys.argv) > 1:
		config_location = sys.argv[1]

	config_parser = configparser.ConfigParser()

	with open(config_location, 'r') as f:
		config.read_file(f)

	config_token = config['NetBot']['token']
	client.run(config_token)
