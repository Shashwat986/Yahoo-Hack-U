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

# Header for HTML Ends.

# If the number of categories is mentioned
if "cats" in form:
	try:
		# save the number of categories in `cat`
		nCats=int(form["cats"].value)
	except:
		isNCatsKnown=False
	else:
		isNCatsKnown=True
else:
	isNCatsKnown=False

# `isNCatsKnown` is True if the number of categories is specified. `isNCatsKnown` is false otherwise.
# If `isNCatsKnown` is True, `nCats` contains the number of categories


if "lim" in form:
	LIM = int(form["lim"].value)
else:
	LIM = 15


# Search string.
q=cgi.escape(form["q"].value.split()[0],True)

# Create a new file in the data/ folder.
fp=open('data/%s.txt' % q,'w')
fp.close()

# Header.
print '''<html>
<head>
<title>Yahoo! Voices - %s Search Results</title>
<script src="http://yui.yahooapis.com/3.11.0/build/yui/yui-min.js"></script>
<meta http-equiv="Content-type" content="text/html;charset=UTF-8">
''' % q

print '''
<style type="text/css">
.c0{
	background-color:#faac58;
}
.c1{
	background-color:#2efef7;
}
.c2{
	background-color:#f781f3;
}
.c3{
	background-color:#81f781;
}
.c4{
	background-color:#fa5858;
}
.c5{
	background-color:#f4fa58;
}
.uc{
	background-color:silver;
	color:grey;
}
</style>
'''

print '''
<script type="text/javascript">
var asyncCalls=0;
// Keeps track of the number of asynchronous calls made so that it can run the next stage of the script once they're all made
var iid;
var grps;
var arr_num;
var arr_cls;

// This function is called after all the asynchronous calls have started.
function alldone(){
	if(asyncCalls<=-500){
		// If the asynchronous calls have ended.
		// Just to make sure that the alldone() function isn't called needlessly
		document.getElementById('progress').innerHTML="Number of classes created: "+grps;
		clearInterval(iid);
	}
	
	else if(asyncCalls<=0){
		// If all calls have completed, call `done.py` with the category and search term information and display the result
		
		clearInterval(iid);
		asyncCalls=-1000;
		YUI().use('io','node',function(Y){
			var cfg = {
				on:{
					success:handleSuccess
				}
			}
			Y.io('done.py%s',cfg);	// AJAX call to `done.py`
			
			/*
				`done.py` returns values for the `grps`, `arr_num` and `arr_cls` variables.
				An eval() function is run in the handleSuccess function to store these values in the JavaScript variables.
			*/
			
			function handleSuccess(tid, resp){
				document.getElementById('progress').innerHTML=resp.responseText;
				// Take the response and display it. Debugging
				
				eval(resp.responseText);
				// `done.py` returns values for the `grps`, `arr_num` and `arr_cls` variables. eval stores these values
				
				// Sets all element classes as "uc"
				var i=arr_num;
				while(i>-1)
				{
					i--;
					if(document.getElementById("in"+i))
						document.getElementById("in"+i).className="uc";
				}
				
				// Colors the clustered elements correctly as "c1" to "c6"
				for(i=0;i<arr_num.length;i++){
					document.getElementById("in"+arr_num[i]).className="c"+arr_cls[i];
				}
				
				document.getElementById('progress').innerHTML="Number of classes created: "+grps;
				
				// Show the toggle button
				document.getElementById('toggleButton').style.display='inline';
				
				// Hide the Category View
				document.getElementById('categoryView').style.display='none';
				
				// Create and Show the Clustered View.
				var norde=Y.one('#clusteredView');
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
	else{
		// If the Asynchronous calls haven't ended.
		document.getElementById('progress').innerHTML="Please wait. Loading<br/>"+(%d-asyncCalls)+"/%d";
	}
}

// Toggles the view from Category View to Clustering View and vice-versa.
function toggleview()
{
	if(document.getElementById('categoryView').style.display == 'none')
		document.getElementById('categoryView').style.display='inline';
	else
		document.getElementById('categoryView').style.display='none';
	if(document.getElementById('clusteredView').style.display == 'none')
		document.getElementById('clusteredView').style.display='inline';
	else
		document.getElementById('clusteredView').style.display='none';
}
</script>
</head>
<body>
''' % ((("?cats="+str(nCats)+"&term="+q) if isNCatsKnown else "?term="+q), 2*LIM, 2*LIM)
# Passes the information required to `done.py`

