#!c:\Python27-32\python.exe
import cgitb
import sys
import cgi

# Python CGI header.
cgitb.enable()

form=cgi.FieldStorage()
if "url" not in form:
	print "Location: /voices.html"
	print
	sys.exit(0)
print "Content-type: text/html; charset=utf-8"
print

# The URL to access
url=form["url"].value
ctr=int(form["id"].value)
keyword=form["term"].value.lower()

import urllib2
from bs4 import BeautifulSoup
import re
import nltk

proxy_support=urllib2.ProxyHandler({})							# No Proxy
#proxy_support=urllib2.ProxyHandler({"username:password@bsnlproxy.iitk.ac.in":3128})	# Proxy
opener=urllib2.build_opener(proxy_support)
urllib2.install_opener(opener)

try:
	response=urllib2.urlopen(url)
except:
	print "Not able to open Yahoo!"
	sys.exit(1)

# PREPROCESSING
msg=response.read()
soup=BeautifulSoup(msg)

data_h=soup.find(id='content_header')
data_a=soup.find(id='c-ontent_article')
# `data` contains the text of the entire article
data=data_a.get_text()

# Display the title of the article
try:
	head=data_h.find('h2').string
except:
	head=data_h.find('h1').string
try:
	print '<i>'+ head + '</i><br/>'
except:
	print head.encode('utf-8');


#-------------------------COMMENT BIAS COUNTER-------------------------
#-    Look through the comment list and count the number of           -
#-        occourences of bias words as defined below.                 -
#-    Return this value divided by the number of comments made        -
#-        (if non-zero).                                              -
#----------------------------------------------------------------------

try:
	comments=soup.find(id="comment_list")
	
	num_comm=int(comments.find('h3').string.split()[0])
	comm=soup.find_all("p","content")
	commenttext=""
	
	# Merge all comments together.
	for c in comm:
		commenttext += c.string + " "
except:
	comm_bias=0.0
	num_comm=0.0
else:
	neg_biasedwords=['should','need','point','purpose','appropriate', \
		'horrible','wrong','incorrect','bad','immoral', \
		'dirty','unclean','repulsive','perverse','unnatural','heathen','infidel', \
		'duty','purpose','meaning','unfair','justice', \
		'guilty','deserve','cause','fault','responsible', \
		'insult','complaint','whine','accuse','blame', \
		'shame','decency','rude','impolite','freak','coward','selfish']
	
	comm_bias=0.0
	for w in neg_biasedwords:
		comm_bias+=len(re.findall(w,commenttext))
	
	if num_comm:
		comm_bias/=num_comm
	else:
		comm_bias=0.0

# Results:
#		comm_bias --> Number of biased words
#		num_comm  --> Number of comments
# On error, comm_bias = None

#----------------SYNONYM/ANTONYM FREQUENCY COUNTER-----------------

'''
bias=0

#terms = re.split(' ();."',head)
try:
	terms = nltk.word_tokenize(head)
except:
	
#terms = head.split();

terms=set(terms)
'''

'''
syn=[]
ant=[]
for term in terms:
	try:
		response=urllib2.urlopen(r"http://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20xml%20where%20url%3D'http%3A%2F%2Fwww.dictionaryapi.com%2Fapi%2Fv1%2Freferences%2Fthesaurus%2Fxml%2F"+term+r"%3Fkey%3D80424fa5-b982-413c-a445-f7bf2bf92552'&diagnostics=true&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys")
	except:
		continue
	msg=response.read()
	soup=BeautifulSoup(msg)
	
	for s in soup.find_all('syn'):
		if (s.string):
			for k in s.string.split(", "):
				if nltk.tag.pos_tag([k])[0][1] not in ['FW','NN','NNP','NNPS','NNS','POS','PRP','SYM','UH','WDT','WP','WP$','WRB']:
					syn.append(k)
	
	for s in soup.find_all('ant'):
		if s.string:
			for k in s.string.split(", "):
				if nltk.tag.pos_tag([k])[0][1] not in ['FW','NN','NNP','NNPS','NNS','POS','PRP','SYM','UH','WDT','WP','WP$','WRB']:
					ant.append(k)

ctr_syn=0.0
ctr_ant=0.0
for w in syn:
	ctr_syn += len(re.findall(w,data))
if len(syn)!=0:
	ctr_syn/=len(syn)
else:
	bias=None
for w in ant:
	ctr_ant += len(re.findall(w,data))
if len(ant)!=0:
	ctr_ant/=len(ant)
else:
	bias=None

if bias is not None:
	bias = (ctr_syn - ctr_ant)/len(nltk.word_tokenize(data))
'''

#----------------OFF-THE-SHELF SENTIMENT ANALYSIS TOOL-----------------
#- I'm using AlchemyAPI.                                              -
#- Current API-KEY:   5f40995d8dc06c85f02df93a5b370ec744590669        -
#- Alternate API-KEY: 364dff5755880f9d141b88b7c67c5281e848ff65        -
#----------------------------------------------------------------------
API_KEY = r"5f40995d8dc06c85f02df93a5b370ec744590669"

sentiment=0

sentences=""
for sentc in nltk.tokenize.sent_tokenize(data):
	if re.findall(keyword,sentc.lower()):
		sentences+=sentc+" "


# Escape the punctuation in the sentences so that it can be sent to the YQL url.
# Sometimes prone to problems.
from urllib import quote
sentences=sentences.replace('"','%22')
sentences=quote(sentences,'')
sentences=cgi.escape(sentences).strip()

