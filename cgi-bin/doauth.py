#!c:\Python27-32\python.exe
import cgitb
import sys
import cgi

# Python CGI header.
cgitb.enable()

form=cgi.FieldStorage()
if "aurl" not in form or "aname" not in form:
	print "Location: /voices.html"
	print
	sys.exit(0)
print "Content-type: text/plain"
print

# PREPROCESSING
# The URL to access
a_url=form["aurl"].value
a_name=form["aname"].value
ctr=int(form["id"].value)
keyword=form["term"].value.lower()

import urllib2
from bs4 import BeautifulSoup

proxy_support=urllib2.ProxyHandler({})							# No Proxy
#proxy_support=urllib2.ProxyHandler({"username:password@bsnlproxy.iitk.ac.in":3128})	#Proxy
opener=urllib2.build_opener(proxy_support)
urllib2.install_opener(opener)

# Display the author name
print a_name
print '<br/>'

#------------------------FEATURED ARTICLE COUNT------------------------
feat_count=0

# Using the YQL API to get information about the article author.
try:
	response=urllib2.urlopen(r'http://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20yahoovoices.featuredarticles%20where%20query%3D%22'+a_url+r'%22&diagnostics=true&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys')
except:
	print "Not able to open Yahoo!"
	sys.exit(1)

# Parse YQL's result
msg=response.read()
soup=BeautifulSoup(msg)

data_a=soup.find('count')
feat_count = int(data_a.string)

# Results:
#		feat_count --> Number of featured articles
# On error, feat_count = None


#----------------NUMBER OF COMMENTS ON RECENT ARTICLES-----------------
'''
comments=0.0

try:
	response=urllib2.urlopen(r'http://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20yahoovoices.recentarticles%20where%20query%3D%22'+aurl+r'%22&diagnostics=true&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys')
except:
	print "Not able to open Yahoo!"
	sys.exit(1)

# Parse YQL's result
msg=response.read()
soup=BeautifulSoup(msg)

links=soup.find_all('link',limit=5)				# limit to recent 5
numrec=len(links)


for link in links:
	try:
		response=urllib2.urlopen(link.string)
	except:
		continue
	msg=response.read()
	soup=BeautifulSoup(msg)
	try:
		comm=soup.find(id="comment_list")
		comments+=int(comm.find('h3').string.split()[0])
	except:
		numrec-=1
		continue

if numrec>0:
	comments/=numrec
else:
	comments=-1

'''


#-------------------WRITE DATA TO FILE FOR NEXT STEP-------------------
#-    This section of the code writes all the information gathered    -
#-        into the file created in `voice_res.py`.                    -
#-    This information is used by `done.py` when it is called.        -
#-                                                                    -
#-    This section also displays the calculated values so that they   -
#-        can be shown on `voice_res.py` when the AJAX call completes -
#----------------------------------------------------------------------

# Featured Article Count
fp=open('data/%s.txt'%keyword,'a')
fp.write('('+str(ctr)+","+str(feat_count)+')\n')
fp.close()
if feat_count is not None:
	print '('+str(feat_count)+' featured)'
else:
	print feat_count
print '<br/>'

'''
fp=open('data/%s.txt'%keyword,'a')
fp.write('('+str(ctr)+","+str(comments)+')\n')
fp.close()
print '('+str(comments)+' comments/article)'
print '<br/>'
'''