#!c:\Python27-32\python.exe
import cgitb
import sys
import cgi

# Python CGI header.
cgitb.enable()

print "Content-type: text/plain"
print

#print "HEY!"

from scipy.cluster.vq import kmeans2, vq, kmeans
import numpy as np

form=cgi.FieldStorage()
keyword=form["term"].value.lower()

fp=open('data/%s.txt'%keyword,'r')

lines=fp.readlines()

sz=35	# Number of articles
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

#arr=np.array(vects)

#fr=open('debug.txt','w')	#

mx=0
for v in vects:
	mx=max(mx,len(v))

#fr.write(str(mx))	#
#fr.write('\n')		#
arr=[]
arr_num=[]
ctr=-1
for v in vects:
	s=" ".join([str(e) for e in v])
	ctr+=1
	if len(v)==mx:
		arr.append(v)
		arr_num.append(ctr)
	
	#fr.write(s)		#
	#fr.write('\n'+str(ctr)+'\n')	#
	

arr=np.array(arr)

#fr.write('\n')
#fr.write('\n')
#fr.write(str(len(arr_num)))
#fr.close()

minx=None

for grps in range(2,7):
	centroid, _ = kmeans(arr,grps)
	idx, ds = vq(arr,centroid)
	tot=0
	dst=ds.tolist()
	tot=sum(dst)
	if minx is None:
		minx=tot
		ming=grps
		idxF=idx
	else:
		if minx>tot:
			minx=tot
			idxF=idx
			ming=grps

print 'arr_num =', arr_num
print 'arr_cls =', idxF.tolist()
print 'grps =',ming
