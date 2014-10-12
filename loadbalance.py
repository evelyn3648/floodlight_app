#! /usr/bin/python
from flask import Flask,request
import os
import sys
import subprocess
import json
import argparse
import io
import time

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/server', methods=['POST'])
def select_server():
	print request.data
	command = "curl -s http://%s/wm/device/?ipv4=%s" % (args.controllerRestIp, request.data)
	result = os.popen(command).read()
	parsedResult = json.loads(result)
	print command+"\n"
	choose_serverPort = parsedResult[0]['attachmentPoint'][0]['port']
	choose_serverMac = parsedResult[0]['mac'][0]

	command = "curl -X DELETE -d '{\"name\":\"%s\"}' http://%s/wm/staticflowentrypusher/json" % (args.servername+"_to", args.controllerRestIp)
	result = os.popen(command).read()
	print command+"\n"

	command = "curl -X DELETE -d '{\"name\":\"%s\"}' http://%s/wm/staticflowentrypusher/json" % (args.servername+"_from", args.controllerRestIp)
	result = os.popen(command).read()
	print command+"\n"

	command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"dst-mac\":\"%s\", \"ether-type\":\"%s\",\"dst-ip\":\"%s\", \"protocol\":\"%s\", \"dst-port\":\"%s\", \"priority\":\"32768\",\"active\":\"true\", \"actions\":\"set-dst-ip=%s,set-dst-mac=%s,output=%s\"}' http://%s/wm/staticflowentrypusher/json" % (Dpid, args.servername+"_to", origin_sourceMac, "0x800", args.server_ip, "6", "80", request.data, choose_serverMac, choose_serverPort, args.controllerRestIp)
	result = os.popen(command).read()
	print command+"\n"

	command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-mac\":\"%s\", \"ether-type\":\"%s\", \"src-ip\":\"%s\", \"protocol\":\"%s\", \"dst-port\":\"%s\", \"priority\":\"32768\",\"active\":\"true\", \"actions\":\"set-src-ip=%s,set-src-mac=%s,output=%s\"}' http://%s/wm/staticflowentrypusher/json" % (Dpid, args.servername+"_from", choose_serverMac, "0x800", request.data, "6", "80", args.server_ip, origin_sourceMac, sourcePort, args.controllerRestIp)
	result = os.popen(command).read()
	print command+"\n"

	command="curl -s http://%s/wm/core/switch/all/flow/json| python -mjson.tool" % (args.controllerRestIp)
	result = os.popen(command).read()
	print command + "\n" + result

	return "web traffic will redirect to"+request.data

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='web loadbalance')
	parser.add_argument('--controller', dest='controllerRestIp', action='store', default='localhost:8080', help='controller IP:RESTport, e.g., localhost:8080 or A.B.C.D:8080')
	parser.add_argument('--client_ip', dest='client_ip', action='store', default='192.168.71.220', help='client address: if type=ip, A.B.C.D')
	parser.add_argument('--original', dest='server_ip', action='store', default='192.168.71.221', help='server address: if type=ip, A.B.C.D')
	parser.add_argument('--name', dest='servername', action='store', default='server-1', help='name for server, e.g., server-1')
	args = parser.parse_args()
	print args
	command = "curl -s http://%s/wm/device/?ipv4=%s" % (args.controllerRestIp, args.client_ip)
	result = os.popen(command).read()
	parsedResult = json.loads(result)
	try:
		Dpid = parsedResult[0]['attachmentPoint'][0]['switchDPID']
		print "Switch_DPID is "+Dpid
	except IndexError:
		print "ERROR : the specified end point must already been known to the controller (i.e., already have sent packets on the network, easy way to assure this is to do a ping (to any target) from the two hosts." 
		sys.exit()
	sourcePort = parsedResult[0]['attachmentPoint'][0]['port']
	sourceMac = parsedResult[0]['mac'][0]
	print "Client's MAC is "+sourceMac+"attachmentPoint: "+str(sourcePort)

	command = "curl -s http://%s/wm/device/?ipv4=%s" % (args.controllerRestIp, args.server_ip)
	result = os.popen(command).read()
	parsedResult = json.loads(result)
	origin_sourceMac = parsedResult[0]['mac'][0]
	print "original server's MAC is "+origin_sourceMac
	app.run(host="0.0.0.0", debug=True)

