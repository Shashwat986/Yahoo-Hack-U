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

# The URL to access
aurl=form["aurl"].value
au=form["aname"].value
ctr=int(form["id"].value)
keyword=form["term"].value.lower()

import urllib2
from bs4 import BeautifulSoup

#proxy_support=urllib2.ProxyHandler({})							# No Proxy
proxy_support=urllib2.ProxyHandler({"ghoshs:nature89@bsnlproxy.iitk.ac.in":3128})
opener=urllib2.build_opener(proxy_support)
urllib2.install_opener(opener)

print au
print '<br/>'

#----------------FEATURED ARTICLE COUNT-----------------
feat_count=0

try:
	response=urllib2.urlopen(r'http://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20yahoovoices.featuredarticles%20where%20query%3D%22'+aurl+r'%22&diagnostics=true&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys')
except:
	print "Not able to open Yahoo!"
	sys.exit(1)

# Parse YQL's result
msg=response.read()
soup=BeautifulSoup(msg)

art=soup.find('count')
feat_count = int(art.string)

#----------------NUMBER OF COMMENTS ON RECENT ARTICLES-----------------
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




#----------------SAVING-----------------
fp=open('data/%s.txt'%keyword,'a')
fp.write('('+str(ctr)+","+str(feat_count)+')\n')
fp.close()
print '('+str(feat_count)+' featured)'
print '<br/>'

fp=open('data/%s.txt'%keyword,'a')
fp.write('('+str(ctr)+","+str(comments)+')\n')
fp.close()
print '('+str(comments)+' comments/article)'
print '<br/>'