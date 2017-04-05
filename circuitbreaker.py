from flask import jsonify
import requests
import sqlite3
import redis
import json

import os
import sys

import boto.sqs
from boto.sqs.message import Message

########################################
# INITIALIZE REDIS OBJECTS
#####################################

TOLERANCE_THRESHOLD = 20
PASS_CODES={200}
FAIL_CODES={500}
IGNORE_CODES={}

redisDB = redis.Redis('localhost')


if not (redisDB.exists("circuitStatus")):
	redisDB.set("circuitStatus",1)

if not (redisDB.exists("failedReq")):
	redisDB.set("failedReq",0)

if not (redisDB.exists("successReq")):
	redisDB.set("successReq",0)

###########################







###################

def postReq(*args,**kwargs):


	if int(redisDB.get("circuitStatus"))==1:
		print "CIRCUIT IS LIVE"
		servResp = requests.post(*args,**kwargs)
		code = servResp.status_code


		if code in FAIL_CODES:

			print "KWARGS ABOVE"
			# new_request = processQueue(url="esting",parameters={'tries':{'yep':'123'}},tries=0,reqType="POST")

			#push to queue	

		isLive = updateStatus(code)
		if not isLive:
			print ""
			restore()

		return servResp

	else:
		print "CIRCUIT NOT LIVE"
		return requests.post("http://127.0.0.1:5000/serviceDown",**kwargs) ### post req to be replaced with live queue implementation for scaling





def getReq(*args,**kwargs):

	if int(redisDB.get("circuitStatus"))==1:
	 	print "CIRCUIT IS LIVE"
		servResp = requests.get(*args,**kwargs)
		code = servResp.status_code
		if code in FAIL_CODES:
			# print kwargs['headers']
			#print json.dumps(kwargs['data'])
			testing = kwargs
			print testing

			print "KWARGS ABOVE"
			#push to queue

		isLive = updateStatus(code)
		if not isLive:
			print ""
			restore()

		return servResp

	else:
		print "CIRCUIT NOT LIVE"
		return requests.post("http://127.0.0.1:5000/serviceDown",**kwargs)


def trip():
	print "Ooops I tripped"
	redisDB.set("circuitStatus",0)
	redisDB.set("failedReq",0)
	redisDB.set("successReq",0)
	return 0

def updateStatus(result):

	if (result== 400 or result==500):
		redisDB.incr("failedReq")
	elif (result==200):
		redisDB.incr("successReq")


	successRate=100*(int(redisDB.get("successReq"))/(int(redisDB.get("successReq"))+int(redisDB.get("failedReq"))))


	if successRate > TOLERANCE_THRESHOLD:
		return 1

	else:
		return trip()


def restore():
	#execute qFail
	#check for status
	print "Restoring"
	redisDB.set("circuitStatus",1)
	return



