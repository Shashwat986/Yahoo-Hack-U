#!c:\Python27-32\python.exe
import cgitb
import sys
import cgi

# Python CGI header.
cgitb.enable()

form=cgi.FieldStorage()
if "q" not in form:
	print "Location: /voices.html"
	print
	sys.exit(0)
print "Content-type: text/html"
print

if "cats" in form:
	try:
		cat=int(form["cats"].value)
	except:
		catss=False
	else:
		catss=True
else:
	catss=False

if "lim" in form:
	LIM = int(form["lim"].value)
else:
	LIM = 15


# Search string.
q=cgi.escape(form["q"].value,True)
fp=open('data/%s.txt' % q,'w')
fp.close()
print '''<html>
<head>
<title>Yahoo! Voices - %s Search Results</title>
<script src="http://yui.yahooapis.com/3.11.0/build/yui/yui-min.js"></script>
<meta http-equiv="Content-type" content="text/html;charset=UTF-8">
''' % q

print '''
<style type="text/css">
.c0{
	background-color:#ff6633;
}
.c1{
	background-color:#ff99ff;
}
.c2{
	background-color:#33ffff;
}
.c3{
	background-color:ff3333;
}
.c4{
	background-color:66ccff;
}
.c5{
	background-color:ffff00;
}
.uc{
	background-color:silver;
	color:grey;
}
</style>
'''

print '''
<script type="text/javascript">
var async_calls=0;
var iid;
var grps;
var arr_num;
var arr_cls;
function alldone(){
	if(async_calls==0){
		clearInterval(iid);
		async_calls=-1000;
		YUI().use('io','node',function(Y){
			var cfg = {
				on:{
					success:handleSuccess
				}
			}
			Y.io('done.py%s',cfg);
			function handleSuccess(tid, resp){
				document.getElementById('ldgf').innerHTML=resp.responseText;
				eval(resp.responseText);
				var i=0;
				while(i>-1)
				{
					if(document.getElementById("in"+i))
						document.getElementById("in"+i).className="uc";
					else
						break;
				}
				for(i=0;i<arr_num.length;i++){
					document.getElementById("in"+arr_num[i]).className="c"+arr_cls[i];
				}
				document.getElementById('ldgf').innerHTML="Number of classes created: "+grps;
				document.getElementById('show').style.display='inline';
				
				
				//document.getElementById('ldg').innerHTML="Done...";
				document.getElementById('tab').style.display='none';
				
				var norde=Y.one('#cattab');
				var groups=[];
				for(i=0;i<grps;i++)
				{
					groups.push(norde.appendChild("<tr></tr>"));
				}
				for(i=0;i<arr_num.length;i++)
				{
					t0=groups[arr_cls[i]].appendChild("<table></table>");
					t=t0.appendChild("<tr></tr>");
					t0.append("<br/>");
					t.setHTML(document.getElementById("in"+arr_num[i]).innerHTML);
					t.addClass("c"+arr_cls[i]);
				}
			}
		});
	}
	else
		document.getElementById('ldg').innerHTML=(%d-async_calls)+"/%d";
	if(async_calls==-1000)
		document.getElementById('ldg').innerHTML="";
}

function toggleview()
{
	if(document.getElementById('tab').style.display == 'none')
		document.getElementById('tab').style.display='inline';
	else
		document.getElementById('tab').style.display='none';
	if(document.getElementById('cattab').style.display == 'none')
		document.getElementById('cattab').style.display='inline';
	else
		document.getElementById('cattab').style.display='none';
}
</script>
</head>
<body>
''' % ((("?cats="+str(cat)+"&term="+q) if catss else "?term="+q), LIM, LIM)

print '<div id="ldg">Please wait... Loading</div><div id="ldgf"></div>'

print '''
<div id="show" style="display:none">
<input type="button" onclick="toggleview()" value="Toggle View" />
<br/>
</div>
'''
import urllib2
from bs4 import BeautifulSoup

#proxy_support=urllib2.ProxyHandler({})							# No Proxy
proxy_support=urllib2.ProxyHandler({"ghoshs:nature89@bsnlproxy.iitk.ac.in":3128})
opener=urllib2.build_opener(proxy_support)
urllib2.install_opener(opener)

# Get results from Yahoo! Voices.
url = 'http://voices.yahoo.com/search.html?content_type=article&q='+q

try:
	response=urllib2.urlopen(url)
except:
	print "Not able to open Yahoo!"
	sys.exit(1)

msg=response.read()
soup=BeautifulSoup(msg)

# Custom searces in BS
def f_res_list(tag):
	return tag.has_attr('class') and ('results_list' in tag['class'])
def f_title(tag):
	return tag.name=='a' and tag.has_attr('class') and ('title' in tag['class'])
def f_auth(tag):
	return tag.has_attr('class') and ('byline' in tag['class'])

res = soup.find(f_res_list)

print '<table border="0" id="tab">\n'
ctr=0
for tag in res.children:
	ctr+=1
	if ctr>LIM:
		ctr=LIM
		break
	print '<tr><td id="in%d">'%ctr
	#print tag.prettify()
	title_a = tag.find(f_title)									# The A element
	title_a['href']='http://voices.yahoo.com'+title_a['href']
	title_a['target']='_blank'
	print title_a
	auth_link = tag.find(f_auth).a['href']						# The url to the author's page
	au=tag.find(f_auth).a.string
	title_link = title_a['href']									# The url to the page
	print '</td>'
	
	print '<td><div id="do%d">Loading...</div></td>'%ctr
	print '<td><div id="doau%d">%s<br/>(...)</div></td>'%(ctr,au)
	print '''
	<script type='text/javascript'>
		YUI().use('io','node',function(Y){
			var cfg1 = {
				on:{
					success:handleSuccessT
				}
			}
			var cfg2 = {
				on:{
					success:handleSuccessA
				}
			}
			Y.io('do.py?url=%s&id=%d&term=%s',cfg1);
			async_calls++;
			Y.io('doauth.py?aurl=%s&aname=%s&id=%d&term=%s',cfg2);
			async_calls++;
			iid = window.setInterval(alldone,500);
			
			function handleSuccessT(tid, resp){
				Y.one('#do%d').setHTML(resp.responseText);
				async_calls--;
			}
			function handleSuccessA(tid, resp){
				Y.one('#doau%d').setHTML(resp.responseText);
				async_calls--;
			}
		});
	</script>
	''' % (cgi.escape(title_link),ctr, q, \
		cgi.escape(auth_link),cgi.escape(au),ctr, q, \
		ctr,ctr)
	print '</tr>'
	print

print '</table>'

print '''
<table id="cattab">
</table>
'''

print '''
</body>
</html>'''