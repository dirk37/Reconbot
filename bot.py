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

	if "Ping statistics" not in result:
		return False
	else:
		return result

def getip(url):
	result = os.popen('ping -4 -n 1 ' + url).read()

	if "Ping statistics" not in result:
		return False
	else:
		result = result[1 + result.find("["):result.find("]")]
		return result

def send(msg):
	msg = msg.format(message)

# Handle messages received 
def dispatch(message):
	if message.content.startswith('!hello'):
		msg = 'Hello {0.author.mention}'.format(message)
		await client.send_message(message.channel, msg)

	if message.content.startswith('!ping'):
		data = message.content.split(" ")

		if len(data) != 2:
			msg = "Error. This command takes 1 argument"
			await client.send_message(message.channel, msg)	
		else:
			url = data[1]
			msg = 'Pinging ' + url

			await client.send_message(message.channel, msg)	

			msg = ping(url)

			if msg == False:
				msg = "Host not found / up"
			else:
				msg = msg[msg.find("Ping stat"):]
			
			await client.send_message(message.channel, msg)	
			
	if message.content.startswith('!geo'):
		data = message.content.split(" ")

		if len(data) != 2:
			msg = "Error. This command takes 1 argument"
			await client.send_message(message.channel, msg)	
		else:
			url = data[1]
			ip = getip(url)

			if ip == False:
				msg = "Host not found / up"
				await client.send_message(message.channel, msg)	
			else:
				msg = "Ip address: " + ip

				await client.send_message(message.channel, msg)	

				r = requests.get("http://ipinfo.io/"+ ip +"?token=cc8b1d0905b2cf")
				jdata = json.loads(r.text)
				msg += "https://maps.google.com?q=" + jdata["loc"]

				await client.send_message(message.channel, map)	

@client.event
async def on_message(message):
	# We do not want the bot to reply to itself
	if message.author != client.user:
		dispatch(message)

@client.event
async def on_ready():
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')

if __name__ == '__main__':
	config_location = 'config.ini'

	if len(sys.argv) > 1:
		config_location = sys.argv[1]

	config_parser = configparser.ConfigParser()

	with open(config_location, 'r') as f:
		config.read_file(f)

	config_token = config['NetBot']['token']
	client.run(config_token)
