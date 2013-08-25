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
print "Content-type: text/plain"
print

# The URL to access
url=form["url"].value
ctr=int(form["id"].value)
keyword=form["term"].value.lower()

import urllib2
from bs4 import BeautifulSoup
import re
import nltk

#proxy_support=urllib2.ProxyHandler({})							# No Proxy
proxy_support=urllib2.ProxyHandler({"ghoshs:nature89@bsnlproxy.iitk.ac.in":3128})
opener=urllib2.build_opener(proxy_support)
urllib2.install_opener(opener)

try:
	response=urllib2.urlopen(url)
except:
	print "Not able to open Yahoo!"
	sys.exit(1)

# Search the article for bias words.
msg=response.read()
soup=BeautifulSoup(msg)

art=soup.find(id='content_header')
data_t=soup.find(id='content_article')
data=data_t.get_text()
try:
	head=art.find('h2').string
except:
	head=art.find('h1').string
print head, '<br/>'

#terms = re.split(' ();."',head)
terms = nltk.word_tokenize(head)
#terms = head.split();

terms=set(terms)

#----------------SYNONYM/ANTONYM FREQUENCY COUNTER-----------------
bias=0

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

#----------------OFF-THE-SHELF SENTIMENT ANALYSIS TOOL-----------------
#- I'm using AlchemyAPI.                                              -
#----------------------------------------------------------------------
sentiment=0

sentences=""
for sentc in nltk.tokenize.sent_tokenize(data):
	if re.findall(keyword,sentc.lower()):
		sentences+=sentc+" "

#print sentences

from urllib import quote
sentences=sentences.replace('"','%22')
sentences=quote(sentences,'')
sentences=cgi.escape(sentences).strip()

try:
	url=r"http://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20htmlpost%20where%0Aurl%3D'http%3A%2F%2Faccess.alchemyapi.com%2Fcalls%2Ftext%2FTextGetTargetedSentiment'%20%0Aand%20postdata%3D%22apikey%3D5f40995d8dc06c85f02df93a5b370ec744590669%26text%3D"+sentences+r"%26target%3D"+keyword+r"%22%20and%20xpath%3D%22%2F%2Fp%22&diagnostics=true&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys"
	
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
if bword==0.0:
	bword=None

#----------------BIASED WORDS ACCORDING TO WIKIPEDIA-----------------
#- http://en.wikipedia.org/wiki/Wikipedia:Words_to_watch            -
#--------------------------------------------------------------------

# Unsupported
bias_wiki_words=['legendary','great', 'acclaimed', 'visionary', 'outstanding', 'leading', 'celebrated', 'landmark', 'cutting-edge', 'extraordinary', 'brilliant', 'famous', 'renowned', 'remarkable', 'prestigious', 'world-class', 'respected', 'notable', 'virtuoso', \
'cult', 'racist', 'perverted', 'sect', 'fundamentalist', 'heretic', 'extremist', 'denialist', 'terrorist', 'freedom fighter', 'bigot', 'myth', 'pseudo', 'gate', 'controversial', \
'some people say', 'many scholars state', 'it is believed','it is regarded', 'many are of the opinion', 'most feel', 'experts declare', 'it is often reported', 'it is widely thought', 'research has shown', 'science says', \
'supposed', 'apparent', 'purported', 'alleged', 'accused', 'so-called']

# Editorializing
bias_wiki_words2=['notably', 'interestingly', 'it should be noted', 'essentially', 'actually', 'clearly', 'without a doubt', 'of course', 'fortunately', 'happily', 'unfortunately', 'tragically', 'untimely', \
'reveal', 'point out', 'expose', 'explain', 'find', 'note', 'observe', 'insist', 'speculate', 'surmise', 'claim', 'assert', 'admit', 'confess', 'deny', \
'passed away', 'gave his life', 'make love', 'an issue with', 'collateral damage', 'ethnic cleansing', 'living with cancer', 'sightless', 'people with blindness']

wbword=0.0
wbword2=0.0
for w in bias_wiki_words:
	wbword+=len(re.findall(w,data))
for w in bias_wiki_words2:
        wbword2+=len(re.findall(w,data))

wbword/=len(nltk.word_tokenize(data))
wbword2/=len(nltk.word_tokenize(data))
if wbword==0.0:
	wbword=None
if wbword2==0.0:
        wbword=None


#----------------MULTI-FILE ANALYSIS-----------------



#----------------WRITE DATA TO FILE FOR NEXT STEP-----------------

fp=open('data/%s.txt'%keyword,'a')
fp.write('('+str(ctr)+","+str(bias)+')\n')
fp.close()
if bias is not None:
	print "Word Usage: %.2g" % bias
else: print sentiment
print '<br/>'

fp=open('data/%s.txt'%keyword,'a')
fp.write('('+str(ctr)+","+str(sentiment)+')\n')
fp.close()
if sentiment is not None:
		print "Sentiment: %.2g" % sentiment
else: print sentiment
print '<br/>'

fp=open('data/%s.txt'%keyword,'a')
fp.write('('+str(ctr)+","+str(bword)+')\n')
fp.close()
if bword is not None:
	print "Bigoted: %.2g" % bword
else: print sentiment
print '<br/>'

fp=open('data/%s.txt'%keyword,'a')
fp.write('('+str(ctr)+","+str(wbword)+')\n')
fp.close()
if wbword is not None:
	print "Non-neutral: %.2g" % wbword
else: print sentiment
print '<br/>'
