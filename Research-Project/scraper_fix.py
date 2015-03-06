import urllib2
import sys
from bs4 import BeautifulSoup
import os
import hashlib

def _unicode(s):
	if type(s) is str:
		return s
	else:
		try:
			if type(s.encode('ascii','replace')) is str:
				return s.encode('ascii','replace')
		except:
			return ""
def _print(s):
	try:
		print s.encode('ascii','replace')
	except:
		try:
			print s
		except:
			print ""

proxy_support=urllib2.ProxyHandler({})							# No Proxy
opener=urllib2.build_opener(proxy_support)
urllib2.install_opener(opener)

# Get results from Yahoo! Voices.
if len(sys.argv) < 2:
	q = "terrorism"
else:
	q = " ".join(sys.argv[1:])

q = "+".join(q.split())
url = 'http://voices.yahoo.com/search.html?content_type=article&q='+q
print url


# Custom searces in BS
def f_res_list(tag):
	return tag.has_attr('class') and ('results_list' in tag['class'])
def f_title(tag):
	return tag.name=='a' and tag.has_attr('class') and ('title' in tag['class'])
def f_auth(tag):
	return tag.has_attr('class') and ('byline' in tag['class'])

try:
	response=urllib2.urlopen(url)
	msg=response.read()
except KeyError:
	sys.exit(1)
except:
	print("Not able to open Yahoo!")
	sys.exit(1)

soup=BeautifulSoup(msg)

# Extract all visible pages
res = soup.find(id="pagerRSBot")
urls = ['http://voices.yahoo.com/'+elem['value'] for elem in res.find_all("option")]

# Connection Problems
undone_urls = []
#urls = urls[28:]

ctr=0
# Scrape each page. Save the text.
dirname = 'data/'+q
if not os.path.exists(dirname):
	os.mkdir(dirname)
for url in urls:
	try:
		response=urllib2.urlopen(url)
		msg=response.read()
	except KeyError:
		sys.exit(1)
	except:
		print("Not able to open '%s'!"%url)
		continue
	
	soup=BeautifulSoup(msg)
	res = soup.find(f_res_list)

	for tag in res.children:
		print ctr
		ctr+=1
		
		title_a = tag.find_all(f_title)[-1]
		auth_a = tag.find(f_auth)
		print "="*80
		_print(title_a.string)
		t_url = 'http://voices.yahoo.com'+title_a['href']
		
		# Hashed to prevent duplicates.
		fname = dirname+'/'+hashlib.md5(t_url).hexdigest()
		if os.path.exists(fname+".title.txt"):
			fp = open(fname+".url.txt",'w')
			fp.write(_unicode(t_url))
			fp.close()

print undone_urls
#'''




















