#!c:\Python27-32\python.exe
import cgitb
import sys
import cgi

# Python CGI header.
cgitb.enable()

print "Content-type: text/plain"
print

# Using scipy to perform K-Means on the results
from scipy.cluster.vq import kmeans2, vq, kmeans
import numpy as np

form=cgi.FieldStorage()
keyword=form["term"].value.lower()

# This file has been written into by both the data-collection modules: `do.py` and `doauth.py`.
fp=open('data/%s.txt'%keyword,'r')

# Extract the information from the file and store it in `vects`
lines=fp.readlines()

sz=35	# Maximum number of articles
vects=[0]*sz

for i in xrange(sz):
	vects[i]=[]

for line in lines:
	try:
		i=int(line.split('(')[1].split(',')[0])
		j=float(line.split(',')[1].split(')')[0])
	except:
		continue
	vects[i].append(j)

# Get the maximum number of variables calculated for an article. Only articles with this number of variables shall be clustered.
mx=0
for v in vects:
	mx=max(mx,len(v))

paramMatrix=[]	# The matrix with all paramaters for all articles
arr_num=[]		# The article numbers.
ctr=-1
for v in vects:
	s=" ".join([str(e) for e in v])
	ctr+=1
	if len(v)==mx:
		paramMatrix.append(v)
		arr_num.append(ctr)
	

paramMatrix=np.array(paramMatrix)

# `minx` stores the minimum error based on the number of clusters made.
minx=None

if "cats" in form:
	# If the number of clusters has been mentioned, those many clusters are created.
	numClusters=int(form["cats"].value)
	centroid, _ = kmeans(paramMatrix,numClusters)
	idxF, ds = vq(paramMatrix,centroid)
else:
	for grps in range(2,7):
		# All clusters from 2 to 6 (inclusive) are tried.
		centroid, _ = kmeans(paramMatrix,grps)
		idx, ds = vq(paramMatrix,centroid)
		tot=0
		dst=ds.tolist()
		tot=sum(dst)
		if minx is None:
			minx=tot
			numClusters=grps
			idxF=idx
		else:
			if minx>tot:
				minx=tot
				idxF=idx
				numClusters=grps
# `idxF` stores the final clustering for each article.

# This section returns values that can be understood and evaluated by JavaScript for use in `voice_res.py`
print 'arr_num =', arr_num
print 'arr_cls =', idxF.tolist()
print 'grps =', numClusters