###### COPYRIGHT NOTICE ########################################################
#
# Copyright (C) 2007-2012, Cycle Computing, LLC.
# 
# Licensed under the Apache License, Version 2.0 (the "License"); you
# may not use this file except in compliance with the License.  You may
# obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0.txt
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
################################################################################

################################################################################
# USAGE
################################################################################

# For detailed usage information please see README.md
#
#   cycle_submit.py --host=<hostname>:<port> <submission file>
#
# The cycle_submit tool allows you to push Condor jobs to a CycleServer
# meta-scheduler instance from the command line. It provides all the same
# features and capabilities of the Submit Job GUI in CycleServer from the
# command line, in a format that's easily integrated in to your scripts.
#
# It also serves as an example of how to use CycleServer's RESTful job
# submission API.


################################################################################
# IMPORTS
################################################################################

import urllib
import urllib2
import sys
import getpass
import os
from optparse import OptionParser
import xml.etree.ElementTree as ET

################################################################################
# GLOBALS
################################################################################

__version__ = '1.0'


################################################################################
# CLASSES
################################################################################



################################################################################
# METHODS
################################################################################

def lookup_http_response_code(code):
	'''
	Map a response code to a human-parsable response message. This list
	is and the mapping are from:

	http://www.voidspace.org.uk/python/articles/urllib2.shtml#error-codes

	Given an integer code returns a string describing it or 'Unknown' if
	the code cannot be found in the mapping.
	'''
	responses = {
		100: ('Continue', 'Request received, please continue'),
		101: ('Switching Protocols',
		'Switching to new protocol; obey Upgrade header'),

		200: ('OK', 'Request fulfilled, document follows'),
		201: ('Created', 'Document created, URL follows'),
		202: ('Accepted',
		'Request accepted, processing continues off-line'),
		203: ('Non-Authoritative Information', 'Request fulfilled from cache'),
		204: ('No Content', 'Request fulfilled, nothing follows'),
		205: ('Reset Content', 'Clear input form for further input.'),
		206: ('Partial Content', 'Partial content follows.'),

		300: ('Multiple Choices',
		'Object has several resources -- see URI list'),
		301: ('Moved Permanently', 'Object moved permanently -- see URI list'),
		302: ('Found', 'Object moved temporarily -- see URI list'),
		303: ('See Other', 'Object moved -- see Method and URL list'),
		304: ('Not Modified',
		'Document has not changed since given time'),
		305: ('Use Proxy',
		'You must use proxy specified in Location to access this '
		'resource.'),
		307: ('Temporary Redirect',
		'Object moved temporarily -- see URI list'),

		400: ('Bad Request',
		'Bad request syntax or unsupported method'),
		401: ('Unauthorized',
		'No permission -- see authorization schemes'),
		402: ('Payment Required',
		'No payment -- see charging schemes'),
		403: ('Forbidden',
		'Request forbidden -- authorization will not help'),
		404: ('Not Found', 'Nothing matches the given URI'),
		405: ('Method Not Allowed',
		'Specified method is invalid for this server.'),
		406: ('Not Acceptable', 'URI not available in preferred format.'),
		407: ('Proxy Authentication Required', 'You must authenticate with '
		'this proxy before proceeding.'),
		408: ('Request Timeout', 'Request timed out; try again later.'),
		409: ('Conflict', 'Request conflict.'),
		410: ('Gone',
		'URI no longer exists and has been permanently removed.'),
		411: ('Length Required', 'Client must specify Content-Length.'),
		412: ('Precondition Failed', 'Precondition in headers is false.'),
		413: ('Request Entity Too Large', 'Entity is too large.'),
		414: ('Request-URI Too Long', 'URI is too long.'),
		415: ('Unsupported Media Type', 'Entity body in unsupported format.'),
		416: ('Requested Range Not Satisfiable',
		'Cannot satisfy request range.'),
		417: ('Expectation Failed',
		'Expect condition could not be satisfied.'),

		500: ('Internal Server Error', 'Server got itself in trouble'),
		501: ('Not Implemented',
		'Server does not support this operation'),
		502: ('Bad Gateway', 'Invalid responses from another server/proxy.'),
		503: ('Service Unavailable',
		'The server cannot process the request due to a high load'),
		504: ('Gateway Timeout',
		'The gateway server did not receive a timely response'),
		505: ('HTTP Version Not Supported', 'Cannot fulfill request.'),
	}
	return str(code) + ' ' + ' - '.join(responses[code])

def get_target(hostname):
	'''
	Get the target pool for the submission by querying the CycleServer
	instance for a list of avialable targets and picking one. returns
	the pool ID to target the submission at.

	TODO Don't just pick the first one. If >1 pool ask the user to choose.
	'''
	target = None
	url = 'http://' + hostname + '/condor/submit/targets'
	try:
		pagehandle = urllib2.urlopen(url)
	except urllib2.HTTPError, e:
		print 'Error: The server could not fulfill the request'
		print 'Error: ' + lookup_http_response_code(e.code)
		target = None
	except urllib2.URLError, e:
		print 'Error: Failed to reach URL ' + url
		print 'Error: ' + lookup_http_response_code(e.code)
		target = None
	else:
		xmltree = ET.fromstring(pagehandle.read())
		for node in xmltree:
			target = node.attrib.get('poolId')
			if target:
				break
	return target