print '<div id="progress">Please wait... Loading</div>'

print '''
<div id="toggleButton" style="display:none">
<input type="button" onclick="toggleview()" value="Toggle View" />
<br/>
</div>
'''

import urllib2
from bs4 import BeautifulSoup

proxy_support=urllib2.ProxyHandler({})							# No Proxy
#proxy_support=urllib2.ProxyHandler({"username:password@bsnlproxy.iitk.ac.in":3128})		# Proxy
opener=urllib2.build_opener(proxy_support)
urllib2.install_opener(opener)

# Get results from Yahoo! Voices.
q = "+".join(q.split())
#url = 'http://voices.yahoo.com/search.html?content_type=article&q='+q
url = 'http://voices.yahoo.com/subject/article/'+q

try:
	response=urllib2.urlopen(url)
	msg=response.read()
except:
	print "Not able to open Yahoo!"
	sys.exit(1)

soup=BeautifulSoup(msg)

# Custom searces in BS
def f_res_list(tag):
	return tag.has_attr('class') and ('results_list' in tag['class'])
def f_title(tag):
	return tag.name=='a' and tag.has_attr('class') and ('title' in tag['class'])
def f_auth(tag):
	return tag.has_attr('class') and ('byline' in tag['class'])

res = soup.find(f_res_list)

print '<table border="0" id="categoryView">\n'
ctr=0
for tag in res.children:
	ctr+=1
	if ctr>LIM:
		ctr=LIM
		break
	
	# Create a table element in Category View
	# The Title and link to article go here. ID = "in%" where % is the result number
	print '<tr><td id="in%d">'%ctr
	
	title_a = tag.find_all(f_title)[-1]								# The A element
	title_a['href']='http://voices.yahoo.com'+title_a['href']
	title_a['target']='_blank'
	title_link = title_a['href']									# The url to the page
	print title_a
	
	print '</td>'
	
	# The calculated results for each entry go here. ID = "do%" where % is the result number
	print '<td><div id="do%d">Loading...</div></td>'%ctr
	
	# Display the calculated author information for the article. ID = "doau%" where % is the result number
	auth_link = tag.find(f_auth).a['href']						# The url to the author's page
	auth_name=tag.find(f_auth).a.string
	print '<td><div id="doau%d">%s<br/>(...)</div></td>'%(ctr,auth_name)
	
	# Call the Asynchronous functions
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
			
			// Make AJAX call and increment the number of `asyncCalls`.
			Y.io('do.py?url=%s&id=%d&term=%s',cfg1);	// AJAX call to `do.py` with url, id and term information
			asyncCalls++;
			
			// Make AJAX call and increment the number of `asyncCalls`.
			Y.io('doauth.py?aurl=%s&aname=%s&id=%d&term=%s',cfg2);	// AJAX call to `doauth.py` with url, id, author-name and term information
			asyncCalls++;
			
			// If the AJAX call has completed, reduce asyncCalls, and display the required result.
			// The suffix T is for `do.py` and A is for `doauth.py`.
			function handleSuccessT(tid, resp){
				Y.one('#do%d').setHTML(resp.responseText);
				asyncCalls--;
			}
			function handleSuccessA(tid, resp){
				Y.one('#doau%d').setHTML(resp.responseText);
				asyncCalls--;
			}
		});
	</script>
	''' % (cgi.escape(title_link),ctr, q, \
		cgi.escape(auth_link),cgi.escape(auth_name),ctr, q, \
		ctr,ctr)
	
	print '</tr>'
	print

print '</table>'

print '''
<script type='text/javascript'>
	// Start making calls to alldone() to check if all AJAX calls have completed.
	iid = window.setInterval(alldone,500);
</script>
'''

# Create empty table that will be filled when all AJAX calls end. This will contain the Clustered View.
print '''
<table id="clusteredView">
</table>
'''

# Footer.
print '''
</body>
</html>
'''