# Use YQL to call the Alchemy API.
try:
	url=r"http://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20htmlpost%20where%0Aurl%3D'http%3A%2F%2Faccess.alchemyapi.com%2Fcalls%2Ftext%2FTextGetTargetedSentiment'%20%0Aand%20postdata%3D%22apikey%3D"+API_KEY+"%26text%3D"+sentences+r"%26target%3D"+keyword+r"%22%20and%20xpath%3D%22%2F%2Fp%22&diagnostics=true&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys"
	
	response = urllib2.urlopen(url)

except urllib2.URLError, e:
	print e.reason
	sentiment=None
else:
	try:
		msg=response.read()
		soup=BeautifulSoup(msg)
		a=soup.find('p').string.split('english ')[1].split()[1]
		sentiment=float(a.strip())
	except:
		strr= soup.find('p').string
		if strr.find('neutral'):
			sentiment=0
		else:
			print str
			sentiment=None

# Results:
#		sentiment --> Result returned by Alchemy. Ranges from -1 to +1. 0 = Neutral.
# On error, sentiment = None

#----------------BIASED WORDS ACCORDING TO Alex Rohde-----------------
#- The correct way would be to look for common words in articles     -
#- classified as biased, but that's more than a one-day-hack         -
#---------------------------------------------------------------------

biasedwords=['should','need','point','purpose','appropriate', \
	'right','wrong','good','bad','moral','immoral','honor','honorable', \
	'dirty','unclean','repulsive','perverse','unnatural','heathen','infidel', \
	'duty','purpose','meaning','fair','unfair','just','justify','justice', \
	'guilty','innocent','deserve','cause','fault','responsible','earn', \
	'insult','complaint','compliment','whine','accuse','blame','sorry','apologize', \
	'worth','value','shame','decency','rude','polite','freak','brave','coward','selfish']

bword=0.0
for w in biasedwords:
	bword+=len(re.findall(w,data))

bword/=len(nltk.word_tokenize(data))

# Results:
#		bword --> Number of biased words in article.
# On error, bword = None

#----------------BIASED WORDS ACCORDING TO WIKIPEDIA-----------------
#- http://en.wikipedia.org/wiki/Wikipedia:Words_to_watch            -
#--------------------------------------------------------------------

bias_wiki_words=['legendary','great', 'acclaimed', 'visionary', 'outstanding', 'leading', 'celebrated', 'landmark', 'cutting-edge', 'extraordinary', 'brilliant', 'famous', 'renowned', 'remarkable', 'prestigious', 'world-class', 'respected', 'notable', 'virtuoso', \
'cult', 'racist', 'perverted', 'sect', 'fundamentalist', 'heretic', 'extremist', 'denialist', 'terrorist', 'freedom fighter', 'bigot', 'myth', 'pseudo', 'gate', 'controversial', \
'some people say', 'many scholars state', 'it is believed','it is regarded', 'many are of the opinion', 'most feel', 'experts declare', 'it is often reported', 'it is widely thought', 'research has shown', 'science says', \
'supposed', 'apparent', 'purported', 'alleged', 'accused', 'so-called', \
'notably', 'interestingly', 'it should be noted', 'essentially', 'actually', 'clearly', 'without a doubt', 'of course', 'fortunately', 'happily', 'unfortunately', 'tragically', 'untimely', \
'reveal', 'point out', 'expose', 'explain', 'find', 'note', 'observe', 'insist', 'speculate', 'surmise', 'claim', 'assert', 'admit', 'confess', 'deny', \
'passed away', 'gave his life', 'make love', 'an issue with', 'collateral damage', 'ethnic cleansing', 'living with cancer', 'sightless', 'people with blindness']

wbword=0.0
for w in bias_wiki_words:
	wbword+=len(re.findall(w,data))

wbword/=len(nltk.word_tokenize(data))

# Results:
#		wbword --> Number of non-neutral words in article.
# On error, wbword = None


#----------------BI-, TRI-GRAM ANALYSIS-----------------



#-------------------WRITE DATA TO FILE FOR NEXT STEP-------------------
#-    This section of the code writes all the information gathered    -
#-        into the file created in `voice_res.py`.                    -
#-    This information is used by `done.py` when it is called.        -
#-                                                                    -
#-    This section also displays the calculated values so that they   -
#-        can be shown on `voice_res.py` when the AJAX call completes -
#----------------------------------------------------------------------

'''
fp=open('data/%s.txt'%keyword,'a')
fp.write('('+str(ctr)+","+str(bias)+')\n')
fp.close()
if bias is not None:
	print "Word Usage: %.2g" % bias
else: print sentiment
print '<br/>'
'''

# Comment Bias
fp=open('data/%s.txt'%keyword,'a')
fp.write('('+str(ctr)+","+str(comm_bias)+')\n')
fp.close()
if comm_bias is not None:
	print "Comment Bias: %.2g" % comm_bias , '(%d Comments)'%num_comm
else:
	print comm_bias
print '<br/>'

# Sentiment Analysis
fp=open('data/%s.txt'%keyword,'a')
fp.write('('+str(ctr)+","+str(sentiment)+')\n')
fp.close()
if sentiment is not None:
		print "Sentiment: %.2g" % sentiment
else:
	print sentiment
print '<br/>'

# Bigoted Word analysis
fp=open('data/%s.txt'%keyword,'a')
fp.write('('+str(ctr)+","+str(bword)+')\n')
fp.close()
if bword is not None:
	print "Bigoted: %.2g" % bword
else:
	print bword
print '<br/>'

# Non-Neutral Word analysis.
fp=open('data/%s.txt'%keyword,'a')
fp.write('('+str(ctr)+","+str(wbword)+')\n')
fp.close()
if wbword is not None:
	print "Non-neutral: %.2g" % wbword
else:
	print wbword
print '<br/>'