def read_submission_file(filename, description=None):
	'''
	Read the submission file in to a variable. Return the
	initialized variable.
	'''
	f = open(filename, 'r')
	subfile = f.read()
	f.close()
	if description:
		subfile = '+cycleSubmissionDescription = "' + description + '"\n\n' + subfile
	return subfile

def define_option_parser():
	'''
	Sets up a command line parser for this tool. Return the initialized parser.
	'''
	parser = OptionParser()
	parser.add_option('-d', '--description', dest='description', help='Optional description for submission')
	parser.add_option('-u', '--username', dest='username', help='Username for submission')
	parser.add_option('-p', '--password', dest='password', help='Password for submission')
	parser.add_option('-g', '--group', dest='group', help='Group name for submission')
	parser.add_option('--poolid', dest='poolid', help='Pool ID for the target pool')
	parser.add_option('--host', dest='hostname', default='localhost:8080', help='Host name or IP address of CycleServer instance')
	parser.add_option('-v', '--version', dest='version', default=False, action='store_true', help='Show version and exit')
	return parser

def submit_job(hostname, pool_id, username, group, submission_file):
	'''
	Actually do the submission to CycleServer. Report back an errors or success.
	'''
	submission_id = None

	headers = {
		'Content-Type' : 'text/plain',
		'Content-Encoding' : 'utf-8',
	}

	options = {
		'pool' : pool_id,
		'user' : username
	}
	if group:
		options['group'] = group

	url = 'http://' + hostname + '/condor/submit/submission?' + urllib.urlencode(options)
	#url = 'http://' + hostname + '/condor/submit/submit_file?' + urllib.urlencode(options)
	#print 'URL: '  + url

	req = urllib2.Request(url, submission_file, headers)
	try:
		response = urllib2.urlopen(req)
	except urllib2.HTTPError, e:
		print 'Error: The server could not fulfill the request'
		print 'Error: ' + lookup_http_response_code(e.code)
		subid = None
	except urllib2.URLError, e:
		print 'Error: Failed to reach URL ' + url
		print 'Error: ' + lookup_http_response_code(e.code)
		subid = None
	else:
		subid = response.read()
		# If subid is more than just an integer something went wrong with the submission
		# and we need to figure it out.
		try:
			int(subid)
		except ValueError:
			print 'Error: CycleServer rejected your submission'
			print 'Error: Possible causes for this failure include:'
			print 'Error: * A syntax error in your submission file'
			print 'Error: * You belong to multiple groups but no --group option was passed'
			print 'Error: * You passed a group that does not exist, remember: group names are case sensitive'
			subid = None
	return subid

def main():
	'''The main() routine that drives the script.'''
	parser = define_option_parser()
	(options, args) = parser.parse_args()

	if options.version:
		print '%s v%s' % (sys.argv[0], __version__)
		return 0

	# Require at least one argument to exist which is the name of the submission file
	if len(args) < 1:
		print 'Error: Missing requirement argument: submission file'
		return 1
	if not os.path.isfile(args[0]):
		print 'Error: Unable to find submission file: ' + args[0]
		return 1
	submission_file = args[0]

	if not options.username:
		username = None
		while not username:
			username = raw_input('Username: ')
	else:
		username = options.username

	if not options.password:
		password = None
		while not password:
			password = getpass.getpass('Password: ')
	else:
		password = options.password

	# Authentication details for this domain
	passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
	passman.add_password(None, 'http://'+ options.hostname, username, password)
	authhandler = urllib2.HTTPBasicAuthHandler(passman)
	opener = urllib2.build_opener(authhandler)
	urllib2.install_opener(opener)

	# Get the first pool from the list of pools
	if not options.poolid:
		pool_id = get_target(options.hostname)
	else:
		pool_id = options.poolid
	if not pool_id:
		print 'Error: Unable to find any pools registered to your CycleServer instance at ' + options.hostname
		return 1

	# Parse the submission file
	subfile_contents = read_submission_file(submission_file, description=options.description)
	#print subfile_contents

	# Print details about this submission...
	print 'Submission details:'
	#print '   Pool ID         : ' + pool_id
	print '   Username        : ' + username
	print '   Submission File : ' + args[0]
	if options.description:
		print '   Description     : ' + options.description

	# Do the submission
	subid = submit_job(options.hostname, pool_id, username, options.group, subfile_contents)
	if subid:
		print ''
		print 'Submission ' + subid + ' created successfully'
		retcode = 0
	else:
		print ''
		print 'Error: Unable to create submission'
		retcode = 1
	return retcode

if __name__ == '__main__':
    '''Run the main method if we are being called as a script.'''
    sys.exit(main())
