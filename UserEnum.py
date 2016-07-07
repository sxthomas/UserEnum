'''
WebApp UserEnum 1.0
Created: March 11, 2016
Author: Stephen Thomas

Description:
This tool makes multiple login attempts with a known bad username followed by multiple login attempts with a a list of usernames.  Some web applications check for the presence of a user account before checking the password.  This leads to a noticeable time delta between attempts with a good username verses a bad username.

This application is used to discover active user accounts, not passwords.  This application makes 10 requests per username.  It is possible to lock out accounts by using this tool.  Use at your own risk.

python userEnum.py -u http://www.website.com/login.php -d "user=administrator&pass=password" -p "user=administrator" -l userlist.txt -v
'''

import requests
import time
import getopt
import sys
import re

def main():
	timeDelta = 1.2     # delta between known wrong and response time. Default is 1.2
	knownBadUser= 'qqaazzwwssxx'     # Username used for known bad
	userList = []
	verbose = False
	payload = {}
	results = []
	possibleUsers = []
	
	print "UserEnum 1.0\n"
	urlGiven = False
	dataGiven = False
	paramGiven = False
	userListGiven = False
	try:
		options, args = getopt.getopt(sys.argv[1:], 'l:vd:hu:p:')
	except getopt.GetoptError as err:
		print str(err)
		sys.exit(2)
		
	for option, value in options:
		if option == '-h':
			usage()
			sys.exit(2)
		elif option == '-l':
			userListFile = value
			userListGiven = True
		elif option == '-v':
			verbose = True
		elif option == '-d':
			postData = value
			dataGiven = True
		elif option == '-u':
			url = value
			urlGiven = True
		elif option == '-p':
			postUser = value
			paramGiven = True
		else:
			print "command not recognized!!!"
	
	if urlGiven == False or dataGiven == False or paramGiven == False or userListGiven == False:
		print "[!] Missing required command line arguments. \n"
		usage()
		sys.exit(2)

	# open user list file and add to internal userList
	with open(userListFile, 'r') as userFile:
		for line in userFile:
			if '\n' in line:
				line=line[:-1]
			userList.append(line)

	
	# reformat all post data given
	postPairList = postData.split("&")
	for postPair in postPairList:
		payload[(postPair.split('=')[0])] = (postPair.split('=')[1])

	# get username param into vars
	postUserParam, postUserValue = postUser.split("=")
	
	print "Testing " + str(len(userList)) + " users\n"
	
	
	# send payload with bad username
	payload[postUserParam] = knownBadUser
	print "Testing known bad username"
	knownBadRun = True
	wrongAverageTime = MakeRequest(url, payload, verbose, knownBadRun)

	# make requests for users in user list
	knownBadRun = False
	for user in userList:
		print "Testing user: " + user
		payload[postUserParam] = user
		averageTime = MakeRequest(url, payload, verbose, knownBadRun)
		results.append((user,averageTime))
	
	# math to find longer login checks
	maxTime = wrongAverageTime * timeDelta
	for result in results:
		if result[1] > maxTime:
			possibleUsers.append(result[0])
			
	# print output
	if verbose == True:
		print "\nAverage wrong time: " + str(wrongAverageTime)
		print "Threshold is: "  + str(maxTime)
		print "Results list is:"
		print results
	
	if len(possibleUsers) == 0:
		print "\nNo given usernames are likely active for this application"
	else:
		print "\nThe following are possible users for this application:"
		for userName in possibleUsers:
			print userName
	
	
def MakeRequest(url, payload, verbose, knownBadRun):
	# setup the request to the server
	uas = {"User-agent": "Wget/1.12.1-dev Mar 04 2010 (mainline-013c8e2f5997) (Windows-MinGW)"}
	proxies = {}
	totalTime = 0
	if knownBadRun == True:
		rangeMax = 20
	else:
		rangeMax = 10
	for i in range(0,rangeMax):
		startTime = time.time()*1000
		webText=requests.post(url, headers = uas, proxies = proxies, data = payload)
		endTime = time.time()*1000
		runtime = endTime - startTime
		if verbose == True:
			print "Runtime is: " + str(runtime)
		# if testing the known bad username, test 20 times and only do stats on last 10. This cuts down on initial connection time deltas
		if knownBadRun == True:
			if i > 10:
				totalTime += runtime
		else:
			totalTime += runtime
	averageTime = totalTime / 10
	return(averageTime)

def usage():
	print 'UserEnum usage:'
	print '-u url'
	print '-d full post data'
	print '-p post param for username'
	print '-l user list text file (line separated)'
	print '-v verbose'
	print '-h this help message'
	print '\nExample:'
	print 'userEnum.py -u http://www.website.com/login.php -d "user=administrator&pass=password" -p "user=administrator" -l userlist.txt -v'


if __name__ == "__main__":
	main()
