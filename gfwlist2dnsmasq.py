#!/usr/bin/env python  
#coding=utf-8
#  
# Generate a list of dnsmasq rules with ipset for gfwlist
#  
# Copyright (C) 2014 http://www.shuyz.com   
# Ref https://github.com/gfwlist/gfwlist   
 
import urllib2 
import re
import os
import datetime
import base64
import shutil
import sys

if len(sys.argv) <>5 and len(sys.argv) <> 3:
	print "usage:\n\tpython",sys.argv[0],"<ipset_name> <output_file_name> <dns_ip> <dns_port>"
	exit()
argc_is_5 = 0
if len(sys.argv) ==5 :
	mydnsip = sys.argv[3]
	mydnsport = sys.argv[4]
	argc_is_5 = 1 
ipsetname = sys.argv[1]
# Extra Domain;
EX_DOMAIN=[ \
'.google.com', \
'.google.com.hk', \
'.google.com.tw', \
'.google.com.sg', \
'.google.co.jp', \
'.blogspot.com', \
'.blogspot.sg', \
'.blogspot.hk', \
'.blogspot.jp', \
'.gvt1.com', \
'.gvt2.com', \
'.gvt3.com', \
'.1e100.net', \
'.blogspot.tw' \
]
 
# the url of gfwlist
baseurl = 'https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt'
# match comments/title/whitelist/ip address
comment_pattern = '^\!|\[|^@@|^\d+\.\d+\.\d+\.\d+'
domain_pattern = '([\w\-\_]+\.[\w\.\-\_]+)[\/\*]*' 
tmpfile = '/tmp/gfwlisttmp'
# do not write to router internal flash directly
outfile = sys.argv[2]
#outfile = './dnsmasq_list.conf'
 
fs =  file(outfile, 'w')
fs.write('# gfw list ipset rules for dnsmasq\n')
fs.write('# updated on ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\n')
fs.write('#\n')
 
print 'fetching list...'
content = urllib2.urlopen(baseurl, timeout=15).read().decode('base64')
 
# write the decoded content to file then read line by line
tfs = open(tmpfile, 'w')
tfs.write(content)
tfs.close()
tfs = open(tmpfile, 'r')
 
print 'page content fetched, analysis...'
 
# remember all blocked domains, in case of duplicate records
domainlist = []

 
for line in tfs.readlines():	
	if re.findall(comment_pattern, line):
		pass
		#print 'this is a comment line: ' + line
		#fs.write('#' + line)
	else:
		domain = re.findall(domain_pattern, line)
		if domain:
			try:
				found = domainlist.index(domain[0])
				print domain[0] + ' exists.'
			except ValueError:
				print 'saving ' + domain[0]
				domainlist.append(domain[0])
				if argc_is_5 :
					fs.write('server=/.%s/%s#%s\n'%(domain[0],mydnsip,mydnsport))
				fs.write('ipset=/.%s/%s\n'%(domain[0],ipsetname))
		else:
			print 'no valid domain in this line: ' + line
					
tfs.close()	

for each in EX_DOMAIN:
	if argc_is_5 :
		fs.write('server=/%s/%s#%s\n'%(each,mydnsip,mydnsport))
	fs.write('ipset=/%s/%s\n'%(each,ipsetname))

print 'write extra domain done'

fs.close();
 
print 'done!'